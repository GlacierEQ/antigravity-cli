#!/usr/bin/env bash
# APEX Desktop Commander Launcher v2.0
# Multi-OS Surface Orchestrator for Crostini (Sommelier), PRoot Ubuntu, and Termux-X11

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR:$HOME:$PYTHONPATH"

echo "============================================================================"
echo " 🖥️ APEX ULTIMATE DESKTOP COMMANDER v2.0 ACTIVATION"
echo "============================================================================"

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

echo "1. 🚀 Activating Supreme Desktop Commander Mode..."
python3 "$SCRIPT_DIR/ultimate_desktop_commander.py" --activate-supreme

echo "============================================================================"
echo " ✨ DESKTOP COMMANDER ONLINE & SUPREME IN CROSTINI!"
echo "============================================================================"
