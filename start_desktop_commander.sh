#!/usr/bin/env bash
# APEX Desktop Commander Launcher for Crostini & Termux

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR:$HOME:$PYTHONPATH"

echo "============================================================================"
echo " 🖥️ APEX DESKTOP COMMANDER ACTIVATION ENGINE"
echo "============================================================================"

# Auto-detect display
if [ -n "$WAYLAND_DISPLAY" ] || [ -e "/tmp/.X11-unix/X0" ]; then
    export DISPLAY=:0
    echo "🟢 Crostini Sommelier Display Server Detected (DISPLAY=:0)"
elif [ -e "/tmp/.X11-unix/X1" ]; then
    export DISPLAY=:1
    echo "🟢 Termux-X11 Server Detected (DISPLAY=:1)"
else
    export DISPLAY=:0
    echo "🟢 Standard Display Default Set (DISPLAY=:0)"
fi

echo "1. 🚀 Activating Desktop Commander Surface Services..."
python3 "$SCRIPT_DIR/desktop_commander.py"

echo "============================================================================"
echo " ✨ DESKTOP COMMANDER ONLINE & READY IN CROSTINI / HYBRID SURFACE!"
echo "============================================================================"
