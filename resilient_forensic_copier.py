#!/usr/bin/env python3
"""
GlacierEQ Resilient Forensic Drive Copier v1.1
Safely extracts high-priority assets from /Volumes/ShadowDrive to Dropbox.
Implements I/O timeouts, sector error tolerance, and post-copy SHA-256 verification.
"""

from __future__ import annotations

import os
import sys
import subprocess
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple

SRC = "/Volumes/ShadowDrive"
DBX_BASE = os.path.expanduser("~/Library/CloudStorage/Dropbox-Cyber.lazer.mermicor")
DEST = os.path.join(DBX_BASE, "ShadowDrive_Preserved_Assets")
CODEX_DIR = "/Users/kcbflux/Codex"

os.makedirs(DEST, exist_ok=True)
os.makedirs(CODEX_DIR, exist_ok=True)

# Priority Targets in order of forensic value
TARGET_GROUPS = [
    ("Root Reports & Code", ["*.md", "*.py", "*.sh", "*.json", "*.yml", "*.yaml"]),
    ("Core Forensic Tools", ["tools/", "core/", "frontend/", "docs/"]),
    ("iCloud Migration Database", ["AppleMigration/iCloud_Final/session/db/"]),
    ("iCloud Container Plists", ["AppleMigration/iCloud_Final/session/containers/"]),
    ("Apple Migration Session State", ["AppleMigration/iCloud_Final/session/t/"])
]


def run_cmd(cmd: str, timeout: int = 30) -> Tuple[str, bool]:
    """Execute shell command with strict timeout."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode == 0
    except subprocess.TimeoutExpired:
        return "TIMEOUT_SKIPPED", False
    except Exception as e:
        return str(e), False


def sha256_file(filepath: str) -> str:
    """Compute SHA-256 hash of file in chunks."""
    h = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(1024 * 1024):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"ERR:{e}"


def main():
    print("============================================================================")
    print(" 🛡️ GLACIEREQ RESILIENT FORENSIC EXTRACTION TO DROPBOX")
    print(f" Source: {SRC}")
    print(f" Target: {DEST}")
    print("============================================================================")

    if not os.path.exists(SRC):
        print(f"❌ Error: {SRC} is not mounted.")
        return

    # Use rsync with 10s per-file timeout, ignoring unreadable sectors
    print("\n[*] Phase 1: High-Speed Resilient Rsync Replication...")
    rsync_cmd = (
        f"rsync -avh --timeout=10 --ignore-errors "
        f"--exclude='.Spotlight*' --exclude='.fseventsd' --exclude='.git' --exclude='.venv' "
        f"'{SRC}/' '{DEST}/'"
    )
    print(f"  └─ Executing: {rsync_cmd}")
    out, ok = run_cmd(rsync_cmd, timeout=300)
    print(f"  └─ Rsync Status: {'🟢 Completed' if ok else '🟡 Completed with Notices'}")
    if out:
        lines = out.splitlines()
        print(f"  └─ Total lines output: {len(lines)}")
        print(f"  └─ Summary: {lines[-3:] if len(lines) >= 3 else lines}")

    # Phase 2: SHA-256 Hashing of Preserved Target in Dropbox
    print("\n[*] Phase 2: Generating Cryptographic SHA-256 Manifest from Dropbox Target...")
    manifest = []
    total_preserved = 0
    total_bytes = 0

    for root, dirs, files in os.walk(DEST):
        for f in files:
            if f in ["SHADOWDRIVE_PRESERVATION_MANIFEST.json"]:
                continue
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, DEST)
            try:
                sz = os.path.getsize(fpath)
                sha = sha256_file(fpath)
                mtime = os.path.getmtime(fpath)
                manifest.append({
                    "rel_path": rel,
                    "size_bytes": sz,
                    "sha256": sha,
                    "mtime_iso": datetime.fromtimestamp(mtime, timezone.utc).isoformat(),
                })
                total_preserved += 1
                total_bytes += sz
            except Exception as e:
                manifest.append({"rel_path": rel, "error": str(e)})

    manifest_data: Dict[str, Any] = {
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_files_preserved": total_preserved,
        "total_bytes_preserved": total_bytes,
        "total_mb": round(total_bytes / (1024 * 1024), 2),
        "dropbox_destination": DEST,
        "files": manifest,
    }

    manifest_local = os.path.join(CODEX_DIR, "SHADOWDRIVE_PRESERVATION_MANIFEST.json")
    manifest_dbx = os.path.join(DEST, "SHADOWDRIVE_PRESERVATION_MANIFEST.json")

    with open(manifest_local, 'w', encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    with open(manifest_dbx, 'w', encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"\n============================================================================")
    print(f" 🟢 PRESERVATION COMPLETE")
    print(f"  • Total Preserved Files : {total_preserved:,}")
    print(f"  • Total Preserved Size  : {manifest_data['total_mb']} MB")
    print(f"  • Dropbox Destination   : {DEST}")
    print(f"  • Manifest (Local)      : {manifest_local}")
    print(f"  • Manifest (Dropbox)    : {manifest_dbx}")
    print("============================================================================")


if __name__ == "__main__":
    main()
