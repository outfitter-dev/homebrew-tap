class Blz < Formula
  desc "Fast local search for llms.txt"
  homepage "https://blz.run"
  license "Apache-2.0"
  version "0.3.0"

  livecheck do
    url "https://github.com/outfitter-dev/blz/releases/latest"
    strategy :github_latest
  end

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-arm64.tar.gz"
      sha256 "9acd1046fd2435951c3550442ae20b9d3dd1b188f912415741a4e5118f85972e"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-x64.tar.gz"
      sha256 "429ed7bf86497a04e7befe958a0537fc8680ddf7ee1c5e3b0b926ff0436c9896"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "7ae0e29733357a04eea4135ed6ddc7a13361789a0b5d015e141ab8e5ac998314"
    end
  end

  def install
    bin.install "blz"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/blz --version")
    assert_match "blz", shell_output("#{bin}/blz --help")
  end
end
