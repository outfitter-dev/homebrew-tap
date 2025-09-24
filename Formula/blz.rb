class Blz < Formula
  desc "Fast local search for llms.txt"
  homepage "https://blz.run"
  license "Apache-2.0"
  version "0.3.2"

  livecheck do
    url "https://github.com/outfitter-dev/blz/releases/latest"
    strategy :github_latest
  end

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-arm64.tar.gz"
      sha256 "bd162a356c6733c9b32fff8b609c281235b5dd120d8ae3930f03a1ffd7e81508"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-x64.tar.gz"
      sha256 "8dde9dc99ad5a43ab5bd3356c56693a9a1c3665fcfc405c997dce9f9b5608acb"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "0d509792ba85ded816029447f62aaee121feebac800fb81ea7e5791bbcbf5c89"
    end
  end

  def install
    bin.install "blz"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/blz --version")
    assert_match "blz", shell_output("#{bin}/blz --help")
  end
end
