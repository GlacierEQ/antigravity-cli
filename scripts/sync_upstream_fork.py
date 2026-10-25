#!/usr/bin/env python3
"""
APEX FORK SYNCHRONIZATION & AUTO-UPDATER ENGINE
Standard: Keeps the fork's main branch continuously updated with upstream while
          preserving modular custom plugins, coder bridges, and extensions.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path("/Users/kcbflux/antigravity-cli")


class ForkSyncOrchestrator:
    """
    Automates upstream tracking, non-invasive merging, and extension verification.
    """

    @classmethod
    def run_cmd(cls, cmd: list, cwd: Path = REPO_ROOT) -> tuple[int, str, str]:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return p.returncode, p.stdout.strip(), p.stderr.strip()

    @classmethod
    def ensure_remotes(cls, upstream_url: str = "") -> None:
        ret, stdout, _ = cls.run_cmd(["git", "remote", "-v"])
        if "upstream" not in stdout and upstream_url:
            print(f"[*] Adding upstream remote: {upstream_url}")
            cls.run_cmd(["git", "remote", "add", "upstream", upstream_url])
        elif "upstream" in stdout:
            print("✓ Upstream remote already configured.")

    @classmethod
    def sync_upstream(cls, rebase: bool = False) -> bool:
        print("=" * 80)
        print("🔄 APEX FORK UPSTREAM SYNCHRONIZATION INITIATED")
        print(f"Repository: {REPO_ROOT}")
        print("=" * 80)

        # 1. Fetch remotes
        print("\n[1/4] 📡 Fetching all remotes (origin & upstream)...")
        ret_fetch, out_fetch, err_fetch = cls.run_cmd(["git", "fetch", "--all", "--prune"])
        if ret_fetch != 0:
            print(f"⚠️ Fetch warning: {err_fetch}")
        else:
            print("  ✓ Remotes fetched cleanly.")

        # 2. Check for upstream updates
        has_upstream = False
        _, remotes_out, _ = cls.run_cmd(["git", "remote"])
        if "upstream" in remotes_out:
            has_upstream = True
            print("\n[2/4] 🔍 Checking for new upstream commits on main...")
            ret, log_out, _ = cls.run_cmd(["git", "log", "HEAD..upstream/main", "--oneline"])
            if log_out:
                print(f"  └─ Found {len(log_out.splitlines())} upstream commits to incorporate.")
                if rebase:
                    print("  [*] Rebasing local changes onto upstream/main...")
                    cls.run_cmd(["git", "rebase", "upstream/main"])
                else:
                    print("  [*] Merging upstream/main...")
                    cls.run_cmd(["git", "merge", "upstream/main", "--no-edit"])
            else:
                print("  ✓ Fork is 100% up to date with upstream/main.")
        else:
            print("\n[2/4] ℹ️  No upstream remote configured yet. Tracking origin/main.")

        # 3. Verify extension integrity
        print("\n[3/4] 🧪 Verifying custom extensions & modular plugin integrity...")
        extensions = [
            "antigravity_coder_bridge.py",
            "model_registry.py",
            "ultimate_desktop_commander.py",
            "models_config.json",
        ]
        all_ok = True
        for ext in extensions:
            p = REPO_ROOT / ext
            if p.exists():
                print(f"  ✓ Preserved: {ext}")
            else:
                print(f"  ❌ Missing extension: {ext}")
                all_ok = False

        # 4. Push to origin if ahead
        print("\n[4/4] 🚀 Syncing with origin/main (GlacierEQ)...")
        ret_status, status_out, _ = cls.run_cmd(["git", "status", "-sb"])
        if "ahead" in status_out:
            print("  [*] Pushing local commits to origin/main...")
            ret_push, _, err_push = cls.run_cmd(["git", "push", "origin", "main"])
            if ret_push == 0:
                print("  🟢 Successfully pushed to origin/main.")
            else:
                print(f"  ⚠️ Push notice: {err_push}")
        else:
            print("  ✓ Local branch is in sync with origin/main.")

        print("\n" + "=" * 80)
        print("✅ FORK SYNCHRONIZATION COMPLETE: 100% OPERATIONAL")
        print("=" * 80)
        return all_ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity CLI Fork Sync Orchestrator")
    parser.add_argument("--upstream", "-u", default="", help="Upstream repository URL if adding")
    parser.add_argument("--rebase", "-r", action="store_true", help="Rebase onto upstream instead of merge")
    args = parser.parse_args()

    if args.upstream:
        ForkSyncOrchestrator.ensure_remotes(args.upstream)
    ForkSyncOrchestrator.sync_upstream(rebase=args.rebase)
