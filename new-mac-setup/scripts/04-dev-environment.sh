#!/bin/bash
# =============================================================================
# SWYX 2025 NEW MAC SETUP — STEP 4: Dev Environment (Node, Python, Git, Docker)
# =============================================================================

set -e

echo "🛠️  SWYX NEW MAC SETUP — Step 4: Dev Environment"
echo "=================================================="
echo ""

eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true

# =============================================================================
# GIT CONFIGURATION
# =============================================================================
echo "📝 Configuring Git..."

git config --global init.defaultBranch main
git config --global user.name "swyxio"
git config --global user.email "shawnthe1@gmail.com"
git config --global core.pager "diff-so-fancy | less --tabs=4 -RFX"
git config --global pull.rebase false

echo "   ✅ Git configured"

# =============================================================================
# SSH KEY
# =============================================================================
echo ""
if [ -f "$HOME/.ssh/id_ed25519" ]; then
    echo "✅ SSH key already exists"
else
    echo "🔑 Generating SSH key..."
    ssh-keygen -t ed25519 -C "shawnthe1@gmail.com" -f "$HOME/.ssh/id_ed25519" -N ""
    eval "$(ssh-agent -s)"
    ssh-add "$HOME/.ssh/id_ed25519"
    echo ""
    echo "📋 Your public key (add to GitHub → Settings → SSH Keys):"
    echo "---"
    cat "$HOME/.ssh/id_ed25519.pub"
    echo "---"
    echo ""
    echo "   Opening GitHub SSH settings page..."
    open "https://github.com/settings/ssh/new" 2>/dev/null || true
    echo "   Press ENTER once you've added the key to GitHub."
    read -r
fi

# =============================================================================
# GITHUB CLI
# =============================================================================
echo ""
if gh auth status &>/dev/null 2>&1; then
    echo "✅ GitHub CLI already authenticated"
else
    echo "🔐 Authenticating GitHub CLI..."
    gh auth login
fi

# =============================================================================
# NODE.JS (via fnm — NOT nvm)
# =============================================================================
echo ""
echo "📦 Setting up Node.js via fnm..."

# Make fnm available
eval "$(fnm env --use-on-cd)" 2>/dev/null || true

CURRENT_NODE=$(node --version 2>/dev/null || echo "none")
echo "   Current Node: $CURRENT_NODE"

if ! fnm list | grep -q "v22"; then
    echo "   📦 Installing Node 22 (LTS)..."
    fnm install 22
fi
fnm use 22
fnm default 22

echo "   ✅ Node $(node --version) active"

# npm config
npm config set loglevel="warn"

# Global packages
echo "   📦 Installing global npm packages..."
npm i -g undollar 2>/dev/null || true
npm i -g npm-check-updates 2>/dev/null || true
sudo npm i -g trash-cli 2>/dev/null || true

echo "   ✅ npm globals installed"

# npm login
echo ""
echo "💡 Run 'npm login' manually when ready."

# =============================================================================
# PYTHON (via uv from Astral — NOT pyenv/pip/conda)
# =============================================================================
echo ""
echo "🐍 Setting up Python via uv..."

if command -v uv &>/dev/null; then
    echo "   ✅ uv already installed"
else
    echo "   📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source "$HOME/.local/bin/env" 2>/dev/null || true
fi

# Install Python 3.12 (stable for ML work)
echo "   📦 Installing Python 3.12 via uv..."
uv python install 3.12 2>/dev/null || true

echo "   ✅ Python via uv ready"
echo "   Usage: uv venv && uv pip install <package>"

# =============================================================================
# DOCKER (via Colima — NOT Docker Desktop)
# =============================================================================
echo ""
echo "🐳 Setting up Docker via Colima..."

# Install docker-compose
if command -v docker-compose &>/dev/null; then
    echo "   ✅ docker-compose already installed"
else
    echo "   📦 Installing docker-compose..."
    sudo mkdir -p /usr/local/bin
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-darwin-aarch64" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "   ✅ Docker via Colima ready"
echo "   Usage: colima start && docker ps"

# =============================================================================
# YARN (without Node dependency from brew)
# =============================================================================
echo ""
echo "📦 Installing Yarn..."
brew install yarn --ignore-dependencies 2>/dev/null || echo "   yarn already installed or skipped"

echo ""
echo "✅ Step 4 complete! Dev environment ready."
echo "   Run ./05-ai-tools.sh next."
