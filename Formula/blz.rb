class Blz < Formula
  desc "Fast local search for llms.txt"
  homepage "https://blz.run"
  version "1.5.5"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  bottle do
    root_url "https://github.com/outfitter-dev/homebrew-tap/releases/download/blz-1.5.5"
    sha256 cellar: :any_skip_relocation, arm64_sequoia: "f1200ab4e81a375bfd9e65f6138445c1a016409bdfeea43be76bb064c89af8c2"
    sha256 cellar: :any_skip_relocation, x86_64_linux:  "b110146b5514aa328001044b09b7ff7fba9fcf6203c7ccfad8c6362068ba3967"
  end

  on_macos do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-arm64.tar.gz"
      sha256 "ad0bd95b75e414877da81d199c110a6fbeaded284949d676e66911fb795d3410"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-darwin-x64.tar.gz"
      sha256 "67a36c645375ac6bb2f2a0882c302f4238bbb3001625ba1ec232bf3f7201b1b5"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "c5945f7bd51b24bf9d21f43a1cf52b04d646cf1b386306b8802f02835e4972e9"
    end
    on_intel do
      url "https://github.com/outfitter-dev/blz/releases/download/v#{version}/blz-#{version}-linux-x64.tar.gz"
      sha256 "c5945f7bd51b24bf9d21f43a1cf52b04d646cf1b386306b8802f02835e4972e9"
    end
  end

  def install
    if OS.linux? && Hardware::CPU.arm?
      odie "The blz Linux arm64 binary is not available yet. Please use the x86_64 build."
    end
    bin.install "blz"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/blz --version")
    assert_match "blz", shell_output("#{bin}/blz --help")
  end
end
