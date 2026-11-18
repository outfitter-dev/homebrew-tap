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

Successful tap CI wakes [`brew pr-pull`](.github/workflows/publish.yml). A twice-hourly scan picks up approvals submitted after CI and recovers missed events. The workflow uses the existing publisher, not a new dispatch token.

- Only same-tap Trails and Skillset stable release drafts qualify. The formula must advance the current version and match the URLs and SHA-256 digests of the latest published upstream release. An npm release alone does not qualify: the GitHub assets and tap draft must exist.
- The draft must contain one release commit on current `main` and touch only the formula (Skillset may also update its README entry). If `main` moves, regenerate or rebase the draft and retest it.
- Both tap workflows, every required check, and GitHub's merge/review rules must pass. A maintainer other than the PR author must approve the exact head SHA; changes requested or unresolved review threads block publication. A failed Intel job blocks it too.
- The publisher checks eligibility before setting up Homebrew and again before invoking `brew pr-pull`. It does not automatically run merged-PR recovery.

The current `blz` handoff does not create a draft and is not eligible for automation. Continue using the manual path for formula updates outside the automated handoffs.

### Manual publication and recovery

After review and every required Homebrew check passes, run the [`brew pr-pull`](.github/workflows/publish.yml) workflow from the `main` branch with both of these inputs:

- `pull_request`: the formula pull request number.
- `head_sha`: the pull request's tested head commit SHA.

The head SHA guard prevents publishing if the pull request changed after its successful test run. The workflow verifies that the exact head remains a draft and that every required check succeeded before Homebrew setup begins. It then mints a one-hour installation token for the tap-only Outfitter Homebrew Publisher GitHub App. `brew pr-pull` owns the landing operation: it downloads the bottle artifacts, updates the formula, uploads the bottles to a GitHub release, creates build-provenance attestations for the bottles, and pushes the resulting commit to `main` through the publisher App's ruleset bypass. Publication runs are serialized so two formula updates cannot race to push the tap.

The publisher App is installed only on this repository and receives `actions: read`, `contents: write`, and `pull requests: write`. Its client ID is stored in the Homebrew-standard `BREW_COMMIT_CLIENT_ID` Actions variable and its private key in the `HOMEBREW_PUBLISHER_APP_PRIVATE_KEY` Actions secret. The normal `GITHUB_TOKEN` remains read-only preflight authority and cannot land formula changes.

If a formula pull request was already merged manually, stop instead of rerunning the ordinary path or reverting the formula. The workflow's `merged_pr_recovery` input is an emergency path that validates the exact reviewed head, merge topology, current `main`, ancestry, and formula contents before creating the missing bottle commit.

The tap tests its publication setup on bare Ubuntu with Homebrew 7 or newer, in addition to the formula matrix. Intel macOS remains in the matrix while GitHub and Homebrew provide a usable runner; Homebrew 7 classifies Intel macOS as Tier 3, so Intel bottles are best-effort rather than a guaranteed upstream Homebrew platform.

See [Homebrew's documentation](https://docs.brew.sh) for general Homebrew usage.

## Skillset

Skillset is available as a native CLI for Apple Silicon and Intel macOS.

```sh
brew install outfitter-dev/tap/skillset
```

Upgrade or uninstall it with `brew upgrade skillset` or `brew uninstall skillset`.

Formula updates arrive through a tested pull request and are landed by `brew pr-pull` only after tap CI passes.
