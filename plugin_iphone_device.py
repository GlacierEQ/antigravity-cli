#!/usr/bin/env python3
"""
Desktop Commander Plugin: iPhone & iOS Device Forensic Bridge
Performs real-time USB bus inspection, Apple MobileDevice protocol detection,
device state validation, backup auditing, and forensic media mapping.
"""

import os
import sys
import subprocess
import glob
from typing import Dict, List, Any

class IPhoneDevicePlugin:
    name = "iphone_device"
    description = "iPhone / iPad USB Device Inspector, State Validator, and Forensic Bridge"

    @staticmethod
    def _run_cmd(cmd: str | List[str], timeout: int = 10) -> tuple[str, bool]:
        try:
            if isinstance(cmd, str):
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            else:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return (r.stdout.strip() if r.stdout else r.stderr.strip()), r.returncode == 0
        except Exception as e:
            return f"Error: {e}", False

    def scan_usb_devices(self) -> List[Dict[str, Any]]:
        """Scans USB buses for connected Apple mobile devices."""
        raw_usb, _ = self._run_cmd("system_profiler SPUSBDataType 2>/dev/null")
        devices = []
        
        current_dev = {}
        in_apple_dev = False
        for line in raw_usb.splitlines():
            line_str = line.strip()
            if any(k in line_str for k in ["iPhone:", "iPad:", "iPod:"]):
                if current_dev:
                    devices.append(current_dev)
                current_dev = {"name": line_str.replace(":", ""), "type": "iOS_Device", "details": {}}
                in_apple_dev = True
            elif in_apple_dev and ":" in line_str:
                k, v = line_str.split(":", 1)
                current_dev["details"][k.strip()] = v.strip()
            elif in_apple_dev and not line_str:
                in_apple_dev = False
                
        if current_dev:
            devices.append(current_dev)
            
        return devices

    def inspect_device_state(self) -> Dict[str, Any]:
        """Deep check of iPhone / iPad connectivity, tethering interface, and backup footprints."""
        devices = self.scan_usb_devices()
        
        # Check Tethering interface (en5 / iPhone USB)
        tether_ip, _ = self._run_cmd("ipconfig getifaddr en5 2>/dev/null || echo 'none'")
        tether_active = tether_ip != "none" and bool(tether_ip)

        # Check local Apple MobileSync Backups
        backup_dir = os.path.expanduser("~/Library/Application Support/MobileSync/Backup")
        backups = []
        if os.path.exists(backup_dir):
            for b in os.listdir(backup_dir):
                b_path = os.path.join(backup_dir, b)
                if os.path.isdir(b_path):
                    mtime = os.path.getmtime(b_path)
                    backups.append({"udid_folder": b, "last_modified": mtime})

        # Check Voice Memos container
        voice_memos = glob.glob(os.path.expanduser("~/Library/Group Containers/group.com.apple.VoiceMemos.shared/**/*.m4a"), recursive=True)
        
        return {
            "connected_devices": devices,
            "device_count": len(devices),
            "usb_tether_active": tether_active,
            "usb_tether_ip": tether_ip if tether_active else "Inactive",
            "mobilesync_backups_found": len(backups),
            "voice_memos_found": len(voice_memos),
            "status": "🟢 DEVICE CONNECTED" if devices else "⏳ WAITING FOR USB CONNECTION"
        }

if __name__ == "__main__":
    plugin = IPhoneDevicePlugin()
    res = plugin.inspect_device_state()
    print(f"Status: {res['status']}")
    print(f"Connected Devices: {len(res['connected_devices'])}")
    for d in res["connected_devices"]:
        print(f"  • {d['name']} | Serial: {d['details'].get('Serial Number', 'N/A')}")
