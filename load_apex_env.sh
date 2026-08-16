#!/usr/bin/env bash
# APEX Sovereign Supreme Unified System Environment & Memory Bridge
# Auto-loaded by ~/.bashrc on shell initialization across Crostini, PRoot Ubuntu, and Termux

export SUPABASE_URL="https://kjebemdgvjvuutzvhbtp.supabase.co"
export SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqZWJlbWRndmp2dXV0enZoYnRwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODE2ODUxNiwiZXhwIjoyMDgzNzQ0NTE2fQ.782ZXi7Q8AGhtT3iQViTjgimt0DrXFBIsxRJohq92qY"

export PYTHONPATH="$HOME/antigravity-cli:$HOME/computer-user:/root/antigravity-cli:/home/droid/antigravity-cli:$PYTHONPATH"
export PATH="$HOME/.local/bin:/home/droid/.local/bin:/root/.local/bin:$PATH"

# Always-On Core Skill Flags
export APEX_SKILL_ASPEN_GROVE="ALWAYS_ON"
export APEX_SKILL_TOKEN_SAVER="ALWAYS_ON"
export APEX_HEAVY_ARCHITECT_DEFAULT="gemini-3.5-pro"
export APEX_FAST_SWARM_DEFAULT="gemini-3.6-flash"

# Display auto-detect for Crostini (Sommelier), Termux-X11, and macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # On macOS, native Quartz/AppKit is used unless XQuartz is active
    if [ -e "/tmp/.X11-unix/X0" ]; then
        export DISPLAY=:0
    fi
elif [ -n "$WAYLAND_DISPLAY" ] || [ -e "/tmp/.X11-unix/X0" ]; then
    export DISPLAY=:0
elif [ -e "/tmp/.X11-unix/X1" ]; then
    export DISPLAY=:1
else
    export DISPLAY=:0
fi
