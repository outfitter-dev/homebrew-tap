class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.26.1/skillset-v0.26.1-darwin-arm64.tar.gz"
  sha256 "6a4540121c16486b8f52e2fb3809077e7292915f52e6a8172e4449d10de70251"
  license "MIT"

  bottle do
    root_url "https://github.com/outfitter-dev/homebrew-tap/releases/download/skillset-0.26.1"
    sha256                               arm64_tahoe: "69b06dd01cc5ce8f519a51fe1fe8bc8aa6c31417049ec5f19a7de81ac1a9026c"
    sha256 cellar: :any_skip_relocation, sequoia:     "afa632c88467fa7181e8794770cfd5d293122f9ca952ba1df7971224a7af3b6f"
  end
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
