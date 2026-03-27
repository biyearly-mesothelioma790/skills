#!/bin/bash
# =============================================================================
# SWYX 2025 NEW MAC SETUP — STEP 3: Homebrew Packages + Cask Apps
# NOTE: Warp removed. Using Ghostty + cmux instead.
# =============================================================================

set -e

echo "🍺 SWYX NEW MAC SETUP — Step 3: Homebrew Packages + Cask Apps"
echo "==============================================================="
echo ""

# Make sure Homebrew is available
eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true

# =============================================================================
# FORMULAE (CLI tools)
# =============================================================================
echo "📦 Installing Homebrew formulae..."

FORMULAE=(
    # Core dev tools
    gh              # GitHub CLI
    git             # Latest git
    fnm             # Fast Node Manager (not nvm!)
    pnpm            # Fast npm alternative
    z               # Directory jumping
    diff-so-fancy   # Better git diffs

    # Languages & runtimes
    elixir
    erlang
    python@3.13

    # Docker without Docker Desktop
    colima
    docker
    docker-completion

    # Media & processing
    ffmpeg
    yt-dlp
    tesseract       # OCR engine

    # Build dependencies
    openssl@3
    readline
    sqlite
    xz
    zstd

    # Databases
    postgresql@14
    rabbitmq

    # Misc CLI
    honcho          # Process manager (Procfile)
    pipx            # Python CLI tool installer
    flyctl          # Fly.io CLI
    entr            # File watcher
    tig             # Git TUI

    # Claude-suggested modern CLI replacements
    fzf             # Fuzzy finder (Ctrl+R history, file search)
    ripgrep         # Fast grep replacement (rg)
    bat             # cat with syntax highlighting
    zoxide          # Smarter z/directory jumping

    # Libraries (needed by other packages)
    cairo
    glib
    harfbuzz
    libvmaf
    webp
)

for pkg in "${FORMULAE[@]}"; do
    # Skip comments
    [[ "$pkg" =~ ^#.*$ ]] && continue
    if brew list "$pkg" &>/dev/null; then
        echo "   ✅ $pkg already installed"
    else
        echo "   📦 Installing $pkg..."
        brew install "$pkg" 2>/dev/null || echo "   ⚠️  Failed to install $pkg (continuing...)"
    fi
done

# =============================================================================
# CASKS (GUI apps)
# =============================================================================
echo ""
echo "📦 Installing Homebrew cask apps..."

CASKS=(
    # Terminal — Ghostty + cmux (NOT Warp)
    ghostty

    # Editors
    cursor
    visual-studio-code

    # Browsers
    arc

    # Communication
    slack
    discord
    zoom

    # Productivity
    raycast
    rectangle
    obsidian
    notion

    # AI & ML
    ollama

    # Media
    vlc
    audacity
    loom
    descript

    # Utilities
    shottr           # Screenshots + OCR
    notunes          # Disable iTunes/Apple Music
    caffeine         # Keep Mac awake (or use Raycast Coffee plugin)
    stretchly        # Break reminders
    quickshade       # Brightness control
    pure-paste       # Clean clipboard
    1password

    # Dev tools
    beeper           # Unified messaging
    superhuman       # Email

    # Claude-suggested additions
    orbstack            # Lighter Docker alternative (even lighter than Colima)
)

for cask in "${CASKS[@]}"; do
    if brew list --cask "$cask" &>/dev/null; then
        echo "   ✅ $cask already installed"
    else
        echo "   📦 Installing $cask..."
        brew install --cask "$cask" 2>/dev/null || echo "   ⚠️  Failed to install $cask (continuing...)"
    fi
done

# =============================================================================
# CMUX — Ghostty-based terminal for AI agents
# =============================================================================
echo ""
echo "📦 Installing cmux (Ghostty-based terminal with vertical tabs)..."
brew tap manaflow-ai/cmux 2>/dev/null || true
if brew list --cask cmux &>/dev/null; then
    echo "   ✅ cmux already installed"
else
    brew install --cask cmux || echo "   ⚠️  Failed to install cmux"
fi

echo ""
echo "✅ Step 3 complete! All packages and apps installed."
echo ""
echo "💡 Apps that need manual download:"
echo "   - Wispr Flow: https://wispr.com"
echo "   - Windsurf: https://windsurf.com/download/editor"
echo "   - Screenflow 11: https://www.telestream.net/screenflow/"
echo "   - App Quitter: https://appquitter.com"
echo ""
echo "   Run ./04-dev-environment.sh next."
