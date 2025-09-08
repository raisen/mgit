#!/bin/bash
# mgit macOS setup script
# This script helps set up mgit on macOS by removing quarantine attributes
# and making the executable available system-wide

set -e

echo "🔧 Setting up mgit for macOS..."

# Check if executable exists
if [ ! -f "./mgit-macos" ]; then
    echo "❌ Error: mgit-macos executable not found in current directory"
    echo "Please download mgit-macos from the GitHub releases first"
    exit 1
fi

# Remove quarantine attribute
echo "🛡️  Removing macOS quarantine attribute..."
xattr -d com.apple.quarantine ./mgit-macos 2>/dev/null || echo "ℹ️  No quarantine attribute found (this is normal)"

# Make executable
echo "⚙️  Making executable..."
chmod +x ./mgit-macos

# Try multiple methods to bypass Gatekeeper
echo "🔓 Attempting to bypass Gatekeeper..."

# Method 1: Remove quarantine with sudo
echo "   Removing quarantine with sudo..."
sudo xattr -d com.apple.quarantine ./mgit-macos 2>/dev/null || echo "   ℹ️  No quarantine attribute found"

# Method 2: Copy to /usr/local/bin (most reliable)
echo "   Copying to /usr/local/bin..."
if sudo cp ./mgit-macos /usr/local/bin/mgit 2>/dev/null; then
    sudo chmod +x /usr/local/bin/mgit
    echo "   ✅ Successfully copied to /usr/local/bin"
    echo "   You can now run 'mgit' from anywhere!"
else
    echo "   ⚠️  Could not copy to /usr/local/bin"
fi

# Test the executable
echo "🧪 Testing executable..."
if ./mgit-macos --help >/dev/null 2>&1; then
    echo "✅ Setup complete! mgit is ready to use."
    echo ""
    echo "Usage:"
    echo "  ./mgit-macos --help"
    echo "  ./mgit-macos status"
    echo ""
    echo "To make it available system-wide, you can:"
    echo "  sudo cp ./mgit-macos /usr/local/bin/mgit"
    echo "  # or add it to your PATH"
else
    echo "❌ Executable test failed"
    echo ""
    echo "🔧 Alternative: Copy to /usr/local/bin (often works!)"
    echo "sudo cp ./mgit-macos /usr/local/bin/mgit"
    echo "sudo chmod +x /usr/local/bin/mgit"
    echo "mgit --help  # Should work from anywhere"
    echo ""
    echo "🔧 Other troubleshooting options:"
    echo "1. Go to System Settings → Privacy & Security → Allow 'mgit-macos'"
    echo "2. Build locally: git clone && make build"
    exit 1
fi