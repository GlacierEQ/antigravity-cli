#!/usr/bin/env bash
# APEX Sovereign Supreme Unified System Environment & Memory Bridge
# Auto-loaded by ~/.bashrc on shell initialization across Crostini, PRoot Ubuntu, and Termux

export SUPABASE_URL="https://kjebemdgvjvuutzvhbtp.supabase.co"
export SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqZWJlbWRndmp2dXV0enZoYnRwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODE2ODUxNiwiZXhwIjoyMDgzNzQ0NTE2fQ.782ZXi7Q8AGhtT3iQViTjgimt0DrXFBIsxRJohq92qY"

export PYTHONPATH="$HOME/antigravity-cli:$HOME/computer-user:/root/antigravity-cli:/home/droid/antigravity-cli:$PYTHONPATH"
export PATH="$HOME/.local/bin:/home/droid/.local/bin:/root/.local/bin:$PATH"

# Verified Free Tier AI Provider Keys
export GROQ_API_KEY="REDACTED_GROQ_KEY_IN_VAULT"
export GROQ_API_KEY_ALT="REDACTED_GROQ_KEY_IN_VAULT"
export OPENROUTER_API_KEY="REDACTED_OPENROUTER_KEY_IN_VAULT"
export OPENROUTER_TOKEN="REDACTED_OPENROUTER_KEY_IN_VAULT"

export GOOGLE_API_KEY="AIzaSyD0qRv23tC0WgjzasodSAqfkfH02N2wp3k"
export GEMINI_API_KEY="AIzaSyD0qRv23tC0WgjzasodSAqfkfH02N2wp3k"
export GLACIER_GOOGLE_KEY_2="AIzaSyD0qRv23tC0WgjzasodSAqfkfH02N2wp3k"
export MISTRAL_API_KEY="REDACTED_MISTRAL_KEY_IN_VAULT"
export CEREBRAS_API_KEY="csk-phd85kkr948hch52nc9ntc5myt36my4y53vx4wnmntknd6yj"
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

# APEX Tri-Pillar Convergence Daemon Autostart
if [ -x /root/.apex/launch_mega_convergence.sh ]; then
    /root/.apex/launch_mega_convergence.sh >/dev/null 2>&1 || true
fi
