class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.30.0/skillset-v0.30.0-darwin-arm64.tar.gz"
  sha256 "182b8001c5b91d393831d0960942ae35c38fb1191f12de53b726c7ee85cd963b"
  license "MIT"
  depends_on :macos

  on_macos do
    on_intel do
      url "https://github.com/outfitter-dev/skillset/releases/download/v0.30.0/skillset-v0.30.0-darwin-x64.tar.gz"
      sha256 "814bb3b78d8daa362dc4df6590ba4eea5f71380f5d2f59cdf06f1837fa55ede5"
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
