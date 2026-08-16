#!/usr/bin/env bash
# Antigravity CLI Launcher Installer v1.0
# Creates the global 'agy' command line executable in ~/.local/bin/agy or /usr/local/bin/agy

set -e

TARGET_DIR="$HOME/.local/bin"
mkdir -p "$TARGET_DIR"

AGY_BIN="$TARGET_DIR/agy"

cat << 'EOF' > "$AGY_BIN"
#!/usr/bin/env bash
# Antigravity CLI Universal Launcher
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHONPATH="$HOME/antigravity-cli:$HOME/computer-user:$PYTHONPATH" python3 -m antigravity "$@" 2>/dev/null || npx -y @google/gemini-cli@latest "$@"
EOF

chmod +x "$AGY_BIN"

echo "🟢 Antigravity CLI binary installed to: $AGY_BIN"
echo "  └─ Simply type 'agy' in your terminal to start!"
