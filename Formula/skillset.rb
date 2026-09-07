class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.25.0/skillset-v0.25.0-darwin-arm64.tar.gz"
  sha256 "d6d9d8a68b5fffa666335d8df793a7bc0c612421892d346cf9e397b1418e3d0b"
  license "MIT"
  depends_on :macos

  on_macos do
    on_intel do
      url "https://github.com/outfitter-dev/skillset/releases/download/v0.25.0/skillset-v0.25.0-darwin-x64.tar.gz"
      sha256 "49ea21e462eeec25f3bc8679a2e466eb3fb3dd309d51e310b67758a9d245ddc7"
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
