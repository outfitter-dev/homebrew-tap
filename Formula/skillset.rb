class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.26.0/skillset-v0.26.0-darwin-arm64.tar.gz"
  sha256 "72199a67ffb8b881e17dba622ff1b88af2d2e5fcd959a9867e75d4a352314537"
  license "MIT"

  bottle do
    root_url "https://github.com/outfitter-dev/homebrew-tap/releases/download/skillset-0.26.0"
    sha256                               arm64_tahoe: "efb07af5607894c2b38b07c903f1d82e84c3909c704328cb1f4f9cc924ed93d3"
    sha256 cellar: :any_skip_relocation, sequoia:     "4a3dd351957850ffb8a36299311db0c0e1cbe3f3f45370af3f5f70b6cc907c30"
  end
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
