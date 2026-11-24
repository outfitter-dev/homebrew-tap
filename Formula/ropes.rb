class Ropes < Formula
  class LinuxX64Sse42Requirement < Requirement
    fatal true

    satisfy(build_env: false) { Hardware::CPU.sse4_2? }

    def message
      "The Ropes Linux x64 executable requires a CPU with SSE4.2 support."
    end
  end

  desc "Repository quality checks, tool configuration, and shared presets"
  homepage "https://github.com/outfitter-dev/ropes"
  url "https://github.com/outfitter-dev/ropes/releases/download/v0.1.0-canary.4/ropes-0.1.0-canary.4-darwin-arm64.tar.gz"
  version "0.1.0-canary.4"
  sha256 "30366f3d1cec02ca62d1dac8543980c253a67a2c31b17ae3a95ddf7d8427d704"
  license "MIT"

  on_macos do
    depends_on arch: :arm64

    on_arm do
      depends_on "rumdl" => :test
    end
  end

  on_linux do
    depends_on "rumdl" => :test

    on_arm do
      url "https://github.com/outfitter-dev/ropes/releases/download/v0.1.0-canary.4/ropes-0.1.0-canary.4-linux-arm64.tar.gz"
      sha256 "3b41f7211e79bcfb190213bf81046685223bea911f7edd39086749f82ee348f1"
    end
    on_intel do
      url "https://github.com/outfitter-dev/ropes/releases/download/v0.1.0-canary.4/ropes-0.1.0-canary.4-linux-x64.tar.gz"
      sha256 "4081564a29daadc0dbc13d65834a647554c433cda3cdcfc130a1e105e01ec406"
      depends_on LinuxX64Sse42Requirement
    end
  end

  def install
    bin.install "rope"
  end

  test do
    ENV["PATH"] = [formula_opt_bin("rumdl"), "/usr/bin", "/bin"].join(File::PATH_SEPARATOR)
    refute Utils.which("bun")
    assert_equal "rope #{version} (binary)", shell_output("#{bin}/rope --version").strip

    (testpath/"README.md").write "# Ropes smoke test\n\nThis Markdown file passes its checks.\n"
    system "git", "init", "--quiet"
    system "git", "add", "README.md"
    system "git", "-c", "user.name=Homebrew", "-c", "user.email=homebrew@example.com",
           "commit", "--quiet", "--message", "Seed fixture"
    system bin/"rope", "init", "--yes"

    result = JSON.parse(shell_output("#{bin}/rope check README.md --json"))
    assert_equal "clean", result.fetch("outcome")
    assert_equal ["passed"], result.fetch("steps").filter_map { |step| step["status"] if step["adapter"] == "rumdl" }
  end
end
