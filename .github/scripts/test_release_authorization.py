from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import select_release as gate

PROJECT = "skillset"
UPSTREAM = f"outfitter-dev/{PROJECT}"
ROOT = f"repos/{UPSTREAM}"
TAG = "v0.30.0"
COMMIT = "1" * 40
DIGEST = "a" * 64
ARCHIVE = f"{PROJECT}-{TAG}-darwin-arm64.tar.gz"
MANIFEST = f"{PROJECT}-{TAG}-manifest.json"
RUN_ID = 42
RUN_ENDPOINT = f"{ROOT}/actions/runs/{RUN_ID}"


class UpstreamAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.policy = gate.load_authorization(PROJECT)
        repo = {"id": self.policy["repository_id"]}
        self.release = {"tag_name": TAG, "published_at": "2026-10-26T14:38:10Z",
                        "assets": [{"name": MANIFEST, "state": "uploaded", "size": 100}]}
        self.ref = {"object": {"type": "commit", "sha": COMMIT}}
        self.manifest = {"version": TAG[1:], "commit": COMMIT,
                         "artifacts": [{"archive": ARCHIVE, "sha256": DIGEST}]}
        self.certificate = {"sourceRepositoryIdentifier": str(repo["id"]), "buildTrigger": "push",
                            "runInvocationURI": f"https://github.com/{UPSTREAM}/actions/runs/{RUN_ID}/attempts/1"}
        self.attestation = {"verificationResult": {"signature": {"certificate": self.certificate},
                                                   "statement": {"predicate": {}}}}
        self.run = {
            "id": RUN_ID, "workflow_id": self.policy["workflow_id"], "path": ".github/workflows/release.yml",
            "head_branch": "main", "head_sha": COMMIT, "repository": repo, "head_repository": repo,
            "event": "push", "run_attempt": 1, "status": "completed", "conclusion": "success",
            "actor": {"id": 1}, "triggering_actor": {"id": 1},
        }
        self.approver = {"type": "User", "id": self.policy["approver_ids"][0]}
        self.review = {"user": self.approver, "state": "approved",
                       "environments": [{"name": self.policy["approval_environment"]}]}
        self.approvals = [self.review]
        job = {"run_id": RUN_ID, "head_sha": COMMIT, "status": "completed", "conclusion": "success"}
        self.jobs = [
            {**job, "name": self.policy["approval_job"], "completed_at": "2026-10-26T14:35:00Z"},
            {**job, "name": self.policy["publication_job"], "started_at": "2026-10-26T14:36:00Z",
             "completed_at": "2026-10-26T14:39:00Z"},
        ]
        self.responses = {
            f"{ROOT}/git/ref/tags/{TAG}": self.ref,
            RUN_ENDPOINT: self.run,
            f"{RUN_ENDPOINT}/approvals": self.approvals,
            f"{RUN_ENDPOINT}/attempts/1/jobs?per_page=100": [{"jobs": self.jobs}],
        }
        mock_api = patch.object(gate, "api", side_effect=lambda *a: self.responses[a[-1]])
        verify = patch.object(gate, "verified_manifest", return_value=(self.manifest, [self.attestation]))
        self.mock_api = mock_api.start()
        self.verify = verify.start()
        self.addCleanup(mock_api.stop)
        self.addCleanup(verify.stop)

    def authorize(self, project=PROJECT, digests=None):
        gate.verify_upstream_authorization(project, self.release, {ARCHIVE: DIGEST} if digests is None else digests)

    def test_attested_assets_from_the_independently_approved_run_pass(self):
        self.authorize()
        self.verify.assert_called_once_with(UPSTREAM, TAG, COMMIT, self.release["assets"][0])

    def test_trails_has_no_automatic_policy(self):
        with self.assertRaisesRegex(gate.NotEligible, "trails has no automatic upstream authorization policy"):
            self.authorize(project="trails")
        self.mock_api.assert_not_called()

    def test_missing_or_unreadable_policy_fails_closed(self):
        with TemporaryDirectory() as directory, patch.object(gate, "AUTHORIZATION_PATH", Path(directory) / "missing"):
            with self.assertRaisesRegex(gate.NotEligible, "Cannot verify upstream authorization"):
                self.authorize()
        self.mock_api.assert_not_called()

    def test_missing_manifest_or_changed_tag_does_not_initialize_verification(self):
        self.ref["object"]["type"] = "tag"
        with self.assertRaisesRegex(gate.NotEligible, "exact commit"):
            self.authorize()
        self.ref["object"]["type"] = "commit"
        self.release["assets"].append(deepcopy(self.release["assets"][0]))
        with self.assertRaisesRegex(gate.NotEligible, "unambiguous upstream authorization manifest"):
            self.authorize()
        self.verify.assert_not_called()

    def test_failed_attestation_verification_blocks_before_looking_up_approval(self):
        self.verify.side_effect = subprocess.CalledProcessError(1, ["gh"])
        with self.assertRaisesRegex(gate.NotEligible, "Cannot verify upstream authorization"):
            self.authorize()
        self.mock_api.assert_called_once_with(f"{ROOT}/git/ref/tags/{TAG}")

    def test_reused_manifest_or_asset_changes_fail_closed(self):
        self.manifest["commit"] = "2" * 40
        with self.assertRaisesRegex(gate.NotEligible, "not for this tag and source commit"):
            self.authorize()
        self.manifest["commit"] = COMMIT
        for digests in ({ARCHIVE: "b" * 64}, {"unlisted.tar.gz": DIGEST}):
            with self.subTest(digests=digests), self.assertRaisesRegex(gate.NotEligible, "does not authorize"):
                self.authorize(digests=digests)

    def test_unsigned_invocation_or_rerun_cannot_supply_authority(self):
        original = self.certificate["runInvocationURI"]
        self.certificate["runInvocationURI"] = original.removesuffix("/1") + "/2"
        self.attestation["verificationResult"]["statement"] = {"predicate": {"runDetails": {
            "metadata": {"invocationId": original}
        }}}
        with self.assertRaisesRegex(gate.NotEligible, "workflow identity"):
            self.authorize()
        self.certificate["runInvocationURI"] = original
        self.run["run_attempt"] = 2
        with self.assertRaisesRegex(gate.NotEligible, "not a successful release of the exact source"):
            self.authorize()

    def test_wrong_workflow_or_source_commit_fails_closed(self):
        for key in ("workflow_id", "head_sha", "head_branch", "event"):
            original = self.run[key]
            self.run[key] = "wrong"
            with self.subTest(key=key), self.assertRaisesRegex(gate.NotEligible, "exact source"):
                self.authorize()
            self.run[key] = original

    def test_approval_must_be_independent_and_apply_to_this_run_and_environment(self):
        original_environments = self.review["environments"]
        self.review["environments"] = [{"name": "unrelated"}]
        with self.assertRaisesRegex(gate.NotEligible, "No independent upstream approval"):
            self.authorize()
        self.review["environments"] = original_environments
        self.run["actor"] = self.approver
        with self.assertRaisesRegex(gate.NotEligible, "No independent upstream approval"):
            self.authorize()
        self.run["actor"] = {"id": 1}
        self.approvals.append({**self.review, "state": "rejected"})
        with self.assertRaisesRegex(gate.NotEligible, "No independent upstream approval"):
            self.authorize()
        self.approvals.clear()
        with self.assertRaisesRegex(gate.NotEligible, "No independent upstream approval"):
            self.authorize()

    def test_approval_and_publication_jobs_must_succeed_in_order_for_this_release(self):
        self.jobs[0]["conclusion"] = "skipped"
        with self.assertRaisesRegex(gate.NotEligible, "did not pass its approval job"):
            self.authorize()
        self.jobs[0]["conclusion"] = "success"
        self.release["published_at"] = "2026-10-26T14:40:00Z"
        with self.assertRaisesRegex(gate.NotEligible, "not published by the independently approved run"):
            self.authorize()


