#!/usr/bin/env python3
"""
ANTIGRAVITY CODER BRIDGE: OPENCODE + KILO CODE + OPENROUTER + NOVITA AI
Standard: Unified execution bridge allowing Antigravity CLI to dispatch tasks seamlessly
          across OpenCode Zen, Kilo Code, OpenRouter Free Tier, and Novita AI.
Resilience: Fully standalone with dynamic MCP gateway detection and native REST failover.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

# Attempt to load local gateway server module if present
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Dynamic gateway paths
POTENTIAL_GATEWAYS = [
    os.getenv("OPENROUTER_GATEWAY_PATH"),
    "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/MCP_SERVERS/openrouter-free-gateway",
    str(Path.home() / "APEX_SYSTEM/INFRASTRUCTURE/MCP_SERVERS/openrouter-free-gateway"),
]

chat_openrouter = None
chat_novita_ai = None

for gp in POTENTIAL_GATEWAYS:
    if gp and Path(gp).exists():
        if str(gp) not in sys.path:
            sys.path.insert(0, str(gp))
        try:
            from server import chat_novita_ai as _cn, chat_openrouter as _co
            chat_novita_ai = _cn
            chat_openrouter = _co
            break
        except Exception:
            pass

# Import Supabase Vault for API key fallback
try:
    from supabase_vault_client import SupabaseVaultClient
    _vault_client = SupabaseVaultClient()
except Exception:
    _vault_client = None


def _get_api_key(key_name: str, env_vars: List[str]) -> Optional[str]:
    """Retrieve API key from environment variables or Supabase Vault fallback."""
    for ev in env_vars:
        val = os.getenv(ev)
        if val:
            return val.strip()
    if _vault_client:
        return _vault_client.get_key(key_name)
    return None


def _native_rest_openrouter(
    prompt: str,
    model: str = "xiaomi/mimo-v2.5-pro",
    system_prompt: str = "",
    max_tokens: int = 4096,
    timeout: int = 45,
) -> Dict[str, Any]:
    """Native REST OpenRouter fallback when local gateway MCP server is not reachable."""
    api_key = _get_api_key("OPENROUTER_API_KEY", ["OPENROUTER_API_KEY", "OPENROUTER_API_KEY2"])
    if not api_key:
        return {
            "status": "error",
            "engine": "openrouter_rest_fallback",
            "message": "OpenRouter API key not found in environment or Supabase Vault.",
        }

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/GlacierEQ/antigravity-cli",
        "X-Title": "Antigravity Coder Bridge",
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    t0 = time.time()
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - t0
            content = data["choices"][0]["message"]["content"]
            return {
                "status": "success",
                "engine": "openrouter_rest_direct",
                "model": model,
                "response": content.strip(),
                "elapsed_sec": round(elapsed, 2),
                "usage": data.get("usage", {}),
            }
    except Exception as e:
        return {
            "status": "error",
            "engine": "openrouter_rest_direct",
            "message": f"OpenRouter REST request failed: {e}",
        }


def _native_rest_novita(
    prompt: str,
    model: str = "meta-llama/llama-3.3-70b-instruct",
    system_prompt: str = "",
    max_tokens: int = 4096,
    timeout: int = 45,
) -> Dict[str, Any]:
    """Native REST Novita AI fallback when local gateway MCP server is not reachable."""
    api_key = _get_api_key("NOVITA_API_KEY", ["NOVITA_API_KEY", "NOVITA_KEY"])
    if not api_key:
        return {
            "status": "error",
            "engine": "novita_rest_fallback",
            "message": "Novita API key not found in environment or Supabase Vault.",
        }

    url = "https://api.novita.ai/v3/openai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    t0 = time.time()
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - t0
            content = data["choices"][0]["message"]["content"]
            return {
                "status": "success",
                "engine": "novita_rest_direct",
                "model": model,
                "response": content.strip(),
                "elapsed_sec": round(elapsed, 2),
                "usage": data.get("usage", {}),
            }
    except Exception as e:
        return {
            "status": "error",
            "engine": "novita_rest_direct",
            "message": f"Novita REST request failed: {e}",
        }


class AntigravityCoderBridge:
    """
    Unified multi-engine execution dispatcher for Antigravity CLI.
    Orchestrates OpenCode Zen, Kilo Code, OpenRouter Free Tier, and Novita AI with zero crash risk.
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
            return {"status": "error", "engine": "opencode_zen", "message": "OpenCode CLI binary not found."}

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
            return {"status": "error", "engine": "kilo_code", "message": "Kilo Code CLI binary not found."}

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
        if chat_openrouter is not None:
            try:
                res = chat_openrouter(model=model, prompt=prompt, system_prompt=system_prompt, max_tokens=max_tokens)
                if res.get("status") == "success":
                    return res
            except Exception:
                pass

        # Direct REST fallback
        res = _native_rest_openrouter(prompt, model=model, system_prompt=system_prompt, max_tokens=max_tokens)
        if res.get("status") == "success":
            return res

        # Novita fallback if available
        if chat_novita_ai is not None:
            try:
                return chat_novita_ai(prompt=prompt, system_prompt=system_prompt, max_tokens=max_tokens)
            except Exception:
                pass

        return _native_rest_novita(prompt, system_prompt=system_prompt, max_tokens=max_tokens)

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
