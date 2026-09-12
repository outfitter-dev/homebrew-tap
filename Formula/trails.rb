class Trails < Formula
  desc "Agent-native, contract-first TypeScript framework"
  homepage "https://github.com/outfitter-dev/trails"
  license "MIT"
  # Keep this scheme after the reset from 1.0.0-beta to 0.2.0.
  version_scheme 1

  bottle do
    root_url "https://github.com/outfitter-dev/homebrew-tap/releases/download/trails-0.2.1"
    sha256 cellar: :any,                 arm64_tahoe:  "59a45b42e5c4f50be089bae3cbc1b13606a82739dbc1328e7078dd6614b7eb0a"
    sha256 cellar: :any_skip_relocation, arm64_linux:  "93049699af8121c3bed0c81c55dc4afa1b0579a71500e040928f5352dac6b50e"
    sha256 cellar: :any_skip_relocation, x86_64_linux: "44d9a824dbd2bedfda5f18258f750417244cf5973a75b33e3346ac223bc99957"
  end

  depends_on "bun"

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.1/trails-v0.2.1-darwin-arm64.tar.gz"
      sha256 "f90130b7f8ca314cff87b44816fce699667d90b79f84b834ccb663be81d16c22"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.1/trails-v0.2.1-darwin-x64.tar.gz"
      sha256 "dbd6a36ff793d1121f9318d7a215f998d70e87e5ad051a21041672ce619c9916"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.1/trails-v0.2.1-linux-arm64.tar.gz"
      sha256 "ffa83649456d1f555c3f102e9af89d1ae0b7df0104346e6a4426422955ea452c"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.1/trails-v0.2.1-linux-x64.tar.gz"
      sha256 "abe076065413a890c2fb72c46f8bc5eb826d6c163f25a1732ecf915b7cab7e46"
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
