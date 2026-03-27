#!/bin/bash
# =============================================================================
# SWYX 2025 NEW MAC SETUP — STEP 1: Xcode CLI Tools + Homebrew
# This takes 15-25 minutes. Run this first!
# =============================================================================

set -e

echo "🔧 SWYX NEW MAC SETUP — Step 1: Xcode CLI Tools + Homebrew"
echo "============================================================"
echo ""

# --- Xcode Command Line Tools ---
if xcode-select -p &>/dev/null; then
    echo "✅ Xcode Command Line Tools already installed"
else
    echo "📦 Installing Xcode Command Line Tools (15-25 min)..."
    xcode-select --install
    echo ""
    echo "⏳ A dialog should have appeared. Click 'Install' and wait."
    echo "   Press ENTER here once the installation finishes."
    read -r
fi

# --- Homebrew ---
if command -v brew &>/dev/null; then
    echo "✅ Homebrew already installed"
else
    echo "🍺 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add to PATH for Apple Silicon
    echo '' >> "$HOME/.zprofile"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

echo ""
echo "✅ Step 1 complete! Homebrew version: $(brew --version | head -1)"
echo "   Run ./02-shell-setup.sh next."
