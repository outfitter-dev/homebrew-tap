class Skillset < Formula
  desc "Source-first compiler for provider-native agent loadouts"
  homepage "https://github.com/outfitter-dev/skillset"
  url "https://github.com/outfitter-dev/skillset/releases/download/v0.29.0/skillset-v0.29.0-darwin-arm64.tar.gz"
  sha256 "cdc0005ba455a93feaa153cb8f303fc948d01a677a04f9a8b5e4e3df3003d939"
  license "MIT"

  bottle do
    root_url "https://github.com/outfitter-dev/homebrew-tap/releases/download/skillset-0.29.0"
    sha256                               arm64_tahoe: "41cf3909f7be13c4d9e107224e9c2949035707ae0acfa9f8d44137c0d2ce5581"
    sha256 cellar: :any_skip_relocation, sequoia:     "79c32839a4c47244688e5cec047ddc1958289c474ac1b20b616a31c4e2035920"
  end
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
