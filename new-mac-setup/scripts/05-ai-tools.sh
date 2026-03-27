#!/bin/bash
# =============================================================================
# SWYX 2025 NEW MAC SETUP — STEP 5: AI & ML Tools
# =============================================================================

set -e

echo "🤖 SWYX NEW MAC SETUP — Step 5: AI & ML Tools"
echo "================================================"
echo ""

eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true
eval "$(fnm env --use-on-cd)" 2>/dev/null || true

# =============================================================================
# CLAUDE CODE
# =============================================================================
echo "📦 Installing Claude Code..."
if command -v claude &>/dev/null; then
    echo "   ✅ Claude Code already installed"
else
    npm install -g @anthropic-ai/claude-code
    echo "   ✅ Claude Code installed"
fi

# Add Playwright MCP to Claude Code
echo "   📦 Adding Playwright MCP to Claude Code..."
claude mcp add playwright -- npx -y @playwright/mcp@latest 2>/dev/null || echo "   ⚠️  Playwright MCP setup skipped (run manually later)"

# =============================================================================
# GEMINI CLI
# =============================================================================
echo ""
echo "📦 Installing Gemini CLI..."
if command -v gemini &>/dev/null; then
    echo "   ✅ Gemini CLI already installed"
else
    npm install -g @anthropic-ai/claude-code 2>/dev/null || true
    # Gemini CLI install (check latest method)
    npx -y @anthropic-ai/claude-code 2>/dev/null || true
    echo "   💡 Install Gemini CLI manually: npm install -g @google/gemini-cli"
fi

# =============================================================================
# OPENAI CODEX
# =============================================================================
echo ""
echo "📦 Installing OpenAI Codex CLI..."
npm i -g @openai/codex 2>/dev/null || echo "   ⚠️  OpenAI Codex install skipped"

# =============================================================================
# OLLAMA — Local AI Models
# =============================================================================
echo ""
echo "📦 Setting up Ollama models..."

# Check if Ollama is running
if command -v ollama &>/dev/null; then
    echo "   ✅ Ollama installed"

    # Start Ollama if not running
    if ! pgrep -x "ollama" &>/dev/null; then
        echo "   🔄 Starting Ollama..."
        open -a Ollama 2>/dev/null || ollama serve &>/dev/null &
        sleep 3
    fi

    echo "   📦 Pulling models (this takes a while)..."
    echo "   📦 Pulling llama3.2..."
    ollama pull llama3.2 2>/dev/null || echo "      ⚠️  Failed (try: ollama pull llama3.2)"

    echo "   📦 Pulling qwen2.5-coder:14b..."
    ollama pull qwen2.5-coder:14b 2>/dev/null || echo "      ⚠️  Failed (try: ollama pull qwen2.5-coder:14b)"

    echo "   📦 Pulling deepseek-r1 distill..."
    ollama pull hf.co/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF:Q8_0 2>/dev/null || echo "      ⚠️  Failed (try manually)"
else
    echo "   ⚠️  Ollama not found — install via: brew install --cask ollama"
fi

# =============================================================================
# LLAMA.CPP (Local inference server)
# =============================================================================
echo ""
echo "📦 Installing llama.cpp..."
if command -v llama-server &>/dev/null; then
    echo "   ✅ llama.cpp already installed"
else
    brew install llama.cpp 2>/dev/null || echo "   ⚠️  llama.cpp install failed"
fi

echo ""
echo "✅ Step 5 complete! AI tools ready."
echo ""
echo "💡 Useful commands:"
echo "   ollama run llama3.2              # Chat with Llama"
echo "   ollama run qwen2.5-coder:14b     # Code with Qwen"
echo "   claude                            # Start Claude Code"
echo "   llama-server -hf ggml-org/Qwen2.5-Coder-3B-Q8_0-GGUF --port 8012 -ngl 99"
echo ""
echo "💡 Manual downloads:"
echo "   - ChatGPT Desktop: https://chat.openai.com/download"
echo "   - LM Studio: https://lmstudio.ai"
echo "   - Claude Desktop: https://claude.ai/download"
echo ""
echo "   Run ./06-dotfiles.sh next."
