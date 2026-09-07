class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.25.0/skillset-v0.25.0-darwin-arm64.tar.gz"
  sha256 "d6d9d8a68b5fffa666335d8df793a7bc0c612421892d346cf9e397b1418e3d0b"
  license "MIT"

  bottle do
    root_url "https://github.com/outfitter-dev/homebrew-tap/releases/download/skillset-0.25.0"
    sha256                               arm64_tahoe: "b7cd68a5381139782d38bc0149b8fce6260101b17d4bbbecef7d0357a3eca18a"
    sha256 cellar: :any_skip_relocation, sequoia:     "24aaa87483f1caf428615b56599d9e18a1878fd5fef3b38e69f28b162084cbba"
  end
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
