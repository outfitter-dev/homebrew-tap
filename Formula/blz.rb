class Blz < Formula
  desc "Fast local search for llms.txt"
  homepage "https://blz.run"
  version "2.0.0-beta.1"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-arm64.tar.gz"
      sha256 "653795fd28b10fc08887bc98414a6f5fff8f56d7d55e43bb03e97e6c65eec58c"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-x64.tar.gz"
      sha256 "0fc7e459077ba06516147ab6a6c92651aea130349c2919a7490bb86ba2314c13"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "1e8ece23104cf7c29361c0f36e7b4d4cd0d81bea414b09a8de14e74100a4358b"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "1e8ece23104cf7c29361c0f36e7b4d4cd0d81bea414b09a8de14e74100a4358b"
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
