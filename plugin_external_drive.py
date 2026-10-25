#!/usr/bin/env python3
"""
Desktop Commander Plugin: External Drive Medic & PC Filesystem Inspector
Integrates non-destructive drive diagnostics, volume verification, healing, and file inspection.
Supports macOS diskutil and Linux lsblk/findmnt storage backends.
"""

from __future__ import annotations

import os
import sys
import subprocess
import shutil
from typing import Dict, List, Any, Tuple


class ExternalDrivePlugin:
    name = "external_drive"
    description = "External Hard Drive Medic, Health Verification, and PC Filesystem Inspector"

    @staticmethod
    def _run_cmd(cmd: str | List[str], timeout: int = 15) -> Tuple[str, bool]:
        """Run system command with output capture and error handling."""
        try:
            if isinstance(cmd, str):
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            else:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return (r.stdout.strip() if r.stdout else r.stderr.strip()), r.returncode == 0
        except Exception as e:
            return f"Error: {e}", False

    def scan_drives(self) -> List[Dict[str, Any]]:
        """Identify all connected external disks and partition schemes across macOS and Linux."""
        disks = []
        if shutil.which("diskutil"):
            out, _ = self._run_cmd("diskutil list")
            current = None
            for line in out.splitlines():
                if line.startswith("/dev/disk"):
                    parts = line.split()
                    dev = parts[0]
                    is_internal = "internal" in line
                    current = {"device": dev, "header": line, "internal": is_internal, "volumes": []}
                    if not is_internal:
                        disks.append(current)
                elif current and not current["internal"] and line.strip():
                    current["volumes"].append(line.strip())
        elif shutil.which("lsblk"):
            out, _ = self._run_cmd("lsblk -J -o NAME,SIZE,TYPE,MOUNTPOINT,HOTPLUG,RM 2>/dev/null || lsblk -l")
            disks.append({"device": "linux_block_devices", "header": "lsblk", "internal": False, "volumes": out.splitlines()})

        return disks

    def inspect_volume(self, disk_dev: str) -> Dict[str, Any]:
        """Perform comprehensive non-destructive inspection of a volume."""
        props: Dict[str, str] = {}
        verify_ok = False
        verify_out = "N/A"

        if shutil.which("diskutil"):
            info_out, _ = self._run_cmd(f"diskutil info {disk_dev}")
            for line in info_out.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    props[k.strip()] = v.strip()

            # Non-destructive volume verification
            verify_out, verify_ok = self._run_cmd(f"diskutil verifyVolume {disk_dev}", timeout=60)

        mount_pt = props.get("Mount Point", "")
        pc_files: List[Dict[str, Any]] = []
        scan_error = None

        if mount_pt and os.path.exists(mount_pt):
            try:
                for item in os.listdir(mount_pt)[:25]:
                    if not item.startswith("."):
                        ipath = os.path.join(mount_pt, item)
                        sz = os.path.getsize(ipath) if os.path.isfile(ipath) else 0
                        pc_files.append({"name": item, "is_dir": os.path.isdir(ipath), "size": sz})
            except Exception as e:
                scan_error = str(e)

        return {
            "device": disk_dev,
            "name": props.get("Volume Name") or props.get("Device / Media Name", "Unknown"),
            "filesystem": props.get("File System Personality") or props.get("Type (Bundle)", "Unknown"),
            "capacity": props.get("Disk Size") or props.get("Volume Total Space", "Unknown"),
            "mount_point": mount_pt or "Not Mounted",
            "writable": props.get("Volume Read-Only") == "No",
            "smart_status": props.get("SMART Status", "External / N/A"),
            "healthy": verify_ok,
            "verification_log": verify_out[:300],
            "root_files_preview": pc_files,
            "scan_error": scan_error,
        }

    def heal_volume(self, disk_dev: str) -> Dict[str, Any]:
        """Safely repair a filesystem using native diskutil repairVolume or fsck."""
        if shutil.which("diskutil"):
            repair_out, repair_ok = self._run_cmd(f"diskutil repairVolume {disk_dev}", timeout=120)
        else:
            repair_out, repair_ok = self._run_cmd(f"fsck -y {disk_dev}", timeout=120)
        return {
            "device": disk_dev,
            "repaired": repair_ok,
            "log": repair_out,
        }


if __name__ == "__main__":
    plugin = ExternalDrivePlugin()
    drives = plugin.scan_drives()
    print(f"External Drives Found: {len(drives)}")
    for d in drives:
        res = plugin.inspect_volume(d["device"])
        print(f"Volume: {res['name']} ({res['filesystem']}) -> Health: {'🟢 OK' if res['healthy'] else '🟡 Needs Repair'}")
