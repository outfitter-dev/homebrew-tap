# Outfitter Homebrew Tap

This tap distributes Outfitter command-line tools as Homebrew formulae.

## Install

```sh
brew install outfitter-dev/tap/blz
```

To add the tap separately:

```sh
brew tap outfitter-dev/tap
brew install blz
```

In a `Brewfile`:

```ruby
tap "outfitter-dev/tap"
brew "blz"
```

## Publish A Formula Update

Upstream release workflows open formula pull requests in this repository. The [`brew test-bot`](.github/workflows/tests.yml) workflow audits the formula, tests installation, and uploads bottles for macOS and Linux.

Keep formula pull requests open and in draft. **Do not mark them ready or merge them with GitHub's merge button.** The `formula-landing-policy` check rejects formula pull requests that are marked ready.

### Automatic publication

After reviewing and merging the automation, a tap maintainer can opt in by setting the repository's [Actions variable `HOMEBREW_AUTO_PUBLISH`](https://github.com/outfitter-dev/homebrew-tap/settings/variables/actions) to `true`. Unset it or change it to `false` to stop new automatic jobs; this does not cancel an in-flight job. The manual path is unchanged.

Successful tap CI wakes a read-only scan in [`brew pr-pull`](.github/workflows/publish.yml). A twice-hourly scan picks up approvals submitted after CI and recovers missed events. No-op scans do not enter the serialized publisher job or displace pending manual runs.

- The reviewed [`autopublish.yaml`](.github/autopublish.yaml) on current `main` lists which upstream repositories can publish automatically. It lists Skillset and Trails. Use a JSON-style YAML list of supported `owner/repository` names; an empty list disables automatic publication, and a missing or invalid file fails closed.
- Only same-tap stable release drafts from listed upstreams qualify. Every byte of the formula must match what the [reviewed template](.github/workflows/release-policy) generates from the latest stable upstream release and its GitHub asset digests. The version must advance. An npm release alone does not qualify.
- The draft must contain one release commit on current `main` and touch only its formula. Drafts with other changes, such as a Skillset README update, are not candidates for automatic publication.
- [Install support](.github/workflows/release-policy/install-support.json) is reviewed per project, platform, and method. `formula_archive` means the upstream asset consumed by the formula; `homebrew_bottle` means tap-built evidence. Only an explicit `unsupported` target waives the evidence for that method. Unknown support, missing assets, or absent or expired bottles on supported targets block publication. This policy does not change the GitHub CI matrix or required checks.
- Both tap workflows, every required check, and GitHub's merge/review rules must pass. A maintainer other than the PR author must approve the exact head SHA; changes requested or unresolved review threads block publication.
- The publisher checks eligibility before setting up Homebrew and again before invoking `brew pr-pull`. It does not automatically run merged-PR recovery.

The current `blz` handoff does not create a draft and is not eligible for automation.

### Manual publication and recovery

After review and every required Homebrew check passes, run the [`brew pr-pull`](.github/workflows/publish.yml) workflow from the `main` branch with both of these inputs:

- `pull_request`: the formula pull request number.
- `head_sha`: the pull request's tested head commit SHA.

The head SHA guard prevents publishing if the pull request changed after its successful test run. The workflow verifies that the exact head remains a draft and that every required check succeeded before Homebrew setup begins. It then mints a one-hour installation token for the tap-only Outfitter Homebrew Publisher GitHub App. `brew pr-pull` owns the landing operation: it downloads the bottle artifacts, updates the formula, uploads the bottles to a GitHub release, creates build-provenance attestations for the bottles, and pushes the resulting commit to `main` through the publisher App's ruleset bypass. Publication runs are serialized so two formula updates cannot race to push the tap.

The publisher App is installed only on this repository and receives `actions: read`, `contents: write`, and `pull requests: write`. Its client ID is stored in the Homebrew-standard `BREW_COMMIT_CLIENT_ID` Actions variable and its private key in the `HOMEBREW_PUBLISHER_APP_PRIVATE_KEY` Actions secret. The normal `GITHUB_TOKEN` remains read-only preflight authority and cannot land formula changes.

If a formula pull request was already merged manually, stop instead of rerunning the ordinary path or reverting the formula. The workflow's `merged_pr_recovery` input is an emergency path that validates the exact reviewed head, merge topology, current `main`, ancestry, and formula contents before creating the missing bottle commit.

The tap tests its publication setup on bare Ubuntu with Homebrew 7 or newer, in addition to the formula matrix. Intel macOS remains in the matrix while GitHub and Homebrew provide a usable runner; Homebrew 7 classifies Intel macOS as Tier 3, so Intel bottles are best-effort rather than a guaranteed upstream Homebrew platform.

See [Homebrew's documentation](https://docs.brew.sh) for general Homebrew usage.

### Refresh stale release drafts

When enabled, [the refresh workflow](.github/workflows/refresh-releases.yml) scans after pushes to `main` and twice an hour. It refreshes an independently approved stale draft only if its old parent is in `main` history, the published formula has not changed since that parent, and the draft still matches the trusted template and verified release. It regenerates one formula commit from current `main` and updates only the release branch, using a lease against the old head.

The refresh push starts normal PR CI. The refreshed head needs fresh CI, bottles, and independent approval before publication. An unresolved review, a noncanonical draft, or a newer upstream release not matching the draft blocks regeneration.

Refresh is off by default. To enable it, install a separate tap-only GitHub App with Contents write and Pull requests read access and no ruleset bypass. Configure `HOMEBREW_REFRESH_APP_CLIENT_ID` and `HOMEBREW_REFRESH_APP_PRIVATE_KEY`, then set `HOMEBREW_AUTO_REFRESH` to `true`. Both automation switches must be on for refresh to run. The refresher never uses the publisher credential.

## Trails

Homebrew is supported on Apple Silicon Macs and Linux arm64 and x64:

```sh
brew install outfitter-dev/tap/trails
```

On Intel Macs, use the `trails-v<version>-darwin-x64.tar.gz` standalone archive from the [Trails releases page](https://github.com/outfitter-dev/trails/releases/latest) instead. Verify its GitHub release asset SHA-256 before extracting it. The tap requires that archive's digest but does not require an Intel Trails bottle. Intel CI remains required, including both macOS bottles for Skillset.

## Skillset

Skillset is available as a native CLI for Apple Silicon and Intel macOS.

```sh
brew install outfitter-dev/tap/skillset
```

Upgrade or uninstall it with `brew upgrade skillset` or `brew uninstall skillset`.

Formula updates arrive through a tested pull request and are landed by `brew pr-pull` only after tap CI passes.
