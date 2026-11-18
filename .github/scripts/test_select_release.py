import base64
from copy import deepcopy
from functools import partial
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import select_release as gate
import refresh_release as refresh


BASE = "1" * 40
HEAD = "2" * 40
OLD_HEAD = "3" * 40
BRANCH = "release/trails-0.3.0"
REPO = gate.REPOSITORY
NUMBER = 44
PATH = "Formula/trails.rb"
TREE = "f" * 40
PLATFORMS = ("darwin-arm64", "darwin-x64", "linux-arm64", "linux-x64")
DIGEST = "a" * 64
ALLOWLIST = frozenset({"outfitter-dev/trails"})
SUPPORT = gate.load_support(gate.SUPPORT_PATH)


def formula(tag, project="trails"):
    return gate.render_formula(project, tag, {p: DIGEST for p in SUPPORT[project]["formula_archive"]})


class EligibilityTests(unittest.TestCase):
    def setUp(self):
        self.project = "trails"
        self.path = PATH
        self.pr = {
            "number": NUMBER, "state": "open", "draft": True, "user": {"login": "release-author"},
            "base": {"ref": "main", "sha": BASE},
            "head": {"sha": HEAD, "ref": BRANCH, "repo": {"full_name": REPO}},
        }
        self.release = {
            "tag_name": "v0.3.0", "draft": False, "prerelease": False, "published_at": "2026-11-18T13:00:00Z",
            "assets": [{"name": f"trails-v0.3.0-{p}.tar.gz", "state": "uploaded",
                        "digest": f"sha256:{DIGEST}"} for p in PLATFORMS],
        }
        self.commit = {"parents": [{"sha": BASE}], "files": [{"filename": PATH, "status": "modified"}],
                       "commit": {"tree": {"sha": TREE}}}
        self.tree = {"truncated": False, "tree": [{"path": PATH, "type": "blob", "mode": "100644"}]}
        self.run_info = {
            "id": 4321, "event": "pull_request", "head_sha": HEAD, "head_repository": {"full_name": REPO},
            "pull_requests": [{"number": NUMBER}], "status": "completed", "conclusion": "success",
        }
        self.artifacts = [{"name": f"bottles_{runner}", "expired": False, "size_in_bytes": 100}
                          for runner in ("macos-26", "ubuntu-latest", "ubuntu-24.04-arm")]
        self.runs = {"tests.yml": [self.run_info], "formula-landing-policy.yml": [deepcopy(self.run_info)]}
        self.review = {
            "state": "APPROVED", "authorCanPushToRepository": True,
            "author": {"__typename": "User", "login": "maintainer"}, "commit": {"oid": HEAD},
        }
        self.review_state = {
            "state": "OPEN", "isDraft": True, "headRefOid": HEAD, "baseRefOid": BASE,
            "mergeStateStatus": "CLEAN", "reviewDecision": None,
            "reviewThreads": {"pageInfo": {"hasNextPage": False}, "nodes": []},
            "latestOpinionatedReviews": {"pageInfo": {"hasNextPage": False}, "nodes": [self.review]},
        }
        self.proposed = formula("v0.3.0")
        self.current = formula("v0.2.3")
        api = patch.object(gate, "api", side_effect=self.github_api)
        self.api = api.start()
        self.addCleanup(api.stop)

    def github_api(self, *args):
        endpoint = args[-1]
        if args[0] == "graphql":
            return {"data": {"repository": {"pullRequest": self.review_state}}}
        if "/actions/workflows/" in endpoint:
            workflow = re.search(r"/workflows/(.+?)/runs\?", endpoint)[1]
            return [{"workflow_runs": self.runs[workflow]}]
        if endpoint == f"repos/{REPO}/actions/runs/4321/artifacts?per_page=100":
            return [{"artifacts": self.artifacts}]
        if endpoint == f"repos/{REPO}/commits/{HEAD}?per_page=100":
            return self.commit
        if endpoint == f"repos/{REPO}/git/trees/{TREE}?recursive=1":
            return self.tree
        if endpoint == f"repos/outfitter-dev/{self.project}/releases/latest":
            return self.release
        if endpoint in (f"repos/{REPO}/contents/{self.path}?ref={BASE}", f"repos/{REPO}/contents/{self.path}?ref={HEAD}"):
            data = self.current if endpoint.endswith(BASE) else self.proposed
            return {"type": "file", "encoding": "base64", "content": base64.b64encode(data.encode())}
        self.fail(f"Unexpected GitHub API call: {args}")

    def assert_ineligible(self, reason, **kwargs):
        with self.assertRaisesRegex(gate.NotEligible, reason):
            gate.eligible(self.pr, BASE, ALLOWLIST, SUPPORT, **kwargs)

    def test_verified_release_and_exact_approved_head(self):
        allowlist = gate.load_allowlist(gate.ALLOWLIST_PATH)
        self.assertEqual(gate.eligible(self.pr, BASE, allowlist, SUPPORT), (NUMBER, HEAD))
        self.assertEqual(gate.eligible(self.pr, BASE, allowlist, SUPPORT, expected_head=HEAD), (NUMBER, HEAD))

    def test_skillset_requires_a_verified_release_and_both_mac_bottles(self):
        self.project = "skillset"
        self.path = "Formula/skillset.rb"
        self.pr["head"]["ref"] = "release/skillset"
        self.commit["files"] = [{"filename": self.path, "status": "modified"}]
        self.tree["tree"][0]["path"] = self.path
        platforms = ("darwin-arm64", "darwin-x64")
        tag = "v0.30.0"
        self.current = formula("v0.29.0", self.project)
        self.proposed = formula(tag, self.project)
        self.release["tag_name"] = tag
        self.release["assets"] = [
            {"name": f"skillset-{tag}-{platform}.tar.gz", "state": "uploaded", "digest": f"sha256:{DIGEST}"}
            for platform in platforms
        ]
        self.artifacts = [{"name": f"bottles_{runner}", "expired": False, "size_in_bytes": 100}
                          for runner in ("macos-26", "macos-15-intel")]
        allowlist = gate.load_allowlist(gate.ALLOWLIST_PATH)
        self.assertEqual(gate.eligible(self.pr, BASE, allowlist, SUPPORT), (NUMBER, HEAD))
        self.assertEqual(gate.eligible(self.pr, BASE, allowlist, SUPPORT, expected_head=HEAD), (NUMBER, HEAD))
        self.artifacts.pop()
        with self.assertRaisesRegex(gate.NotEligible, "missing unexpired bottle artifacts"):
            gate.eligible(self.pr, BASE, allowlist, SUPPORT)

    def test_unlisted_upstream_is_denied_before_inspecting_a_release(self):
        self.pr["head"]["ref"] = "release/skillset"
        self.assert_ineligible("outfitter-dev/skillset is not allowed")
        self.api.assert_not_called()

    def test_recheck_rejects_a_replaced_head(self):
        self.assert_ineligible("selected head", expected_head=OLD_HEAD)

    def test_ignores_fork_and_non_draft(self):
        self.pr["head"]["repo"]["full_name"] = "example/homebrew-tap"
        self.assert_ineligible("same-tap draft")
        self.pr["head"]["repo"]["full_name"] = REPO
        self.pr["draft"] = False
        self.assert_ineligible("same-tap draft")

    def test_rejects_stale_base_and_unrelated_changes(self):
        self.commit["parents"] = [{"sha": OLD_HEAD}]
        self.assert_ineligible("directly on current main")
        self.commit["parents"] = [{"sha": BASE}]
        self.commit["files"].append({"filename": ".github/workflows/tests.yml", "status": "modified"})
        self.assert_ineligible("Only the expected release formula")

    def test_failure_on_latest_run_cannot_fall_back_to_older_success(self):
        self.runs["tests.yml"].insert(0, {**self.run_info, "conclusion": "failure"})
        self.assert_ineligible("Latest tests.yml run")

    def test_checks_must_belong_to_this_pr_and_head(self):
        self.runs["tests.yml"][0]["head_sha"] = OLD_HEAD
        self.assert_ineligible("Latest tests.yml run")
        self.runs["tests.yml"][0]["head_sha"] = HEAD
        self.runs["tests.yml"][0]["pull_requests"] = [{"number": NUMBER + 1}]
        self.assert_ineligible("Latest tests.yml run")

    def test_policy_workflow_must_also_succeed(self):
        self.runs["formula-landing-policy.yml"] = []
        self.assert_ineligible("Latest formula-landing-policy.yml run")

    def test_expired_bottles_do_not_qualify(self):
        self.artifacts[1]["expired"] = True
        self.assert_ineligible("missing unexpired bottle artifacts")

    def test_review_requires_a_maintainer_and_the_exact_head(self):
        self.review["commit"]["oid"] = OLD_HEAD
        self.assert_ineligible("approval of the exact head")
        self.review["commit"]["oid"] = HEAD
        self.review["authorCanPushToRepository"] = False
        self.assert_ineligible("approval of the exact head")
        self.review["authorCanPushToRepository"] = True
        self.review["state"] = "DISMISSED"
        self.assert_ineligible("approval of the exact head")

    def test_unresolved_threads_and_github_review_requirements_block(self):
        self.review_state["reviewThreads"]["nodes"] = [{"isResolved": False}]
        self.assert_ineligible("Review threads")
        self.review_state["reviewThreads"]["nodes"] = []
        self.review_state["reviewDecision"] = "REVIEW_REQUIRED"
        self.assert_ineligible("required reviews")

    def test_approved_head_still_blocks_if_changes_requested(self):
        blocker = deepcopy(self.review)
        blocker["author"]["login"] = "another-maintainer"
        blocker["state"] = "CHANGES_REQUESTED"
        self.review_state["latestOpinionatedReviews"]["nodes"].append(blocker)
        self.assert_ineligible("outstanding changes requested")

    def test_stale_approval_does_not_veto_a_current_approval(self):
        stale = deepcopy(self.review)
        stale["author"]["login"] = "another-maintainer"
        stale["commit"]["oid"] = OLD_HEAD
        self.review_state["latestOpinionatedReviews"]["nodes"].append(stale)
        self.assertEqual(gate.eligible(self.pr, BASE, ALLOWLIST, SUPPORT), (NUMBER, HEAD))

    def test_preview_or_missing_assets_do_not_qualify(self):
        self.release["prerelease"] = True
        self.assert_ineligible("eligible stable release")
        self.release["prerelease"] = False
        self.release["assets"].pop()
        self.assert_ineligible("asset or SHA-256 digest is missing")

    def test_trails_still_requires_the_intel_archive(self):
        self.release["assets"] = [asset for asset in self.release["assets"] if "darwin-x64" not in asset["name"]]
        self.assert_ineligible("missing or ambiguous for darwin-x64")

    def test_skillset_requires_both_mac_bottles(self):
        self.artifacts = [{"name": "bottles_macos-26", "expired": False, "size_in_bytes": 100}]
        with self.assertRaisesRegex(gate.NotEligible, "bottles_macos-15-intel"):
            gate.verify_runs(NUMBER, HEAD, BRANCH, SUPPORT["skillset"]["homebrew_bottle"])
        self.artifacts.append({"name": "bottles_macos-15-intel", "expired": False, "size_in_bytes": 100})
        gate.verify_runs(NUMBER, HEAD, BRANCH, SUPPORT["skillset"]["homebrew_bottle"])

    def test_only_explicit_unsupported_bottle_can_skip(self):
        policy = json.loads(gate.SUPPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(gate.eligible(self.pr, BASE, ALLOWLIST, SUPPORT), (NUMBER, HEAD))
        policy["trails"]["homebrew_bottle"]["darwin-x64"] = "supported"
        with TemporaryDirectory() as directory:
            path = Path(directory) / "support.json"
            path.write_text(json.dumps(policy), encoding="utf-8")
            support = gate.load_support(path)
        with self.assertRaisesRegex(gate.NotEligible, "bottles_macos-15-intel"):
            gate.eligible(self.pr, BASE, ALLOWLIST, support)
        for artifact in self.artifacts:
            with self.subTest(artifact=artifact["name"]):
                artifact["expired"] = True
                self.assert_ineligible("missing unexpired bottle artifacts")
                artifact["expired"] = False

    def test_matching_sources_do_not_authorize_arbitrary_formula_code(self):
        self.proposed = self.proposed.replace('  depends_on "bun"', '  depends_on "curl"')
        self.assert_ineligible("Full formula must match")

    def test_rejects_a_formula_symlink(self):
        self.tree["tree"][0]["mode"] = "120000"
        self.assert_ineligible("Expected a regular formula file")

    def test_mismatched_hash_and_already_published_version_do_not_qualify(self):
        self.proposed = self.proposed.replace(DIGEST, "b" * 64, 1)
        self.assert_ineligible("Full formula must match")
        self.proposed = formula("v0.3.0")
        self.current = self.proposed
        self.assert_ineligible("must advance the current formula")

    def plan_stale_refresh(self, **kwargs):
        self.commit["parents"] = [{"sha": OLD_HEAD}]
        self.pr["base"]["sha"] = OLD_HEAD
        self.review_state["baseRefOid"] = OLD_HEAD
        self.review_state["mergeStateStatus"] = "BEHIND"
        with patch.object(refresh.subprocess, "run") as ancestor, patch.object(refresh, "git") as git:
            ancestor.return_value.returncode = kwargs.pop("ancestor_status", 0)
            git.side_effect = kwargs.pop("formula_blobs", ("same", "same"))
            return refresh.refresh_candidate(self.pr, BASE, ALLOWLIST, SUPPORT, **kwargs)

    def test_refresh_freshens_an_authorized_stale_draft_without_using_old_ci(self):
        self.runs["tests.yml"] = []
        draft, expected = self.plan_stale_refresh(expected_head=HEAD)
        self.assertEqual((draft.head, draft.parent, expected), (HEAD, OLD_HEAD, self.proposed))
        self.assertFalse(any("/actions/" in str(call) for call in self.api.call_args_list))

    def test_refresh_denies_unapproved_otherwise_canonical_candidate(self):
        self.review["author"]["login"] = self.pr["user"]["login"]
        with self.assertRaisesRegex(gate.NotEligible, "approval of the exact head"):
            self.plan_stale_refresh()

    def test_refresh_denies_unresolved_reviews_or_changed_review_head(self):
        self.review_state["reviewThreads"]["nodes"] = [{"isResolved": False}]
        with self.assertRaisesRegex(gate.NotEligible, "Review threads"):
            self.plan_stale_refresh()
        self.review_state["reviewThreads"]["nodes"] = []
        self.review_state["headRefOid"] = OLD_HEAD
        with self.assertRaisesRegex(gate.NotEligible, "required reviews"):
            self.plan_stale_refresh()

    def test_refresh_denies_a_nonancestor_and_published_formula_drift(self):
        with self.assertRaisesRegex(gate.NotEligible, "not in current main history"):
            self.plan_stale_refresh(ancestor_status=1)
        with self.assertRaisesRegex(gate.NotEligible, "published formula changed"):
            self.plan_stale_refresh(formula_blobs=("old", "new"))

    def test_refresh_denies_stale_draft_that_no_longer_matches_the_verified_release(self):
        self.release["assets"][0]["digest"] = f"sha256:{'b' * 64}"
        with self.assertRaisesRegex(gate.NotEligible, "Full formula must match"):
            self.plan_stale_refresh()

    def test_apply_refresh_refetches_pr_before_pushing_and_requires_current_main(self):
        first = self.plan_stale_refresh()
        second = self.plan_stale_refresh()
        with patch.object(refresh, "refresh_candidate", side_effect=[first, second, first, second]) as candidate, \
             patch.object(gate, "api", return_value=self.pr) as api, \
             patch.object(gate, "current_main", side_effect=[OLD_HEAD, BASE]), \
             patch.object(refresh, "build_commit", return_value="7" * 40), \
             patch.object(refresh, "push_commit") as push:
            with self.assertRaisesRegex(gate.NotEligible, "main moved"):
                refresh.apply_refresh(NUMBER, HEAD, BASE, ALLOWLIST, SUPPORT)
            push.assert_not_called()
            refresh.apply_refresh(NUMBER, HEAD, BASE, ALLOWLIST, SUPPORT)
        self.assertEqual(candidate.call_count, 4)
        self.assertEqual(api.call_count, 4)
        push.assert_called_once()


class RefreshGitTests(unittest.TestCase):
    def test_refresh_updates_only_the_formula_and_cannot_overwrite_a_newer_draft(self):
        with TemporaryDirectory() as directory:
            repo = Path(directory) / "work"
            remote = Path(directory) / "remote.git"
            repo.mkdir()
            git = partial(refresh.git, cwd=repo, stderr=subprocess.STDOUT)
            git("init", "--bare", "--initial-branch=main", str(remote))
            git("init", "--initial-branch=main")
            commit = partial(git, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit")
            (repo / "Formula").mkdir()
            (repo / PATH).write_text("old formula\n", encoding="utf-8")
            (repo / "README.md").write_text("old docs\n", encoding="utf-8")
            git("add", ".")
            commit("-m", "old main")
            old_base = git("rev-parse", "HEAD")
            git("switch", "-c", BRANCH)
            formula_update = "generated formula\n"
            (repo / PATH).write_text(formula_update, encoding="utf-8")
            commit("-am", "old draft")
            head = git("rev-parse", "HEAD")
            git("switch", "main")
            (repo / "README.md").write_text("fresh docs\n", encoding="utf-8")
            commit("-am", "unrelated main change")
            base = git("rev-parse", "HEAD")
            git("push", str(remote), "main", BRANCH)

            draft = gate.Draft(NUMBER, head, BRANCH, "author", "trails", "0.3.0", old_base, old_base)
            with patch.object(refresh, "git", side_effect=git):
                refreshed = refresh.build_commit(base, draft, formula_update)
                refresh.push_commit(draft, refreshed, str(remote))
                with self.assertRaisesRegex(subprocess.CalledProcessError, "force-with-lease"):
                    refresh.push_commit(draft, head, str(remote))
            self.assertEqual(git("rev-list", "--parents", "-1", refreshed), f"{refreshed} {base}")
            self.assertEqual(git("diff", "--name-only", base, refreshed), PATH)
            self.assertEqual(git("show", f"{refreshed}:{PATH}"), formula_update.strip())
            self.assertEqual(git("ls-remote", str(remote), f"refs/heads/{BRANCH}").split()[0], refreshed)
            self.assertEqual(git("ls-remote", str(remote), "refs/heads/main").split()[0], base)
            self.assertEqual(git("status", "--porcelain"), "")


class SupportTests(unittest.TestCase):
    def test_missing_unknown_or_invalid_target_fails_closed(self):
        policy = json.loads(gate.SUPPORT_PATH.read_text(encoding="utf-8"))
        trails = policy["trails"]["homebrew_bottle"]
        for change in ({}, {"darwin-x64": "unknown"}, {"darwin-s390x": "unsupported"}, {"darwin-x64": False}):
            with self.subTest(change=change), TemporaryDirectory() as directory:
                path = Path(directory) / "support.json"
                policy["trails"]["homebrew_bottle"] = {k: v for k, v in trails.items() if k != "darwin-x64"} | change
                path.write_text(json.dumps(policy), encoding="utf-8")
                with self.assertRaisesRegex(gate.NotEligible, "Install support is unknown"):
                    gate.load_support(path)

    def test_duplicate_key_cannot_override_supported_status(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "support.json"
            path.write_text('{"trails": {}, "trails": {}}', encoding="utf-8")
            with self.assertRaisesRegex(gate.NotEligible, "valid install-support"):
                gate.load_support(path)


class AllowlistTests(unittest.TestCase):
    def test_checked_in_allowlist_contains_only_the_two_reviewed_upstreams(self):
        self.assertEqual(gate.load_allowlist(gate.ALLOWLIST_PATH),
                         frozenset({"outfitter-dev/skillset", "outfitter-dev/trails"}))

    def test_empty_allowlist_disables_all_upstreams(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "autopublish.yaml"
            path.write_text("[]", encoding="utf-8")
            self.assertEqual(gate.load_allowlist(path), frozenset())

    def test_missing_or_invalid_allowlist_cannot_select_or_recheck(self):
        for config in (None, "[", "{}", '["outfitter-dev/trails", true]',
                       '["outfitter-dev/trails", "outfitter-dev/unknown"]',
                       '["outfitter-dev/trails", "outfitter-dev/trails"]'):
            for args in (["selector"], ["selector", str(NUMBER), HEAD]):
                with self.subTest(config=config, args=args), TemporaryDirectory() as directory:
                    path = Path(directory) / "autopublish.yaml"
                    output = Path(directory) / "output"
                    if config is not None:
                        path.write_text(config, encoding="utf-8")
                    env = {"GITHUB_REPOSITORY": REPO, "GITHUB_REF": "refs/heads/main",
                           "GITHUB_SHA": BASE, "GITHUB_OUTPUT": str(output)}
                    with patch.dict(os.environ, env), patch.object(sys, "argv", args), \
                         patch.object(gate, "ALLOWLIST_PATH", path), \
                         patch.object(gate, "api", return_value={"object": {"sha": BASE}}) as api:
                        with self.assertRaisesRegex(SystemExit, "autopublish.yaml"):
                            gate.main()
                    api.assert_called_once_with(f"repos/{REPO}/git/ref/heads/main")
                    self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
