"""Read-only eligibility gate for automatic brew pr-pull."""

import base64
from dataclasses import dataclass
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from string import Template
from urllib.parse import urlencode


REPOSITORY = "outfitter-dev/homebrew-tap"
CONFIG_DIR = Path(__file__).resolve().parents[1]
ALLOWLIST_PATH = CONFIG_DIR / "autopublish.yaml"
RELEASE_POLICY = CONFIG_DIR / "workflows" / "release-policy"
SUPPORT_PATH = RELEASE_POLICY / "install-support.json"
VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
SHA = r"[0-9a-f]{40}"
BRANCHES = {
    "trails": rf"release/trails-(?P<version>{VERSION})",
    "skillset": r"release/skillset",
}
BOTTLE_RUNNERS = {
    "darwin-arm64": "macos-26",
    "darwin-x64": "macos-15-intel",
    "linux-arm64": "ubuntu-24.04-arm",
    "linux-x64": "ubuntu-latest",
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


@dataclass(frozen=True)
class Draft:
    number: int
    head: str
    branch: str
    author: str
    project: str
    branch_version: str | None
    parent: str
    review_base: str

    @property
    def path(self):
        return f"Formula/{self.project}.rb"


def require(condition, reason):
    if not condition:
        raise NotEligible(reason)


def api(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args], text=True))


def pages(path, key=None):
    for page in api("--paginate", "--slurp", path):
        yield from page[key] if key else page


def load_allowlist(path):
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise NotEligible("Cannot read a valid autopublish.yaml") from error
    supported = {f"outfitter-dev/{project}" for project in BRANCHES}
    require(
        isinstance(entries, list)
        and all(isinstance(entry, str) and entry in supported for entry in entries)
        and len(set(entries)) == len(entries),
        "autopublish.yaml must be a unique list of supported upstream repositories",
    )
    return frozenset(entries)


