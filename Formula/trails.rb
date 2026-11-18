class Trails < Formula
  desc "Agent-native, contract-first TypeScript framework"
  homepage "https://github.com/outfitter-dev/trails"
  license "MIT"
  # Keep this scheme after the reset from 1.0.0-beta to 0.2.0.
  version_scheme 1

  depends_on "bun"

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.3.0/trails-v0.3.0-darwin-arm64.tar.gz"
      sha256 "3a71324c3b113b555c357f906a73a8ed058bc77ac0706be9748033253eb8fe16"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.3.0/trails-v0.3.0-darwin-x64.tar.gz"
      sha256 "2e72cda2ba8d4cb8d664dc3a02cfd1473871fc498e4c92b3eae0b38635c7fd4b"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.3.0/trails-v0.3.0-linux-arm64.tar.gz"
      sha256 "bffb2ddeb7e479db0134cbee8f051e2da0d4d4cc1184d76a26e43350cc293dd6"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.3.0/trails-v0.3.0-linux-x64.tar.gz"
      sha256 "b9f031be918e83b657a8108a423167a7c95fe809162463525e9bd7ec52dc93ee"
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
