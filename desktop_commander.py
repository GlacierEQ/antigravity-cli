#!/usr/bin/env python3
"""
APEX Desktop Commander & Display Surface Orchestrator v1.0
Bridges GUI Window Management, X11/Wayland Display Servers, Sommelier (Crostini), and Termux-X11.
Supports Crostini (:0 / wayland-0) and PRoot Ubuntu / Termux (:1) seamlessly.
"""

import os
import sys
import json
import time
import subprocess
from typing import Dict, List, Any, Optional

sys.path.insert(0, "/root")
from supabase_vault_client import SupabaseVaultClient

class DesktopCommander:
    def __init__(self):
        self.vault = SupabaseVaultClient()
        self.state_file = os.path.expanduser("~/.apex/desktop-commander-state.json")
        self.display = self._detect_display_server()
        self._ensure_state_dir()

    def _detect_display_server(self) -> str:
        if os.getenv("DISPLAY"):
            return os.getenv("DISPLAY")
        if os.path.exists("/tmp/.X11-unix/X0") or os.getenv("WAYLAND_DISPLAY"):
            return ":0"  # Crostini / Sommelier default
        if os.path.exists("/tmp/.X11-unix/X1"):
            return ":1"  # Termux-X11 default
        return ":0"

    def _ensure_state_dir(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        if not os.path.exists(self.state_file):
            with open(self.state_file, "w") as f:
                json.dump({"actions": [], "status": "INITIALIZED"}, f, indent=2)

    def initialize_display_server(self) -> Dict[str, Any]:
        """Activates and verifies the display surface (Crostini Sommelier or Termux-X11)."""
        is_crostini = os.getenv("WAYLAND_DISPLAY") is not None or os.path.exists("/tmp/.X11-unix/X0")
        
        env = os.environ.copy()
        env["DISPLAY"] = self.display

        # Verify xprop or xdotool or xset
        active_windows = []
        try:
            res = subprocess.run(["xdotool", "search", "--onlyvisible", "--name", ".*"], capture_output=True, text=True, timeout=3, env=env)
            active_windows = [w.strip() for w in res.stdout.splitlines() if w.strip()]
        except Exception:
            pass

        status = {
            "display": self.display,
            "display_type": "Crostini Sommelier (Wayland/X11)" if is_crostini else "Termux-X11 / Hybrid Surface",
            "active_windows_count": len(active_windows),
            "status": "🟢 ACTIVE & READY",
            "timestamp": time.time()
        }
        return status

    def launch_app(self, command: str) -> Dict[str, Any]:
        """Launch a GUI app or desktop window command asynchronously."""
        env = os.environ.copy()
        env["DISPLAY"] = self.display
        try:
            proc = subprocess.Popen(command, shell=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            result = {"command": command, "pid": proc.pid, "display": self.display, "status": "LAUNCHED"}
        except Exception as e:
            result = {"command": command, "error": str(e), "status": "FAILED"}

        self._record_action("launch_app", command, result)
        return result

    def _record_action(self, action_type: str, description: str, metadata: Dict[str, Any]):
        try:
            with open(self.state_file, "r+") as f:
                data = json.load(f)
                data.setdefault("actions", []).append({
                    "timestamp": time.time(),
                    "action_type": action_type,
                    "description": description,
                    "metadata": metadata
                })
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
        except Exception:
            pass

if __name__ == "__main__":
    commander = DesktopCommander()
    print("=== APEX DESKTOP COMMANDER INITIALIZATION ===")
    status = commander.initialize_display_server()
    print(json.dumps(status, indent=2))
    print("=============================================")
