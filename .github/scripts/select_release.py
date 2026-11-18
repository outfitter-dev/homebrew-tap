"""Read-only eligibility gate for automatic brew pr-pull."""

import base64
import json
import os
import re
import subprocess
import sys
from urllib.parse import urlencode


REPOSITORY = "outfitter-dev/homebrew-tap"
VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
SHA = r"[0-9a-f]{40}"
BRANCHES = {
    "trails": rf"release/trails-(?P<version>{VERSION})",
    "skillset": r"release/skillset",
}
PLATFORMS = {
    "trails": ("darwin-arm64", "darwin-x64", "linux-arm64", "linux-x64"),
    "skillset": ("darwin-arm64", "darwin-x64"),
}

PR_REVIEW_QUERY = """
query($number: Int!) {
  repository(owner: "outfitter-dev", name: "homebrew-tap") {
    pullRequest(number: $number) {
      state isDraft headRefOid baseRefOid mergeStateStatus reviewDecision
      reviewThreads(first: 100) {
        pageInfo { hasNextPage }
        nodes { isResolved }
      }
      latestOpinionatedReviews(first: 100) {
        pageInfo { hasNextPage }
        nodes { state authorCanPushToRepository author { __typename login } commit { oid } }
      }
    }
  }
}
"""


class NotEligible(Exception):
    pass


def require(condition, reason):
    if not condition:
        raise NotEligible(reason)


def api(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args], text=True))


def pages(path, key=None):
    for page in api("--paginate", "--slurp", path):
        yield from page[key] if key else page


def formula_at(path, sha):
    item = api(f"repos/{REPOSITORY}/contents/{path}?ref={sha}")
    require(item["type"] == "file" and item["encoding"] == "base64", "Expected a formula file")
    return base64.b64decode(item["content"]).decode()


def verify_release(project, branch_match, current, proposed, release):
    tag = release["tag_name"]
    require(
        re.fullmatch(rf"v{VERSION}", tag) and not release["draft"] and not release["prerelease"]
        and release["published_at"],
        "Upstream has no eligible stable release",
    )
    version = tag[1:]
    branch_version = branch_match.groupdict().get("version")
    require(branch_version in (None, version), "Branch is not for the latest upstream release")

    root = f"https://github.com/outfitter-dev/{project}/releases/download/"
    current_versions = set(re.findall(rf'^\s*url "{re.escape(root)}v({VERSION})/', current, re.M))
    require(len(current_versions) == 1, "Current formula version is not recognized")
    current_version = next(iter(current_versions))
    require(tuple(map(int, version.split("."))) > tuple(map(int, current_version.split("."))),
            "Version must advance the current formula")

    assets = {asset["name"]: asset.get("digest") for asset in release["assets"] if asset["state"] == "uploaded"}
    expected = {}
    for platform in PLATFORMS[project]:
        name = f"{project}-{tag}-{platform}.tar.gz"
        digest = assets.get(name) or ""
        require(re.fullmatch(r"sha256:[0-9a-f]{64}", digest), "Release asset or SHA-256 digest is missing")
        expected[f"{root}{tag}/{name}"] = digest.removeprefix("sha256:")

    pairs = re.findall(r'^ *url "([^"\n]+)"\s*\n *sha256 "([0-9a-f]{64})"$', proposed, re.M)
    require(
        dict(pairs) == expected and all(expected.get(url) == sha for url, sha in pairs)
        and len(pairs) == len(re.findall(r'^ *url\b', proposed, re.M))
        and not re.search(r"^\s*bottle\s+do\b", proposed, re.M),
        "Formula sources and checksums must match the published assets, with no prefilled bottles",
    )


def verify_reviews(number, head, base, author):
    pr = api("graphql", "-f", f"query={PR_REVIEW_QUERY}", "-F", f"number={number}")["data"]["repository"]["pullRequest"]
    require(
        pr is not None and pr["state"] == "OPEN" and pr["isDraft"]
        and pr["headRefOid"] == head and pr["baseRefOid"] == base
        and pr["mergeStateStatus"] == "CLEAN" and pr["reviewDecision"] in (None, "APPROVED"),
        "GitHub merge checks or required reviews are not satisfied for this draft head and base",
    )
    threads = pr["reviewThreads"]
    require(not threads["pageInfo"]["hasNextPage"] and all(t["isResolved"] for t in threads["nodes"]),
            "Review threads must be resolved")
    reviews = pr["latestOpinionatedReviews"]
    require(not reviews["pageInfo"]["hasNextPage"], "Could not see every reviewer decision")
    maintainers = [
        review for review in reviews["nodes"]
        if review["authorCanPushToRepository"] and review["author"]
        and review["author"]["__typename"] == "User" and review["author"]["login"] != author
    ]
    approvals = [review["commit"] for review in maintainers if review["state"] == "APPROVED"]
    require(approvals and all(commit and commit["oid"] == head for commit in approvals)
            and not any(r["state"] == "CHANGES_REQUESTED" for r in maintainers),
            "Maintainer approval of the exact head is required, without outstanding changes requested")


