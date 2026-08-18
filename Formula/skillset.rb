class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.24.0/skillset-v0.24.0-darwin-arm64.tar.gz"
  sha256 "cc4968136780ca77f4a9598d03d15e1f9dbffd67f0a7d87b6af2059f21160f6b"
  license "MIT"
  depends_on :macos

  on_macos do
    on_intel do
      url "https://github.com/outfitter-dev/skillset/releases/download/v0.24.0/skillset-v0.24.0-darwin-x64.tar.gz"
      sha256 "1ec9500895b8c5c04f9122e431a3793fedb6ebd18f906d44bb29575744609c76"
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
