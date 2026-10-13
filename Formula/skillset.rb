class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.28.0/skillset-v0.28.0-darwin-arm64.tar.gz"
  sha256 "be9e18b494d96c21f35b921f3617c7fe2f0a2ad0ebaf2a7ce7ef972717bf6d76"
  license "MIT"

  bottle do
    root_url "https://github.com/outfitter-dev/homebrew-tap/releases/download/skillset-0.28.0"
    sha256                               arm64_tahoe: "97153950a9d93d5aef674739ab470665f6fa55ab4c538d9966cc0cfdf3463fed"
    sha256 cellar: :any_skip_relocation, sequoia:     "ee2eb576d8cda876cdab8560c7d5878fd14a836cc668f7081e7e20e4d079e78d"
  end
  depends_on :macos

  on_macos do
    on_intel do
      url "https://github.com/outfitter-dev/skillset/releases/download/v0.28.0/skillset-v0.28.0-darwin-x64.tar.gz"
      sha256 "0bae528b92b9f1080ca8fdcf0741b3ebd9235d905bf91d7abb78daccac19b1cf"
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
