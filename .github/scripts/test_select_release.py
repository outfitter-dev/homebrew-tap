import base64
from copy import deepcopy
import re
import unittest
from unittest.mock import patch

import select_release as gate


BASE = "1" * 40
HEAD = "2" * 40
OLD_HEAD = "3" * 40
BRANCH = "release/trails-0.3.0"
REPO = gate.REPOSITORY
NUMBER = 44
PATH = "Formula/trails.rb"
PLATFORMS = ("darwin-arm64", "darwin-x64", "linux-arm64", "linux-x64")
DIGEST = "a" * 64


def formula(tag):
    return "".join(
        f'    url "https://github.com/outfitter-dev/trails/releases/download/{tag}/trails-{tag}-{p}.tar.gz"\n'
        f'    sha256 "{DIGEST}"\n' for p in PLATFORMS
    )


class EligibilityTests(unittest.TestCase):
    def setUp(self):
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
        self.commit = {"parents": [{"sha": BASE}], "files": [{"filename": PATH, "status": "modified"}]}
        self.run_info = {
            "event": "pull_request", "head_sha": HEAD, "head_repository": {"full_name": REPO},
            "pull_requests": [{"number": NUMBER}], "status": "completed", "conclusion": "success",
        }
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
        api.start()
        self.addCleanup(api.stop)

    def github_api(self, *args):
        endpoint = args[-1]
        if args[0] == "graphql":
            return {"data": {"repository": {"pullRequest": self.review_state}}}
        if "/actions/workflows/" in endpoint:
            workflow = re.search(r"/workflows/(.+?)/runs\?", endpoint)[1]
            return [{"workflow_runs": self.runs[workflow]}]
        if endpoint == f"repos/{REPO}/commits/{HEAD}?per_page=100":
            return self.commit
        if endpoint == "repos/outfitter-dev/trails/releases/latest":
            return self.release
        if endpoint in (f"repos/{REPO}/contents/{PATH}?ref={BASE}", f"repos/{REPO}/contents/{PATH}?ref={HEAD}"):
            data = self.current if endpoint.endswith(BASE) else self.proposed
            return {"type": "file", "encoding": "base64", "content": base64.b64encode(data.encode())}
        self.fail(f"Unexpected GitHub API call: {args}")

    def assert_ineligible(self, reason, **kwargs):
        with self.assertRaisesRegex(gate.NotEligible, reason):
            gate.eligible(self.pr, BASE, **kwargs)

    def test_verified_release_and_exact_approved_head(self):
        self.assertEqual(gate.eligible(self.pr, BASE), (NUMBER, HEAD))
        self.assertEqual(gate.eligible(self.pr, BASE, expected_head=HEAD), (NUMBER, HEAD))

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
        self.assert_ineligible("Only the expected release files")

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

    def test_preview_or_missing_assets_do_not_qualify(self):
        self.release["prerelease"] = True
        self.assert_ineligible("eligible stable release")
        self.release["prerelease"] = False
        self.release["assets"].pop()
        self.assert_ineligible("asset or SHA-256 digest is missing")

    def test_mismatched_hash_and_already_published_version_do_not_qualify(self):
        self.proposed = self.proposed.replace(DIGEST, "b" * 64, 1)
        self.assert_ineligible("checksums must match")
        self.proposed = formula("v0.3.0")
        self.current = self.proposed
        self.assert_ineligible("must advance the current formula")


if __name__ == "__main__":
    unittest.main()
