class Trails < Formula
  desc "Agent-native, contract-first TypeScript framework"
  homepage "https://github.com/outfitter-dev/trails"
  license "MIT"
  # Keep this scheme after the reset from 1.0.0-beta to 0.2.0.
  version_scheme 1

  depends_on "bun"

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.4/trails-v0.2.4-darwin-arm64.tar.gz"
      sha256 "aa3ed2e274c16e89e8de170d7239031c0c30bea17203749ac33a48e1b9f4266c"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.4/trails-v0.2.4-darwin-x64.tar.gz"
      sha256 "481892ddbce1a435a36dfdcb4fd155eeba5828654f3af3285996aa75b03aab82"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.4/trails-v0.2.4-linux-arm64.tar.gz"
      sha256 "b93641ecceadd2c274af5402d2517c06057d05ebc95dd0bd010c5d8aba27ddfb"
    end
    on_intel do
      url "https://github.com/outfitter-dev/trails/releases/download/v0.2.4/trails-v0.2.4-linux-x64.tar.gz"
      sha256 "839cef60aab98081231acfb318368aa63887c77496e3e66c7658a19789699289"
    end
  end

  def install
    libexec.install Dir["*"]
    bin.install_symlink libexec/"bin/trails"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/trails --version")
    assert_match "Usage: trails", shell_output("#{bin}/trails --help")
  end
end
