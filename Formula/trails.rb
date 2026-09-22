class Trails < Formula
  desc "Agent-native, contract-first TypeScript framework"
  homepage "https://github.com/outfitter-dev/trails"
  license "MIT"
  # Keep this scheme after the reset from 1.0.0-beta to 0.2.0.
  version_scheme 1

  depends_on "bun"

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.3/trails-v0.2.3-darwin-arm64.tar.gz"
      sha256 "1914f6adf96ec8f595de4bfc235db2b21a3317b8eef48be07b19eeffab634f28"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.3/trails-v0.2.3-darwin-x64.tar.gz"
      sha256 "4dc50fabecec0ab9079148663c6402e03e4a2061f1c7870cb76fa6fe1fd82037"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.3/trails-v0.2.3-linux-arm64.tar.gz"
      sha256 "75d6ed36a770224dd4e847b5ef0d8c1b093ab9114ea5c3310c616bc36125a8a4"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.3/trails-v0.2.3-linux-x64.tar.gz"
      sha256 "3e96ac7503fe8bcfc9079b96e40f4befc179984fa6b578bf30e98f171ec2d1cb"
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
