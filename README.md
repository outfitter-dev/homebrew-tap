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

The `blz` release workflow opens a formula pull request in this repository. The [`brew test-bot`](.github/workflows/tests.yml) workflow audits the formula, tests installation, and uploads bottles for macOS and Linux.

Keep the formula pull request open while it is reviewed. **Do not merge it with GitHub's merge button.** After every `brew test-bot` job passes, run the [`brew pr-pull`](.github/workflows/publish.yml) workflow from the `main` branch with both of these inputs:

- `pull_request`: the formula pull request number.
- `head_sha`: the pull request's tested head commit SHA.

The head SHA guard prevents publishing if the pull request changed after its successful test run. `brew pr-pull` owns the landing operation: it downloads the bottle artifacts, updates the formula, uploads the bottles to a GitHub release, creates build-provenance attestations for the bottles, and pushes the resulting commit to `main`. Publication runs are serialized so two formula updates cannot race to push the tap.

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
