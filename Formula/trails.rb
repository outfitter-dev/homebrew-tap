class Trails < Formula
  desc "Agent-native, contract-first TypeScript framework"
  homepage "https://github.com/outfitter-dev/trails"
  license "MIT"
  # Keep this scheme after the reset from 1.0.0-beta to 0.2.0.
  version_scheme 1

  depends_on "bun"

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.2/trails-v0.2.2-darwin-arm64.tar.gz"
      sha256 "1229cbb4ad0eb486eeb7a25ae47e418791875820fd411b95418fb6bc42f35f9e"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.2/trails-v0.2.2-darwin-x64.tar.gz"
      sha256 "c9a90780152399cce10850e9d66492c20a9bc1ebb1966e29996006bb8bc588b0"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.2/trails-v0.2.2-linux-arm64.tar.gz"
      sha256 "b0b70230eba328fae1c630995af01ced7c41ccf9ceb74c7c07b3f4c2e5307127"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.2/trails-v0.2.2-linux-x64.tar.gz"
      sha256 "855449446c7ccefea04542486603de1db8bb1349297bf70c42e1c785a3a5513e"
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
