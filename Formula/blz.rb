class Blz < Formula
  desc "Fast local search for llms.txt"
  homepage "https://blz.run"
  version "1.3.0"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-arm64.tar.gz"
      sha256 "73df3564115e7db94546ef1276881a74c19c6204965259a8757342cd3e2121bd"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-x64.tar.gz"
      sha256 "d218ff45af5241ddb5aac565a9dcd2284fb7c4655f61e801605c5386d7bca18d"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "532f29bd859651848dd2cab7410fb6ad407604a42cb68ef32c24c950c3f9a967"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "532f29bd859651848dd2cab7410fb6ad407604a42cb68ef32c24c950c3f9a967"
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
