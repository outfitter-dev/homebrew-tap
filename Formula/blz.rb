class Blz < Formula
  desc "Fast local search for llms.txt"
  homepage "https://blz.run"
  version "2.1.0-beta.1"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-arm64.tar.gz"
      sha256 "113520477ffe93e3b9565fa988eec0fdf5c4585f4239df27c5a948542580193d"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-x64.tar.gz"
      sha256 "61ab3a62fc0f0a3c15c032f4dbf4c37ebb47a41c0acbd7981e1eb155688345e4"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "ae8c48aafcfce29690322e8633d0262d6067f18a9181f012e5978da0353af70f"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "ae8c48aafcfce29690322e8633d0262d6067f18a9181f012e5978da0353af70f"
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
