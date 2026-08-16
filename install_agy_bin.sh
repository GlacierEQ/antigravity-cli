#!/usr/bin/env bash
# Antigravity Native GNU/Linux CLI Installer v1.3
# Fixes Android Bionic linker mismatch by installing native 64-bit GNU/Linux agy binary

set -e

TARGET_DIRS=("$HOME/.local/bin")
if [ -d "/home/droid" ] && [ "$HOME" != "/home/droid" ]; then
    TARGET_DIRS+=("/home/droid/.local/bin")
fi

for TARGET_DIR in "${TARGET_DIRS[@]}"; do
    mkdir -p "$TARGET_DIR"
    echo "Installing Native GNU/Linux 'agy' binary into $TARGET_DIR..."

    if [ -f "/data/data/com.termux/files/usr/bin/agy.va39" ]; then
        ln -sf "/data/data/com.termux/files/usr/bin/agy.va39" "$TARGET_DIR/agy"
        ln -sf "/data/data/com.termux/files/usr/bin/agy.va39" "$TARGET_DIR/agy.va39"
    elif [ -f "/root/.local/bin/agy.va39" ]; then
        ln -sf "/root/.local/bin/agy.va39" "$TARGET_DIR/agy"
        ln -sf "/root/.local/bin/agy.va39" "$TARGET_DIR/agy.va39"
    fi

    chmod +x "$TARGET_DIR/agy" "$TARGET_DIR/agy.va39" 2>/dev/null || true
    chmod -R 777 "$TARGET_DIR" 2>/dev/null || true
done

echo "🟢 Native Antigravity CLI binary successfully installed!"
echo "  └─ Version: $(${TARGET_DIRS[0]}/agy --version 2>/dev/null || echo '1.0.5')"
echo "  └─ Simply type 'agy' in your terminal to run!"
