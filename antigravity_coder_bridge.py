#!/usr/bin/env python3
"""
ANTIGRAVITY CODER BRIDGE: OPENCODE + KILO CODE + OPENROUTER
Standard: Unified execution bridge allowing Antigravity CLI to dispatch tasks seamlessly
          across OpenCode Zen, Kilo Code, OpenRouter Free Tier, and Novita AI.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

GATEWAY_PATH = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/MCP_SERVERS/openrouter-free-gateway")
if str(GATEWAY_PATH) not in sys.path:
    sys.path.insert(0, str(GATEWAY_PATH))

from server import chat_novita_ai, chat_openrouter


class AntigravityCoderBridge:
    """
    Unified multi-engine execution dispatcher for Antigravity CLI.
    """

    OPENCODE_BIN = "/usr/local/bin/opencode"
    KILO_BIN = str(Path.home() / ".local" / "bin" / "kilo")

    @classmethod
    def dispatch_opencode(
        cls,
        prompt: str,
        cwd: Optional[str] = None,
        agent: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """Dispatch task to local OpenCode Zen CLI."""
        bin_path = cls.OPENCODE_BIN if Path(cls.OPENCODE_BIN).exists() else shutil.which("opencode")
        if not bin_path:
            return {"status": "error", "message": "OpenCode CLI binary not found."}

        cmd = [bin_path]
        if agent:
            cmd.extend(["--agent", agent])
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["--print", prompt])

        t0 = time.time()
        try:
            p = subprocess.run(
                cmd,
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            elapsed = time.time() - t0
            if p.returncode == 0:
                return {
                    "status": "success",
                    "engine": "opencode_zen",
                    "agent": agent or "default",
                    "model": model or "config_default",
                    "response": p.stdout.strip(),
                    "elapsed_sec": round(elapsed, 2),
                }
            else:
                return {
                    "status": "error",
                    "engine": "opencode_zen",
                    "exit_code": p.returncode,
                    "error": p.stderr.strip(),
                    "stdout": p.stdout.strip(),
                }
        except subprocess.TimeoutExpired:
            return {"status": "error", "engine": "opencode_zen", "message": f"OpenCode timed out after {timeout}s"}
        except Exception as e:
            return {"status": "error", "engine": "opencode_zen", "message": str(e)}

    @classmethod
    def dispatch_kilo(
        cls,
        prompt: str,
        cwd: Optional[str] = None,
        agent: Optional[str] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """Dispatch task to local Kilo Code CLI."""
        bin_path = cls.KILO_BIN if Path(cls.KILO_BIN).exists() else shutil.which("kilo")
        if not bin_path:
            return {"status": "error", "message": "Kilo Code CLI binary not found."}

        cmd = [bin_path]
        if agent:
            cmd.extend(["--agent", agent])
        cmd.extend(["--print", prompt])

        t0 = time.time()
        try:
            p = subprocess.run(
                cmd,
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            elapsed = time.time() - t0
            if p.returncode == 0:
                return {
                    "status": "success",
                    "engine": "kilo_code",
                    "agent": agent or "default",
                    "response": p.stdout.strip(),
                    "elapsed_sec": round(elapsed, 2),
                }
            else:
                return {
                    "status": "error",
                    "engine": "kilo_code",
                    "exit_code": p.returncode,
                    "error": p.stderr.strip(),
                    "stdout": p.stdout.strip(),
                }
        except subprocess.TimeoutExpired:
            return {"status": "error", "engine": "kilo_code", "message": f"Kilo Code timed out after {timeout}s"}
        except Exception as e:
            return {"status": "error", "engine": "kilo_code", "message": str(e)}

    @classmethod
    def dispatch_openrouter(
        cls,
        prompt: str,
        model: str = "xiaomi/mimo-v2.5-pro",
        system_prompt: str = "",
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Dispatch task to OpenRouter Free Tier gateway with Novita AI failover."""
        return chat_openrouter(model=model, prompt=prompt, system_prompt=system_prompt, max_tokens=max_tokens)

    @classmethod
    def dispatch_auto(
        cls,
        prompt: str,
        preferred_engine: str = "auto",
        model: Optional[str] = None,
        agent: Optional[str] = None,
        cwd: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Auto-routes prompt to the optimal available engine:
        OpenCode -> Kilo -> OpenRouter -> Novita AI.
        """
        if preferred_engine == "opencode":
            res = cls.dispatch_opencode(prompt, cwd=cwd, agent=agent, model=model)
            if res.get("status") == "success":
                return res
        elif preferred_engine == "kilo":
            res = cls.dispatch_kilo(prompt, cwd=cwd, agent=agent)
            if res.get("status") == "success":
                return res
        elif preferred_engine == "openrouter":
            return cls.dispatch_openrouter(prompt, model=model or "xiaomi/mimo-v2.5-pro")

        # Auto Cascading Fallback Loop
        # 1. Try OpenRouter / Novita
        target_model = model or "xiaomi/mimo-v2.5-pro"
        res_or = cls.dispatch_openrouter(prompt, model=target_model)
        if res_or.get("status") == "success":
            return res_or

        # 2. Try OpenCode
        res_oc = cls.dispatch_opencode(prompt, cwd=cwd, agent=agent, model=model)
        if res_oc.get("status") == "success":
            return res_oc

        # 3. Try Kilo Code
        res_kilo = cls.dispatch_kilo(prompt, cwd=cwd, agent=agent)
        if res_kilo.get("status") == "success":
            return res_kilo

        return {
            "status": "error",
            "message": "All execution engines (OpenRouter, OpenCode, Kilo) were attempted and failed.",
        }


def main():
    parser = argparse.ArgumentParser(description="Antigravity Unified Coder Bridge")
    parser.add_argument("prompt", help="Prompt or task instruction to dispatch")
    parser.add_argument("--engine", "-e", choices=["auto", "opencode", "kilo", "openrouter"], default="auto", help="Execution engine")
    parser.add_argument("--model", "-m", help="Target model identifier (e.g. 'xiaomi/mimo-v2.5-pro')")
    parser.add_argument("--agent", "-a", help="Agent persona (e.g. 'coding', 'zen', 'mimo', 'creative')")
    parser.add_argument("--cwd", help="Working directory context")
    args = parser.parse_args()

    result = AntigravityCoderBridge.dispatch_auto(
        prompt=args.prompt,
        preferred_engine=args.engine,
        model=args.model,
        agent=args.agent,
        cwd=args.cwd,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
