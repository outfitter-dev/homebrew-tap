class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.29.0/skillset-v0.29.0-darwin-arm64.tar.gz"
  sha256 "cdc0005ba455a93feaa153cb8f303fc948d01a677a04f9a8b5e4e3df3003d939"
  license "MIT"
  depends_on :macos

  on_macos do
    on_intel do
      url "https://github.com/outfitter-dev/skillset/releases/download/v0.29.0/skillset-v0.29.0-darwin-x64.tar.gz"
      sha256 "0c85fabf9bbcd75e98b597cddbc6300cf0d871881c977bcbdcfb5225a62e2cd3"
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
