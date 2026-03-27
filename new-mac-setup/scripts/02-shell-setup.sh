#!/bin/bash
# =============================================================================
# SWYX 2025 NEW MAC SETUP — STEP 2: Oh-My-ZSH + Plugins + Fonts
# =============================================================================

set -e

echo "🐚 SWYX NEW MAC SETUP — Step 2: Shell Setup"
echo "=============================================="
echo ""

# --- Oh-My-ZSH ---
if [ -d "$HOME/.oh-my-zsh" ]; then
    echo "✅ Oh-My-ZSH already installed"
else
    echo "📦 Installing Oh-My-ZSH..."
    sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# --- ZSH Plugins ---
ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

if [ -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
    echo "✅ zsh-autosuggestions already installed"
else
    echo "📦 Installing zsh-autosuggestions..."
    git clone https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
fi

if [ -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
    echo "✅ zsh-syntax-highlighting already installed"
else
    echo "📦 Installing zsh-syntax-highlighting..."
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
fi

# --- Powerlevel10k Theme ---
if [ -d "$ZSH_CUSTOM/themes/powerlevel10k" ]; then
    echo "✅ powerlevel10k already installed"
else
    echo "📦 Installing powerlevel10k theme..."
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$ZSH_CUSTOM/themes/powerlevel10k"
fi

# --- Powerline Fonts ---
echo ""
echo "📦 Installing Powerline fonts (Meslo LG M, Inconsolata)..."
FONT_DIR="$HOME/Library/Fonts"
mkdir -p "$FONT_DIR"

# Meslo LG M for Powerline (swyx's preferred font)
if ls "$FONT_DIR"/Meslo* &>/dev/null; then
    echo "✅ Meslo fonts already installed"
else
    curl -fsSL -o "$FONT_DIR/Meslo LG M Regular for Powerline.ttf" \
        "https://github.com/powerline/fonts/raw/master/Meslo%20Slashed/Meslo%20LG%20M%20Regular%20for%20Powerline.ttf"
    curl -fsSL -o "$FONT_DIR/Meslo LG M Bold for Powerline.ttf" \
        "https://github.com/powerline/fonts/raw/master/Meslo%20Slashed/Meslo%20LG%20M%20Bold%20for%20Powerline.ttf"
    echo "   ✅ Meslo LG M for Powerline installed"
fi

# Inconsolata for Powerline
if ls "$FONT_DIR"/Inconsolata*Powerline* &>/dev/null; then
    echo "✅ Inconsolata fonts already installed"
else
    curl -fsSL -o "$FONT_DIR/Inconsolata for Powerline.otf" \
        "https://github.com/powerline/fonts/raw/master/Inconsolata/Inconsolata%20for%20Powerline.otf"
    echo "   ✅ Inconsolata for Powerline installed"
fi

echo ""
echo "✅ Step 2 complete! Shell is ready."
echo "   Run ./03-brew-packages.sh next."
