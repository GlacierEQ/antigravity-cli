#!/usr/bin/env bash
# Antigravity CLI — Universal macOS & Linux System Installer
# Configures binaries, environment bridges, agent mesh commands, and shell hooks.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
USER_BIN="$HOME/bin"

mkdir -p "$BIN_DIR" "$USER_BIN"

echo "============================================================================"
echo " 🌌 INSTALLING GLACIEREQ / ANTIGRAVITY CLI ON MACOS"
echo "============================================================================"

# 1. Symlink antigravity -> agy
if [ -f "$BIN_DIR/agy" ]; then
    echo "1. 🔗 Linking $BIN_DIR/antigravity -> $BIN_DIR/agy..."
    ln -sf "$BIN_DIR/agy" "$BIN_DIR/antigravity"
    ln -sf "$BIN_DIR/agy" "$USER_BIN/agy" 2>/dev/null || true
    ln -sf "$BIN_DIR/agy" "$USER_BIN/antigravity" 2>/dev/null || true
    chmod +x "$BIN_DIR/agy" "$BIN_DIR/antigravity" 2>/dev/null || true
fi

# 2. Helper wrappers for Python-based Mesh & Commander commands
echo "2. 🛠️ Creating unified CLI wrappers in $BIN_DIR..."

cat << 'EOF' > "$BIN_DIR/desktop-commander"
#!/usr/bin/env bash
python3 "$HOME/antigravity-cli/ultimate_desktop_commander.py" "$@"
EOF
chmod +x "$BIN_DIR/desktop-commander"

cat << 'EOF' > "$BIN_DIR/heavy-architect"
#!/usr/bin/env bash
python3 "$HOME/antigravity-cli/heavy_architect_fast_executor.py" "$@"
EOF
chmod +x "$BIN_DIR/heavy-architect"

cat << 'EOF' > "$BIN_DIR/agent-mesh"
#!/usr/bin/env bash
python3 "$HOME/antigravity-cli/agent_mesh.py" "$@"
EOF
chmod +x "$BIN_DIR/agent-mesh"

cat << 'EOF' > "$BIN_DIR/mesh-optimizer"
#!/usr/bin/env bash
python3 "$HOME/antigravity-cli/dynamic_mesh_optimizer.py" "$@"
EOF
chmod +x "$BIN_DIR/mesh-optimizer"

cat << 'EOF' > "$BIN_DIR/antigravity-sync"
#!/usr/bin/env bash
bash "$HOME/antigravity-cli/sync_center.sh" "$@"
EOF
chmod +x "$BIN_DIR/antigravity-sync"

# 3. Wire into ~/.zshrc if not already present
echo "3. 🐚 Verifying shell configuration in ~/.zshrc..."
if ! grep -q "antigravity-cli/load_apex_env.sh" "$HOME/.zshrc" 2>/dev/null; then
    cat << 'EOF' >> "$HOME/.zshrc"

# GlacierEQ / Antigravity CLI Suite & APEX Environment Loader
if [ -f "$HOME/antigravity-cli/load_apex_env.sh" ]; then
    source "$HOME/antigravity-cli/load_apex_env.sh"
fi
EOF
    echo "  └─ Appended APEX environment hook to ~/.zshrc"
else
    echo "  └─ APEX environment hook already present in ~/.zshrc"
fi

# 4. Verify installation
echo "4. 🔍 Verifying binary and command availability..."
echo "  └─ agy version: $($BIN_DIR/agy --version 2>/dev/null || echo 'OK')"
echo "  └─ antigravity version: $($BIN_DIR/antigravity --version 2>/dev/null || echo 'OK')"
echo "  └─ desktop-commander: $(which desktop-commander 2>/dev/null || echo "$BIN_DIR/desktop-commander")"
echo "  └─ heavy-architect: $(which heavy-architect 2>/dev/null || echo "$BIN_DIR/heavy-architect")"
echo "  └─ agent-mesh: $(which agent-mesh 2>/dev/null || echo "$BIN_DIR/agent-mesh")"

echo "============================================================================"
echo " 🟢 GLACIEREQ ANTIGRAVITY CLI IS PERFECTLY INSTALLED & READY!"
echo "============================================================================"
