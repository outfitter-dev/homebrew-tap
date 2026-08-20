class Trails < Formula
  desc "Agent-native, contract-first TypeScript framework"
  homepage "https://github.com/outfitter-dev/trails"
  version "1.0.0-beta.49"
  license "MIT"

  depends_on "bun"

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v#{version}/trails-v#{version}-darwin-arm64.tar.gz"
      sha256 "9188d0bbe15a897e209ada67e7c689b4a5d9a88257110c84f8ea901cc40b3c8a"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v#{version}/trails-v#{version}-darwin-x64.tar.gz"
      sha256 "31fdc9b1419c849974ec98941eb040fb771073aada2a6f42c13c33769906e3aa"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v#{version}/trails-v#{version}-linux-arm64.tar.gz"
      sha256 "b6b426398645c23a4610f7de5ca2b0efd275d218382a1ef7e3b544df2c7d3b97"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v#{version}/trails-v#{version}-linux-x64.tar.gz"
      sha256 "f956d10ee94ff4cf7aa869a72874e1b242e8431c7d8fab2d22712c707f40274e"
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
