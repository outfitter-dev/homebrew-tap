class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.26.0/skillset-v0.26.0-darwin-arm64.tar.gz"
  sha256 "72199a67ffb8b881e17dba622ff1b88af2d2e5fcd959a9867e75d4a352314537"
  license "MIT"
  depends_on :macos

  on_macos do
    on_intel do
      url "https://github.com/outfitter-dev/skillset/releases/download/v0.26.0/skillset-v0.26.0-darwin-x64.tar.gz"
      sha256 "abcbb11747fa2eeaeb943b97da02879e649a23f14f0f47f5a8c60bd622c8035b"
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
