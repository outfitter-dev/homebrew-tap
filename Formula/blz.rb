class Blz < Formula
  desc "Fast local search for llms.txt"
  homepage "https://blz.run"
  version "1.5.1"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-arm64.tar.gz"
      sha256 "589be3388281a30e9e2fa29b72bdc302273feef3a7f3c804ddeef44b33d60a67"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-x64.tar.gz"
      sha256 "02408c2cd1c66a44c92d467a8c7cc90387426b85162e2fb4c48f68ae7e6cee60"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "c19214f1328a7aecc65c66a323c8af2f7bc5be2e7d876994444fff989f197ee2"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "c19214f1328a7aecc65c66a323c8af2f7bc5be2e7d876994444fff989f197ee2"
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
