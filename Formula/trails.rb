class Trails < Formula
  desc "Agent-native, contract-first TypeScript framework"
  homepage "https://github.com/outfitter-dev/trails"
  license "MIT"

  depends_on "bun"

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v1.0.0-beta.50/trails-v1.0.0-beta.50-darwin-arm64.tar.gz"
      sha256 "55fff107cdae3a8e9702e00667e000464998336e28a53cdda2116e62e5c8dc1e"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v1.0.0-beta.50/trails-v1.0.0-beta.50-darwin-x64.tar.gz"
      sha256 "a02ff84b0dcd6d550a86842efe8357785e3e03dcfdadd33869454048686a0a77"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v1.0.0-beta.50/trails-v1.0.0-beta.50-linux-arm64.tar.gz"
      sha256 "3773d2b4a55af854268b9ba34150aae281ede55618fdb7482f74b0e6156cf522"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v1.0.0-beta.50/trails-v1.0.0-beta.50-linux-x64.tar.gz"
      sha256 "77209ad6e87e50880e6269268e1153cd29bd5d83886f8165896c98d81114250f"
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
