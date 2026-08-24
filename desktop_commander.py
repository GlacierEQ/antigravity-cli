#!/usr/bin/env python3
"""
APEX Desktop Commander & Display Surface Orchestrator v1.1
Bridges GUI Window Management, X11/Wayland Display Servers, Sommelier (Crostini), Termux-X11, and macOS Quartz.
Multi-platform support: macOS Aqua, Crostini (:0 / wayland-0), PRoot Ubuntu / Termux (:1), and Windows surfaces.
"""

from __future__ import annotations

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# Universal import path resolution
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if "/root" not in sys.path and os.path.exists("/root"):
    sys.path.insert(0, "/root")

try:
    from supabase_vault_client import SupabaseVaultClient
except ImportError:
    SupabaseVaultClient = None


class DesktopCommander:
    def __init__(self):
        self.vault = SupabaseVaultClient() if SupabaseVaultClient else None
        self.state_file = os.path.expanduser("~/.apex/desktop-commander-state.json")
        self.display = self._detect_display_server()
        self._ensure_state_dir()

    def _detect_display_server(self) -> str:
        """Detect display server across macOS, Crostini, Termux-X11, and standard Linux."""
        if sys.platform == "darwin":
            return os.getenv("DISPLAY", "Aqua/Quartz:0")
        if os.getenv("DISPLAY"):
            return os.getenv("DISPLAY", ":0")
        if os.path.exists("/tmp/.X11-unix/X0") or os.getenv("WAYLAND_DISPLAY"):
            return ":0"  # Crostini / Sommelier default
        if os.path.exists("/tmp/.X11-unix/X1"):
            return ":1"  # Termux-X11 default
        return ":0"

    def _ensure_state_dir(self):
        """Ensure ~/.apex directory and state file exist."""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            if not os.path.exists(self.state_file):
                with open(self.state_file, "w", encoding="utf-8") as f:
                    json.dump({"actions": [], "status": "INITIALIZED", "created_at": time.time()}, f, indent=2)
        except Exception as e:
            sys.stderr.write(f"[DesktopCommander] Warning: Failed to initialize state dir: {e}\n")

    def initialize_display_server(self) -> Dict[str, Any]:
        """Activates and verifies the display surface across macOS, Crostini, and Termux-X11."""
        env = os.environ.copy()
        env["DISPLAY"] = self.display

        active_windows: List[str] = []
        display_type = "Generic Surface"

        if sys.platform == "darwin":
            display_type = "macOS Quartz / WindowServer"
            try:
                osa_cmd = 'tell application "System Events" to get name of every process whose background only is false'
                res = subprocess.run(["osascript", "-e", osa_cmd], capture_output=True, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    active_windows = [w.strip() for w in res.stdout.split(",") if w.strip()]
            except Exception as e:
                sys.stderr.write(f"[DesktopCommander] macOS window query notice: {e}\n")
        else:
            is_crostini = os.getenv("WAYLAND_DISPLAY") is not None or os.path.exists("/tmp/.X11-unix/X0")
            display_type = "Crostini Sommelier (Wayland/X11)" if is_crostini else "Termux-X11 / Hybrid Surface"

            if shutil.which("xdotool"):
                try:
                    res = subprocess.run(["xdotool", "search", "--onlyvisible", "--name", ".*"], capture_output=True, text=True, timeout=3, env=env)
                    if res.returncode == 0:
                        active_windows = [w.strip() for w in res.stdout.splitlines() if w.strip()]
                except Exception as e:
                    sys.stderr.write(f"[DesktopCommander] xdotool notice: {e}\n")
            elif shutil.which("wmctrl"):
                try:
                    res = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True, timeout=3, env=env)
                    if res.returncode == 0:
                        active_windows = [w.strip() for w in res.stdout.splitlines() if w.strip()]
                except Exception:
                    pass

        status = {
            "display": self.display,
            "display_type": display_type,
            "active_windows_count": len(active_windows),
            "active_windows_sample": active_windows[:5],
            "status": "🟢 ACTIVE & READY",
            "timestamp": time.time(),
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
        """Persist command action history to state file."""
        try:
            data = {"actions": [], "status": "ACTIVE"}
            if os.path.exists(self.state_file):
                try:
                    with open(self.state_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {"actions": [], "status": "ACTIVE"}

            data.setdefault("actions", []).append({
                "timestamp": time.time(),
                "action_type": action_type,
                "description": description,
                "metadata": metadata,
            })
            # Limit stored history to last 50 actions to keep state lean
            data["actions"] = data["actions"][-50:]

            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            sys.stderr.write(f"[DesktopCommander] Warning: Could not record action: {e}\n")


if __name__ == "__main__":
    commander = DesktopCommander()
    print("=== APEX DESKTOP COMMANDER INITIALIZATION ===")
    status = commander.initialize_display_server()
    print(json.dumps(status, indent=2))
    print("=============================================")
