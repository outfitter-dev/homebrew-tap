class Blz < Formula
  desc "Fast local search for llms.txt"
  homepage "https://blz.run"
  license "Apache-2.0"
  version "0.4.1"

  livecheck do
    url "https://github.com/outfitter-dev/blz/releases/latest"
    strategy :github_latest
  end

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-arm64.tar.gz"
      sha256 "5350e56b85a4c62779f40ed6562344a633589530f062d83d70f4f4093a8d48f6"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-x64.tar.gz"
      sha256 "967b11237d991a74c562c54beb03c869acef3123c485c3f48a547eea8f3a1b9b"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "f5e61c727122f0eab4d0f907b1756768edb9f0db6df0261c8256f17e49c7419d"
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
