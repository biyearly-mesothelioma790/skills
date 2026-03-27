#!/bin/bash
# =============================================================================
# SWYX 2025 NEW MAC SETUP — STEP 7: macOS System Preferences
# These are the opinionated system settings from both blog posts
# =============================================================================

echo "🍎 SWYX NEW MAC SETUP — Step 7: macOS System Settings"
echo "======================================================="
echo ""

# =============================================================================
# FINDER
# =============================================================================
echo "📁 Configuring Finder..."

# Show filename extensions
defaults write NSGlobalDomain AppleShowAllExtensions -bool true

# Show hidden files (dotfiles) — also toggleable with Cmd+Shift+.
defaults write com.apple.finder AppleShowAllFiles -bool true

# Show path bar at bottom of Finder
defaults write com.apple.finder ShowPathbar -bool true

# Show status bar
defaults write com.apple.finder ShowStatusBar -bool true

# Default to list view
defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"

# New Finder windows open to home directory
defaults write com.apple.finder NewWindowTarget -string "PfHm"

echo "   ✅ Finder configured"

# =============================================================================
# DOCK
# =============================================================================
echo ""
echo "🚢 Configuring Dock..."

# Auto-hide the Dock
defaults write com.apple.dock autohide -bool true

# Remove auto-hide delay
defaults write com.apple.dock autohide-delay -float 0

# Speed up auto-hide animation
defaults write com.apple.dock autohide-time-modifier -float 0.3

# Minimize windows into their application icon
defaults write com.apple.dock minimize-to-application -bool true

# Don't show recent applications
defaults write com.apple.dock show-recents -bool false

echo "   ✅ Dock configured (manually remove all apps except Finder & Trash)"

# =============================================================================
# KEYBOARD
# =============================================================================
echo ""
echo "⌨️  Configuring Keyboard..."

# Disable auto-correct
defaults write NSGlobalDomain NSAutomaticSpellingCorrectionEnabled -bool false

# Disable auto-capitalization
defaults write NSGlobalDomain NSAutomaticCapitalizationEnabled -bool false

# Disable smart quotes and dashes (annoying for coding)
defaults write NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false
defaults write NSGlobalDomain NSAutomaticDashSubstitutionEnabled -bool false

# Fast key repeat rate
defaults write NSGlobalDomain KeyRepeat -int 2
defaults write NSGlobalDomain InitialKeyRepeat -int 15

# Disable press-and-hold for accent characters (enables key repeat)
defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool false

echo "   ✅ Keyboard configured"

# =============================================================================
# TRACKPAD
# =============================================================================
echo ""
echo "🖱️  Configuring Trackpad..."

# Disable "Natural" scrolling (swyx opinion: unnatural!)
defaults write NSGlobalDomain com.apple.swipescrolldirection -bool false

# Enable tap to click
defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking -bool true

echo "   ✅ Trackpad configured"

# =============================================================================
# SCREENSHOTS
# =============================================================================
echo ""
echo "📸 Configuring Screenshots..."

# Save screenshots to Desktop
defaults write com.apple.screencapture location -string "$HOME/Desktop"

# Save in PNG format
defaults write com.apple.screencapture type -string "png"

# Disable shadow in screenshots
defaults write com.apple.screencapture disable-shadow -bool true

echo "   ✅ Screenshots configured"
echo ""
echo "   💡 MANUAL: Remap screenshot shortcut to Cmd+E (System Settings → Keyboard → Shortcuts → Screenshots)"

# =============================================================================
# SPOTLIGHT
# =============================================================================
echo ""
echo "🔍 Spotlight..."
echo "   💡 MANUAL: Disable all Spotlight categories except:"
echo "     - Applications"
echo "     - System Preferences"
echo "   💡 MANUAL: Disable Siri"
echo "   💡 MANUAL: Disable 'Developer' in Spotlight if Xcode is installed"

# =============================================================================
# MENU BAR
# =============================================================================
echo ""
echo "📊 Configuring Menu Bar..."

# Auto-hide menu bar (2025 opinion)
defaults write NSGlobalDomain _HIHideMenuBar -bool true 2>/dev/null || true

echo "   ✅ Menu bar set to auto-hide"

# =============================================================================
# ACCESSIBILITY
# =============================================================================
echo ""
echo "♿ Accessibility..."
echo "   💡 MANUAL: Set cursor to large size (for presentations)"
echo "   ⚠️  Note: swyx reports potential memory leak with large cursor"

# =============================================================================
# CREATE WORK FOLDER
# =============================================================================
echo ""
echo "📂 Creating ~/Work folder..."
mkdir -p "$HOME/Work"
echo "   ✅ ~/Work created"
echo "   💡 MANUAL: Set Finder default window to ~/Work folder"

# =============================================================================
# APPLY CHANGES
# =============================================================================
echo ""
echo "🔄 Restarting affected apps..."
killall Finder 2>/dev/null || true
killall Dock 2>/dev/null || true
killall SystemUIServer 2>/dev/null || true

echo ""
echo "✅ Step 7 complete! Most settings applied."
echo ""
echo "⚠️  MANUAL STEPS REMAINING:"
echo "   1. Spotlight: Disable all except Apps + System Preferences"
echo "   2. Keyboard → Shortcuts: Set Cmd+E for screenshot to clipboard"
echo "   3. Keyboard: Disable Ask Siri"
echo "   4. Keyboard: Remap Cmd+Q (double-tap to quit, prevents accidental closes)"
echo "   5. Trackpad: Disable dictionary lookup (Look up & data detectors)"
echo "   6. Finder: Set new windows to show ~/Work"
echo "   7. Dock: Remove all icons except Finder and Trash"
echo "   8. Set cursor to large size in Accessibility → Display"