def verify_runs(number, head, branch):
    query = urlencode({"event": "pull_request", "head_sha": head, "branch": branch, "per_page": 100})
    for workflow in ("tests.yml", "formula-landing-policy.yml"):
        runs = pages(f"repos/{REPOSITORY}/actions/workflows/{workflow}/runs?{query}", "workflow_runs")
        run = next((run for run in runs if run["head_sha"] == head and run["event"] == "pull_request"
                    and (run["head_repository"] or {}).get("full_name") == REPOSITORY
                    and any(pr["number"] == number for pr in run["pull_requests"])), None)
        require(run and run["status"] == "completed" and run["conclusion"] == "success",
                f"Latest {workflow} run for this PR head has not succeeded")


def eligible(pr, base, expected_head=None):
    number, head, branch = pr["number"], pr["head"]["sha"], pr["head"]["ref"]
    require(pr["state"] == "open" and pr["draft"]
            and pr["base"]["ref"] == "main" and pr["base"]["sha"] == base
            and (pr["head"]["repo"] or {}).get("full_name") == REPOSITORY and re.fullmatch(SHA, head)
            and (expected_head is None or head == expected_head),
            "Expected an open same-tap draft on main and the selected head")
    project, match = next(((name, m) for name, pattern in BRANCHES.items()
                           if (m := re.fullmatch(pattern, branch))), (None, None))
    require(project, "Not a supported stable release branch")
    path = f"Formula/{project}.rb"
    permitted_paths = {path, "README.md"} if project == "skillset" else {path}

    # brew pr-pull cherry-picks every PR commit, so vet the whole commit, not just its net diff.
    commit = api(f"repos/{REPOSITORY}/commits/{head}?per_page=100")
    files = commit["files"]
    require([p["sha"] for p in commit["parents"]] == [base], "Expected one release commit directly on current main")
    require({f["filename"] for f in files} <= permitted_paths and any(f["filename"] == path for f in files)
            and all(f["status"] == "modified" and not f.get("previous_filename") for f in files),
            "Only the expected release files may be modified")

    verify_runs(number, head, branch)
    verify_reviews(number, head, base, pr["user"]["login"])
    verify_release(project, match, formula_at(path, base), formula_at(path, head),
                   api(f"repos/outfitter-dev/{project}/releases/latest"))
    return number, head


def main():
    base = os.environ["GITHUB_SHA"]
    recheck = len(sys.argv) > 1
    if os.environ["GITHUB_REPOSITORY"] != REPOSITORY or os.environ["GITHUB_REF"] != "refs/heads/main":
        sys.exit("Automatic publication only runs on the tap's main branch")
    if api(f"repos/{REPOSITORY}/git/ref/heads/main")["object"]["sha"] != base:
        message = "main moved; the next run must check the new base"
        if recheck:
            sys.exit(message)
        print(message)
        return

    if recheck:
        number, expected_head = sys.argv[1:]
        if not number.isascii() or not number.isdecimal() or not re.fullmatch(SHA, expected_head):
            sys.exit("Invalid selected PR number or head")
        candidates = [api(f"repos/{REPOSITORY}/pulls/{number}")]
    else:
        expected_head = None
        candidates = pages(f"repos/{REPOSITORY}/pulls?state=open&base=main&direction=asc&per_page=100")
    for pr in candidates:
        try:
            number, head = eligible(pr, base, expected_head)
        except NotEligible as error:
            print(f"PR #{pr['number']}: {error}")
            continue
        if not recheck:
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
                print(f"pull_request={number}\nhead_sha={head}", file=output)
        return
    if recheck:
        sys.exit("Selected release draft is no longer eligible")
    print("No eligible release drafts")


if __name__ == "__main__":
    main()
