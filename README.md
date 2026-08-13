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

After every `brew test-bot` job passes, run the [`brew pr-pull`](.github/workflows/publish.yml) workflow from GitHub Actions with both of these inputs:

- `pull_request`: the formula pull request number.
- `head_sha`: the pull request's tested head commit SHA.

The head SHA guard prevents publishing if the pull request changed after its successful test run. `brew pr-pull` downloads the bottle artifacts, updates the formula, uploads the bottles to a GitHub release, and pushes the resulting commit to `main`.

See [Homebrew's documentation](https://docs.brew.sh) for general Homebrew usage.

## Skillset

Skillset is available as a native CLI for Apple Silicon and Intel macOS.

```sh
brew install outfitter-dev/tap/skillset
```

Upgrade or uninstall it with `brew upgrade skillset` or `brew uninstall skillset`.

Formula updates arrive through a tested pull request and are merged only after tap CI passes.