class VerifiedManifestTests(unittest.TestCase):
    def test_verifies_only_digest_matched_manifest_with_exact_signer_and_source(self):
        content = b'{"test": 1}'
        asset = {"name": MANIFEST, "size": len(content), "digest": f"sha256:{sha256(content).hexdigest()}"}

        def download(args, **kwargs):
            Path(args[-1]).write_bytes(content)

        with patch.object(gate.subprocess, "run", side_effect=download) as fetch, \
             patch.object(gate.subprocess, "check_output", return_value=json.dumps([{}])) as attest:
            self.assertEqual(gate.verified_manifest(UPSTREAM, TAG, COMMIT, asset), ({"test": 1}, [{}]))
            self.assertEqual(fetch.call_args.args[0][:6], ["gh", "release", "download", TAG, "--repo", UPSTREAM])
            self.assertEqual(attest.call_args.args[0][4:], [
                "--repo", UPSTREAM, "--cert-identity",
                f"https://github.com/{UPSTREAM}/.github/workflows/release.yml@refs/heads/main",
                "--source-ref", "refs/heads/main", "--source-digest", COMMIT, "--deny-self-hosted-runners",
                "--format", "json",
            ])
            attest.reset_mock()
            with self.assertRaisesRegex(gate.NotEligible, "digest changed"):
                gate.verified_manifest(UPSTREAM, TAG, COMMIT, {**asset, "digest": f"sha256:{DIGEST}"})
            attest.assert_not_called()
