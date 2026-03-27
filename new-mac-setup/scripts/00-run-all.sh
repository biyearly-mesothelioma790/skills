#!/bin/bash
# =============================================================================
# SWYX 2025 NEW MAC SETUP — MASTER RUNNER
# Run this to execute all setup steps in order.
# Terminal: Ghostty + cmux (NO Warp)
# =============================================================================

# Don't use set -e so one script failure doesn't kill the whole pipeline
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Source tools into this shell so subscripts inherit them
eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true
eval "$(fnm env --use-on-cd)" 2>/dev/null || true

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          SWYX 2025 NEW MAC SETUP — MASTER RUNNER            ║"
echo "║                                                              ║"
echo "║  M4 Pro MacBook Pro, 14\", 24GB RAM                          ║"
echo "║  Terminal: Ghostty + cmux (Warp-free)                        ║"
echo "║  Based on: swyx.io/new-mac-setup (2024 + 2025)              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "This will run all 7 setup scripts in order."
echo "Some steps require user interaction (SSH keys, GitHub auth)."
echo ""
echo "Press ENTER to start, or Ctrl+C to cancel."
read -r

STEPS=(
    "01-xcode-and-homebrew.sh"
    "02-shell-setup.sh"
    "03-brew-packages.sh"
    "04-dev-environment.sh"
    "05-ai-tools.sh"
    "06-dotfiles.sh"
    "07-macos-settings.sh"
)

for step in "${STEPS[@]}"; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Running: $step"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    bash "$SCRIPT_DIR/$step"
    echo ""
    echo "  ✅ $step finished!"
    echo ""
done

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎉 ALL DONE! 🎉                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "NEXT STEPS (manual):"
echo ""
echo "1. Open Arc Browser and install extensions"
echo "   (uBlock Origin, Video Speed Controller, Refined GitHub, etc.)"
echo ""
echo "2. Open Ghostty or cmux as your terminal"
echo "   Run: p10k configure  (to set up powerlevel10k theme)"
echo ""
echo "3. Open Raycast and configure:"
echo "   - Clipboard history"
echo "   - Window management"
echo "   - Coffee plugin (replaces Caffeine)"
echo ""
echo "4. Download manually:"
echo "   - Wispr Flow: https://wispr.com"
echo "   - Cursor: https://cursor.com"
echo "   - Screenflow 11: https://www.telestream.net/screenflow/"
echo "   - App Quitter: https://appquitter.com"
echo "   - Clipbook: https://clipbook.app"
echo ""
echo "5. System Settings → Spotlight → disable all except Apps"
echo ""
echo "6. Set Ghostty/cmux as default terminal app"
echo ""
echo "7. Grant screen recording permissions:"
echo "   Create a Google Meet call to trigger the dialog"
echo ""
echo "Restart your terminal or run: source ~/.zshrc"
