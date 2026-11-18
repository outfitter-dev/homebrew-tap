class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.31.0/skillset-v0.31.0-darwin-arm64.tar.gz"
  sha256 "072c929b56b98743a51bbdc381065a752383534c87f4e07d0e4397cf32c5b713"
  license "MIT"
  depends_on :macos

  on_macos do
    on_intel do
      url "https://github.com/outfitter-dev/skillset/releases/download/v0.31.0/skillset-v0.31.0-darwin-x64.tar.gz"
      sha256 "96f48b296c1c417d2b6b15ce96ddb8379c3b5c7ce688e9219bddc0f714125aef"
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
