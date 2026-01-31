class Blz < Formula
  desc "Fast local search for llms.txt"
  homepage "https://blz.run"
  version "2.2.0-beta.1"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-arm64.tar.gz"
      sha256 "5309f18e339c089bce7eb8370037c26adf99707b062e5d52f1be896bc73bcbf3"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-x64.tar.gz"
      sha256 "0fd5ca3149aa5df24c74032a315d63b6a983ebef66741d1f783e10efe1a7398e"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "b61f5cb392ca908e16c45f1a0299d6c9d390c1814f4e234b0fc7db997ca7684e"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "b61f5cb392ca908e16c45f1a0299d6c9d390c1814f4e234b0fc7db997ca7684e"
    end
  end

  def install
    if OS.linux? && Hardware::CPU.arm?
      odie "The blz Linux arm64 binary is not available yet. Please use the x86_64 build."
    end
    bin.install "blz"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/blz --version")
    assert_match "blz", shell_output("#{bin}/blz --help")
  end
end
