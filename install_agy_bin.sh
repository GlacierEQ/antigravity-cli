#!/usr/bin/env bash
# Antigravity CLI Universal Launcher Installer v1.1
# Creates the global 'agy' command-line executable in ~/.local/bin/agy

set -e

TARGET_DIR="$HOME/.local/bin"
mkdir -p "$TARGET_DIR"

AGY_BIN="$TARGET_DIR/agy"

cat << 'EOF' > "$AGY_BIN"
#!/usr/bin/env bash
# Antigravity Universal CLI Launcher v1.1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CENTER_DIR="$HOME/antigravity-cli"

if [ -f "$CENTER_DIR/sync_center.sh" ] && [ "$1" == "--sync" ]; then
    exec "$CENTER_DIR/sync_center.sh"
fi

if [ -f "$CENTER_DIR/agent_mesh.py" ] && [ "$1" == "--mesh" ]; then
    shift
    exec python3 "$CENTER_DIR/agent_mesh.py" "$@"
fi

if command -v npx >/dev/null 2>&1; then
    exec npx -y @google/gemini-cli@latest "$@"
elif command -v python3 >/dev/null 2>&1; then
    export PYTHONPATH="$HOME/antigravity-cli:$HOME/computer-user:$PYTHONPATH"
    exec python3 -m antigravity "$@"
else
    echo "Error: Neither npx nor python3 found in PATH."
    exit 1
fi
EOF

chmod +x "$AGY_BIN"

# Remove any broken legacy agy.va39 references
rm -f "$TARGET_DIR/agy.va39"

echo "🟢 Antigravity CLI launcher installed to: $AGY_BIN"
echo "  └─ Simply type 'agy' in your terminal to launch!"
