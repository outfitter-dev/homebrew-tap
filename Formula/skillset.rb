class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.26.1/skillset-v0.26.1-darwin-arm64.tar.gz"
  sha256 "6a4540121c16486b8f52e2fb3809077e7292915f52e6a8172e4449d10de70251"
  license "MIT"
  depends_on :macos

  on_macos do
    on_intel do
      url "https://github.com/outfitter-dev/skillset/releases/download/v0.26.1/skillset-v0.26.1-darwin-x64.tar.gz"
      sha256 "146e662505c15f9f0d77c4d8ae576d3aa6a3198a70d1c7e5b972f078de38bfe4"
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
