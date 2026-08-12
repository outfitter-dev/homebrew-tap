class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.23.0/skillset-v0.23.0-darwin-arm64.tar.gz"
  sha256 "ca3f01a956fb5b337c417da71473a00016d7e75b4d3ac01ed453182b542bc70d"
  license "MIT"
  depends_on :macos

  on_macos do
    on_intel do
      url "https://github.com/outfitter-dev/skillset/releases/download/v0.23.0/skillset-v0.23.0-darwin-x64.tar.gz"
      sha256 "ed1aec8abc83a0ce50bc9c278bb8659f3a73a47101f1e2366dd4e6fb10eab964"
    end
  end

  def install
    bin.install "skillset"
  end

  test do
    assert_equal version.to_s, shell_output("#{bin}/skillset --version").strip
    output = shell_output("#{bin}/skillset lookup workspace --json")
    assert_match "\"command\":\"lookup\"", output
    assert_match "\"ok\":true", output
  end
end
