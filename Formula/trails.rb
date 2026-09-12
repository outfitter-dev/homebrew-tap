class Trails < Formula
  desc "Agent-native, contract-first TypeScript framework"
  homepage "https://github.com/outfitter-dev/trails"
  license "MIT"
  # Keep this scheme after the reset from 1.0.0-beta to 0.2.0.
  version_scheme 1

  bottle do
    root_url "https://github.com/outfitter-dev/homebrew-tap/releases/download/trails-0.2.2"
    sha256 cellar: :any,                 arm64_tahoe:  "81bd8258aa92cf00e6e4639e0b7ed5bc104453fec48bd3a8c63cb638a80d06d7"
    sha256 cellar: :any_skip_relocation, arm64_linux:  "a89022893014db861bb98fdc60ef4a196a6e71b69770ef2454951422f2be494c"
    sha256 cellar: :any_skip_relocation, x86_64_linux: "c0e4b93e2f8baac70226d06d5adfdb75a9276ab9282d6e5af70e93c30b3ca386"
  end

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