def unique_keys(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate key")
    return result


def load_support(path):
    try:
        entries = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
    except (OSError, ValueError) as error:
        raise NotEligible("Cannot read a valid install-support.json") from error
    require(isinstance(entries, dict) and entries.keys() == BRANCHES.keys(),
            "Install support is unknown for one or more projects")
    support = {}
    for project, methods in entries.items():
        require(isinstance(methods, dict) and methods.keys() == {"formula_archive", "homebrew_bottle"},
                f"Install support is unknown for an install method for {project}")
        support[project] = {}
        for method, targets in methods.items():
            require(isinstance(targets, dict) and targets.keys() == BOTTLE_RUNNERS.keys()
                    and all(status in ("supported", "unsupported") for status in targets.values()),
                    f"Install support is unknown for a {project} {method} target")
            support[project][method] = {target for target, status in targets.items() if status == "supported"}
        supported = support[project]
        require(supported["homebrew_bottle"] and supported["homebrew_bottle"] <= supported["formula_archive"],
                f"Supported Homebrew bottles must have formula archives for {project}")
    return support


def formula_at(path, sha):
    item = api(f"repos/{REPOSITORY}/contents/{path}?ref={sha}")
    require(item["type"] == "file" and item["encoding"] == "base64", "Expected a formula file")
    return base64.b64decode(item["content"]).decode()


def render_formula(project, tag, digests):
    values = {"tag": tag, **{f"sha_{platform.replace('-', '_')}": digest
                            for platform, digest in digests.items()}}
    try:
        template = Template((RELEASE_POLICY / f"{project}.rb.in").read_text(encoding="utf-8"))
        identifiers = [m["named"] or m["braced"] for m in template.pattern.finditer(template.template)]
        require(set(identifiers) == values.keys()
                and all(identifiers.count(key) == 1 for key in values if key != "tag"),
                "Reviewed formula template must cover exactly the supported archives")
        return template.substitute(values)
    except (OSError, KeyError, ValueError) as error:
        raise NotEligible("Cannot render the reviewed formula template") from error


def generate_formula(project, branch_version, current, release, archives):
    tag = release["tag_name"]
    require(
        re.fullmatch(rf"v{VERSION}", tag) and not release["draft"] and not release["prerelease"]
        and release["published_at"],
        "Upstream has no eligible stable release",
    )
    version = tag[1:]
    require(branch_version in (None, version), "Branch is not for the latest upstream release")

    root = f"https://github.com/outfitter-dev/{project}/releases/download/"
    current_versions = set(re.findall(rf'^\s*url "{re.escape(root)}v({VERSION})/', current, re.M))
    require(len(current_versions) == 1, "Current formula version is not recognized")
    current_version = next(iter(current_versions))
    require(tuple(map(int, version.split("."))) > tuple(map(int, current_version.split("."))),
            "Version must advance the current formula")

    assets = [asset for asset in release["assets"] if asset["state"] == "uploaded"]
    digests = {}
    for platform in archives:
        name = f"{project}-{tag}-{platform}.tar.gz"
        matches = [asset.get("digest") or "" for asset in assets if asset["name"] == name]
        require(len(matches) == 1 and re.fullmatch(r"sha256:[0-9a-f]{64}", matches[0]),
                f"Release asset or SHA-256 digest is missing or ambiguous for {platform}")
        digests[platform] = matches[0].removeprefix("sha256:")

    return render_formula(project, tag, digests)


def verify_reviews(number, head, base, author, *, publishing=True):
    pr = api("graphql", "-f", f"query={PR_REVIEW_QUERY}", "-F", f"number={number}")["data"]["repository"]["pullRequest"]
    require(
        pr is not None and pr["state"] == "OPEN" and pr["isDraft"]
        and pr["headRefOid"] == head and pr["baseRefOid"] == base
        and (not publishing or pr["mergeStateStatus"] == "CLEAN")
        and pr["reviewDecision"] in (None, "APPROVED"),
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
    exact_approval = any(r["state"] == "APPROVED" and r["commit"] and r["commit"]["oid"] == head
                         for r in maintainers)
    require(exact_approval
            and not any(r["state"] == "CHANGES_REQUESTED" for r in maintainers),
            "Maintainer approval of the exact head is required, without outstanding changes requested")


def verify_runs(number, head, branch, bottle_targets):
    query = urlencode({"event": "pull_request", "head_sha": head, "branch": branch, "per_page": 100})
    for workflow in ("tests.yml", "formula-landing-policy.yml"):
        runs = pages(f"repos/{REPOSITORY}/actions/workflows/{workflow}/runs?{query}", "workflow_runs")
        run = next((run for run in runs if run["head_sha"] == head and run["event"] == "pull_request"
                    and (run["head_repository"] or {}).get("full_name") == REPOSITORY
                    and any(pr["number"] == number for pr in run["pull_requests"])), None)
        require(run and run["status"] == "completed" and run["conclusion"] == "success",
                f"Latest {workflow} run for this PR head has not succeeded")
        if workflow == "tests.yml":
            artifacts = pages(f"repos/{REPOSITORY}/actions/runs/{run['id']}/artifacts?per_page=100", "artifacts")
            available = {a["name"] for a in artifacts if not a["expired"] and a["size_in_bytes"] > 0}
            expected = {f"bottles_{BOTTLE_RUNNERS[target]}" for target in bottle_targets}
            missing = expected - available
            require(not missing, f"Test run is missing unexpired bottle artifacts: {', '.join(sorted(missing))}")


def release_draft(pr, base, allowlist, expected_head=None, *, publishing=True):
    number, head, branch = pr["number"], pr["head"]["sha"], pr["head"]["ref"]
    review_base = pr["base"]["sha"]
    require(pr["state"] == "open" and pr["draft"]
            and pr["base"]["ref"] == "main" and re.fullmatch(SHA, review_base)
            and (not publishing or review_base == base)
            and (pr["head"]["repo"] or {}).get("full_name") == REPOSITORY and re.fullmatch(SHA, head)
            and (expected_head is None or head == expected_head),
            "Expected an open same-tap draft on main and the selected head")
    project, match = next(((name, m) for name, pattern in BRANCHES.items()
                           if (m := re.fullmatch(pattern, branch))), (None, None))
    require(project, "Not a supported stable release branch")
    upstream = f"outfitter-dev/{project}"
    require(upstream in allowlist, f"{upstream} is not allowed by autopublish.yaml")

    # brew pr-pull cherry-picks every PR commit, so vet the whole commit, not just its net diff.
    commit = api(f"repos/{REPOSITORY}/commits/{head}?per_page=100")
    parents = commit["parents"]
    require(len(parents) == 1 and re.fullmatch(SHA, parents[0]["sha"]), "Expected one release commit")
    draft = Draft(number, head, branch, pr["user"]["login"], project, match.groupdict().get("version"),
                  parents[0]["sha"], review_base)
    files = commit["files"]
    require(len(files) == 1 and files[0]["filename"] == draft.path and files[0]["status"] == "modified"
            and not files[0].get("previous_filename"), "Only the expected release formula may be modified")
    tree = api(f"repos/{REPOSITORY}/git/trees/{commit['commit']['tree']['sha']}?recursive=1")
    require(not tree["truncated"] and any(entry["path"] == draft.path and entry["mode"] == "100644"
                                          and entry["type"] == "blob" for entry in tree["tree"]),
            "Expected a regular formula file with unchanged permissions")
    return draft


def verify_formula(draft, base, support):
    expected = generate_formula(draft.project, draft.branch_version, formula_at(draft.path, base),
                                api(f"repos/outfitter-dev/{draft.project}/releases/latest"),
                                support[draft.project]["formula_archive"])
    require(formula_at(draft.path, draft.head) == expected,
            "Full formula must match the reviewed template and verified release")
    return expected


def eligible(pr, base, allowlist, support, expected_head=None):
    draft = release_draft(pr, base, allowlist, expected_head)
    require(draft.parent == base, "Expected one release commit directly on current main")
    verify_runs(draft.number, draft.head, draft.branch, support[draft.project]["homebrew_bottle"])
    verify_reviews(draft.number, draft.head, base, draft.author)
    verify_formula(draft, base, support)
    return draft.number, draft.head


def current_main():
    return api(f"repos/{REPOSITORY}/git/ref/heads/main")["object"]["sha"]


def main():
    base = os.environ["GITHUB_SHA"]
    recheck = len(sys.argv) > 1
    if os.environ["GITHUB_REPOSITORY"] != REPOSITORY or os.environ["GITHUB_REF"] != "refs/heads/main":
        sys.exit("Automatic publication only runs on the tap's main branch")
    if current_main() != base:
        message = "main moved; the next run must check the new base"
        if recheck:
            sys.exit(message)
        print(message)
        return

    try:
        allowlist = load_allowlist(ALLOWLIST_PATH)
        support = load_support(SUPPORT_PATH)
    except NotEligible as error:
        sys.exit(str(error))

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
            number, head = eligible(pr, base, allowlist, support, expected_head)
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
