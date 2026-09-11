class Trails < Formula
  desc "Agent-native, contract-first TypeScript framework"
  homepage "https://github.com/outfitter-dev/trails"
  license "MIT"
  # Keep this scheme after the reset from 1.0.0-beta to 0.2.0.
  version_scheme 1

  bottle do
    root_url "https://github.com/outfitter-dev/homebrew-tap/releases/download/trails-0.2.0"
    sha256 cellar: :any,                 arm64_tahoe:  "5018d3529ca20d318a5d05fb5379e55fb2c99fc9fb68ecf0c4fe4e3dd7f6b444"
    sha256 cellar: :any_skip_relocation, arm64_linux:  "5f501d20441fd610fd9a4f0bb6bc404617f767958fbf04562e8f7e2e5fc9a7db"
    sha256 cellar: :any_skip_relocation, x86_64_linux: "17f58fbcb783e5b38bfec3b5dc1f58f426f7d5482a173f55d6eba8e54d875816"
  end

  depends_on "bun"

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.0/trails-v0.2.0-darwin-arm64.tar.gz"
      sha256 "27d879f400b312e95aca27d05c8c45b680ef89216f294dd0dcee402089d69608"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.0/trails-v0.2.0-darwin-x64.tar.gz"
      sha256 "af624c87fb3f457fdf39ebb689f7a95554eb94cc8471436d522266d873cf2dab"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.0/trails-v0.2.0-linux-arm64.tar.gz"
      sha256 "42fd9bcf5ff0b1428ee835bc26855d8a5201cc8f2b2bdbe404d5c58423d36894"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.0/trails-v0.2.0-linux-x64.tar.gz"
      sha256 "052c0dc188383852635a68a18b71c9da82c61c5141907f6805af145266009121"
    end
  end

  def install
    libexec.install Dir["*"]
    bin.install_symlink libexec/"bin/trails"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/trails --version")
    assert_match "Usage: trails", shell_output("#{bin}/trails --help")
  end
end
