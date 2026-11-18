"""Regenerate an authorized stale release draft without publishing it."""

import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

import select_release as gate


def git(*args, **kwargs):
    return subprocess.check_output(["git", *args], text=True, **kwargs).strip()


def refresh_candidate(pr, base, allowlist, support, expected_head=None):
    draft = gate.release_draft(pr, base, allowlist, expected_head, publishing=False)
    gate.require(draft.parent != base, "Release draft is already based on current main")
    gate.require(subprocess.run(["git", "merge-base", "--is-ancestor", draft.parent, base]).returncode == 0,
                 "Stale release parent is not in current main history")
    gate.verify_reviews(draft.number, draft.head, draft.review_base, draft.author, publishing=False)
    gate.require(git("rev-parse", f"{draft.parent}:{draft.path}") == git("rev-parse", f"{base}:{draft.path}"),
                 "The published formula changed since the draft was generated")
    return draft, gate.verify_formula(draft, base, support)


def build_commit(base, draft, formula):
    with TemporaryDirectory() as directory:
        env = {
            **os.environ,
            "GIT_INDEX_FILE": str(Path(directory) / "index"),
            "GIT_AUTHOR_NAME": "Outfitter Homebrew Refresher",
            "GIT_AUTHOR_EMAIL": "homebrew-refresher@users.noreply.github.com",
            "GIT_COMMITTER_NAME": "Outfitter Homebrew Refresher",
            "GIT_COMMITTER_EMAIL": "homebrew-refresher@users.noreply.github.com",
        }
        git("read-tree", base, env=env)
        blob = git("hash-object", "-w", "--stdin", input=formula, env=env)
        git("update-index", "--cacheinfo", f"100644,{blob},{draft.path}", env=env)
        tree = git("write-tree", env=env)
        return git("commit-tree", tree, "-p", base, "-m", f"Refresh {draft.project} formula on main", env=env)


def push_commit(draft, commit, remote=f"https://github.com/{gate.REPOSITORY}.git"):
    ref = f"refs/heads/{draft.branch}"
    git("-c", "credential.helper=", "-c", "credential.https://github.com.helper=!gh auth git-credential",
        "push", f"--force-with-lease={ref}:{draft.head}", remote, f"{commit}:{ref}")


def apply_refresh(number, head, base, allowlist, support):
    endpoint = f"repos/{gate.REPOSITORY}/pulls/{number}"
    draft, formula = refresh_candidate(gate.api(endpoint), base, allowlist, support, head)
    commit = build_commit(base, draft, formula)
    latest, regenerated = refresh_candidate(gate.api(endpoint), base, allowlist, support, head)
    gate.require(draft == latest and formula == regenerated, "Release inputs changed while preparing the refresh")
    gate.require(gate.current_main() == base, "main moved while preparing the refresh")
    push_commit(draft, commit)
    print(f"Refreshed release draft #{draft.number} to {commit}; awaiting fresh CI and any required reviews")


def main():
    base = os.environ["GITHUB_SHA"]
    applying = len(sys.argv) > 1
    if os.environ["GITHUB_REPOSITORY"] != gate.REPOSITORY or os.environ["GITHUB_REF"] != "refs/heads/main":
        sys.exit("Release refresh only runs on the tap's main branch")
    if not re.fullmatch(gate.SHA, base) or git("rev-parse", "HEAD") != base or gate.current_main() != base:
        sys.exit("Refresh requires the trusted current main checkout")

    try:
        allowlist = gate.load_allowlist(gate.ALLOWLIST_PATH)
        support = gate.load_support(gate.SUPPORT_PATH)
        if applying:
            if len(sys.argv) != 4 or sys.argv[1] != "--apply" or os.environ.get("GITHUB_ACTIONS") != "true":
                sys.exit("Release draft mutation is only supported by the refresh workflow")
            number, head = sys.argv[2:]
            if not re.fullmatch(r"[1-9][0-9]*", number) or not re.fullmatch(gate.SHA, head):
                sys.exit("Invalid refresh PR number or head")
            apply_refresh(number, head, base, allowlist, support)
            return

        for pr in gate.pages(f"repos/{gate.REPOSITORY}/pulls?state=open&base=main&direction=asc&per_page=100"):
            try:
                draft, _ = refresh_candidate(pr, base, allowlist, support)
            except gate.NotEligible as error:
                print(f"PR #{pr['number']}: {error}")
                continue
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
                print(f"pull_request={draft.number}\nhead_sha={draft.head}", file=output)
            return
    except gate.NotEligible as error:
        sys.exit(str(error))
    print("No authorized stale release drafts to refresh")


if __name__ == "__main__":
    main()
