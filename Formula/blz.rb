class Blz < Formula
  desc "Fast local search for llms.txt"
  homepage "https://blz.run"
  license "Apache-2.0"
  version "0.4.0"

  livecheck do
    url "https://github.com/outfitter-dev/blz/releases/latest"
    strategy :github_latest
  end

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-arm64.tar.gz"
      sha256 "d6d9c1605954923bc08ceb934ef4765a72e242cb88c07f708a8e1656769c1f0b"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-x64.tar.gz"
      sha256 "aa3e130b977055aec6a431922bd65cbc9c2bdcda261a9f0fd7192ce9e569c508"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "3c3171b9cd67c2d1cba0d46d9485028c487569369e34c0791f7cd14ff941ee2e"
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
