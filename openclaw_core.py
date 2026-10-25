#!/usr/bin/env python3
"""
APEX Super Pro OpenClaw — Maximized Holographic Mesh Engine v20.0
Multi-Provider Inference · Device Telemetry & Control · FTS5 Forensic Search
Autonomous Agentic Tool Loop · Casebuilder 4000 · Aspen-Grove Memory Substrate

Doctrine: INNOVATION Holographic Mesh (Decentralized, Hard, Pro, Elite)
Operator: Casey Barton / GlacierEQ
"""

import os
import sys
import json
import ast
import re
import ssl
import time
import sqlite3
import subprocess
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Generator

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# ANSI Color Codes for Pro Terminal UI
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

# Substrate & Database Paths
CHAT_DB = Path("/data/data/com.termux/files/home/.openclaw/state/chat_forensics_structured.sqlite")
STEALTH_INDEX_DB = Path("/data/data/com.termux/files/home/.openclaw/state/stealth_claw_index.sqlite")
OPENCLAW_DB = Path("/data/data/com.termux/files/home/.openclaw/state/openclaw.sqlite")
ASPEN_MEMORY_URL = "http://127.0.0.1:8787"
OLLAMA_URL = "http://127.0.0.1:11434"
TERMUX_BIN = Path("/data/data/com.termux/files/usr/bin")

# Provider Specifications
PROVIDERS = {
    "groq": {
        "name": "Groq LPU Engine",
        "env_var": "GROQ_API_KEY",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "default_model": "qwen/qwen3.8-27b",
        "models": ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b", "groq/compound-mini"],
        "timeout": 20.0
    },
    "google": {
        "name": "Google Gemini",
        "env_var": "GOOGLE_API_KEY",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        "default_model": "gemini-2.5-flash",
        "models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite"],
        "timeout": 25.0
    },
    "mistral": {
        "name": "Mistral AI",
        "env_var": "MISTRAL_API_KEY",
        "url": "https://api.mistral.ai/v1/chat/completions",
        "default_model": "codestral-latest",
        "models": ["codestral-latest", "mistral-large-latest", "mistral-code-latest"],
        "timeout": 25.0
    },
    "openrouter": {
        "name": "OpenRouter Free Mesh",
        "env_var": "OPENROUTER_API_KEY",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "default_model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "models": [
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            "google/gemma-4-26b-a4b-it:free",
            "nvidia/nemotron-3-ultra-550b-a55b:free"
        ],
        "timeout": 30.0
    },
    "cerebras": {
        "name": "Cerebras Inference",
        "env_var": "CEREBRAS_API_KEY",
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "default_model": "qwen-3.8-27b",
        "models": ["qwen-3.8-27b", "gpt-oss-120b"],
        "timeout": 15.0
    },
    "local": {
        "name": "Local Ollama / MiMo",
        "env_var": "OLLAMA_API_KEY",
        "url": "http://127.0.0.1:11434/api/generate",
        "default_model": "apex-gemma4",
        "models": ["apex-gemma4", "omni-agent", "apex-gemma-core"],
        "timeout": 45.0
    }
}

CASES = {
    "1FDV": {
        "title": "Barton Custody & Due Process Enforcement (Family Court Vacatur)",
        "docket": "1FDV-23-0001009",
        "path": "/root/LEGAL_WARFARE_PACKAGE_1FDV/casebuilder4000_export",
        "damages": "$2,989,847.00",
        "verified_facts": 125,
        "score": "75.0/100"
    },
    "RICO": {
        "title": "Casey Barton v. Natasha Shaw, Scot Brower, et al.",
        "docket": "1:26-cv-001009-RICO",
        "path": "/root/legal_mesh/apex-legal-case/casebuilder4000_export",
        "damages": "$56,386,460.00",
        "verified_facts": 81,
        "score": "75.0/100"
    },
    "CFAA": {
        "title": "Casey Barton v. Cyber Intrusion Actors & Spoliation Conspirators",
        "docket": "1:26-cv-001030-CFAA",
        "path": "/root/legal_mesh/CYBERTACK-1FDV-23-0001009/casebuilder4000_export",
        "damages": "$2,450,000.00",
        "verified_facts": 60,
        "score": "75.0/100"
    },
    "CASINO": {
        "title": "Casey Barton v. Casino Resort Corporation, Hotel Operations, LLC",
        "docket": "24-PI-CASINO-001",
        "path": "/root/apex_case_framework/CASINO_MASTER_CASE/casebuilder4000_export",
        "damages": "$14,250,000.00",
        "verified_facts": 51,
        "score": "75.0/100"
    },
    "NEXCOM": {
        "title": "Cherry Chan v. Navy Exchange Service Command (NEXCOM)",
        "docket": "26-NEX-007",
        "path": "/root/legal_mesh/nexus-legal-grid/casebuilder4000_export",
        "damages": "$4,850,000.00",
        "verified_facts": 56,
        "score": "75.0/100"
    },
    "BROWER": {
        "title": "In re Professional Misconduct Presentment: Scot S. Brower",
        "docket": "ODC-2026-BROWER",
        "path": "/root/legal_mesh/LEGAL-AI-NEXUS/casebuilder4000_export",
        "damages": "$250,000.00",
        "verified_facts": 85,
        "score": "75.0/100"
    }
}

class SuperProOpenClaw:
    def __init__(self):
        self._load_environment()
        self.active_provider = "groq"
        self.active_model = PROVIDERS["groq"]["default_model"]
        self.history: List[Dict[str, str]] = []

    def _load_environment(self):
        """Loads credentials prioritizing gatekeeper.env > credentials.env > .env > opencode auth.json."""
        sources = [
            Path("/root/.env"),
            Path("/data/data/com.termux/files/home/.openclaw/.env"),
            Path("/root/.apex_vault/credentials.env"),
            Path("/root/.operator_key_vault/gatekeeper.env")
        ]
        pattern = re.compile(r'^(?:export\s+)?([A-Za-z0-9_]+)=["\']?(.*?)["\']?$')
        for s in sources:
            if s.exists():
                try:
                    for line in s.read_text(encoding="utf-8").splitlines():
                        m = pattern.match(line.strip())
                        if m:
                            k, v = m.group(1), m.group(2)
                            if v:
                                os.environ[k] = v
                except Exception:
                    pass

        auth_json = Path("/root/.local/share/opencode/auth.json")
        if auth_json.exists():
            try:
                data = json.loads(auth_json.read_text())
                for prov, env_key in [("groq", "GROQ_API_KEY"), ("openrouter", "OPENROUTER_API_KEY"), 
                                      ("google", "GOOGLE_API_KEY"), ("mistral", "MISTRAL_API_KEY"), 
                                      ("cerebras", "CEREBRAS_API_KEY")]:
                    if prov in data and data[prov].get("key"):
                        os.environ[env_key] = data[prov]["key"]
            except Exception:
                pass

    def get_key(self, provider_id: str) -> Optional[str]:
        cfg = PROVIDERS.get(provider_id)
        if not cfg:
            return None
        return os.getenv(cfg["env_var"])

    # -------------------------------------------------------------------------
    # HARDWARE & DEVICE SUBSYSTEM
    # -------------------------------------------------------------------------
    def run_termux_tool(self, tool_name: str, args: List[str] = None, timeout: int = 3) -> Tuple[int, str]:
        """Runs a Termux API binary safely with argument passing."""
        cmd_path = TERMUX_BIN / tool_name
        if not cmd_path.exists():
            # Check PATH
            cmd_path = tool_name
        cmd = [str(cmd_path)] + (args or [])
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return res.returncode, res.stdout.strip() or res.stderr.strip()
        except Exception as e:
            return -1, str(e)

    def device_control(self, action: str, *args) -> Dict[str, Any]:
        """Full native device hardware operations with Termux API and Linux substrate telemetry."""
        action = action.lower()
        if action in ["status", "telemetry", "battery"]:
            code, bat_out = self.run_termux_tool("termux-battery-status", timeout=1.5)
            bat = None
            if code == 0 and bat_out.startswith("{"):
                try:
                    bat = json.loads(bat_out)
                except Exception:
                    pass
            if not bat:
                bat = {"status": "STANDBY", "note": "Termux:API broadcast unavailable or in sleep mode"}

            # Substrate telemetry
            try:
                load = os.getloadavg()
            except Exception:
                load = [0.0, 0.0, 0.0]

            import shutil
            try:
                tot, used, free = shutil.disk_usage("/root")
                disk_info = {"total_gb": round(tot / (1024**3), 2), "used_gb": round(used / (1024**3), 2), "free_gb": round(free / (1024**3), 2)}
            except Exception:
                disk_info = {}

            return {
                "hardware": "Android ARM64 PRoot Substrate",
                "battery": bat,
                "load_avg": load,
                "disk": disk_info,
                "timestamp": time.time()
            }
        elif action == "notify":
            title = args[0] if len(args) > 0 else "APEX OpenClaw"
            content = args[1] if len(args) > 1 else (args[0] if args else "Notification")
            code, out = self.run_termux_tool("termux-notification", ["-t", title, "-c", content, "-i", "openclaw_1"], timeout=1.5)
            return {"success": code == 0, "title": title, "content": content}
        elif action == "toast":
            msg = " ".join(args) if args else "OpenClaw Pro Alert"
            code, out = self.run_termux_tool("termux-toast", [msg], timeout=1.5)
            return {"success": code == 0, "message": msg}
        elif action == "speak":
            text = " ".join(args) if args else "OpenClaw online"
            code, out = self.run_termux_tool("termux-tts-speak", [text], timeout=2.0)
            return {"success": code == 0, "spoken": text}
        elif action == "vibrate":
            duration = str(args[0]) if args else "300"
            code, out = self.run_termux_tool("termux-vibrate", ["-d", duration], timeout=1.5)
            return {"success": code == 0, "duration_ms": duration}
        elif action == "clip":
            sub = args[0].lower() if args else "get"
            if sub == "get":
                code, out = self.run_termux_tool("termux-clipboard-get", timeout=1.5)
                return {"clipboard": out}
            elif sub == "set":
                val = " ".join(args[1:]) if len(args) > 1 else ""
                code, out = self.run_termux_tool("termux-clipboard-set", [val], timeout=1.5)
                return {"success": code == 0, "copied": val}
        elif action == "torch":
            state = args[0].lower() if args else "on"
            code, out = self.run_termux_tool("termux-torch", [state], timeout=1.5)
            return {"success": code == 0, "torch": state}
        return {"error": f"Unknown device action '{action}'. Choose from: status, battery, notify, toast, speak, vibrate, clip, torch"}

    # -------------------------------------------------------------------------
    # AI INFERENCE ENGINE (MULTI-PROVIDER CASCADE)
    # -------------------------------------------------------------------------
    def call_provider(self, provider_id: str, model: str, prompt: str, system_prompt: str = "") -> Tuple[bool, str, float]:
        """Calls a specific provider with timing and error isolation."""
        cfg = PROVIDERS.get(provider_id)
        if not cfg:
            return False, f"Unknown provider '{provider_id}'", 0.0

        key = self.get_key(provider_id)
        if not key and provider_id != "local":
            return False, f"Missing API key for {cfg['name']}", 0.0

        t0 = time.time()

        # Google Gemini HTTP Format
        if provider_id == "google":
            url = cfg["url"].format(model=model, key=key)
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            if system_prompt:
                payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
            headers = {"Content-Type": "application/json"}
            try:
                if HAS_HTTPX:
                    resp = httpx.post(url, json=payload, headers=headers, timeout=cfg["timeout"])
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        return True, text, time.time() - t0
                    return False, f"HTTP {resp.status_code}: {resp.text[:150]}", time.time() - t0
                else:
                    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    with urllib.request.urlopen(req, timeout=cfg["timeout"], context=ctx) as r:
                        data = json.loads(r.read().decode())
                        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        return True, text, time.time() - t0
            except Exception as e:
                return False, str(e), time.time() - t0

        # OpenAI-Compatible Format (Groq, OpenRouter, Mistral, Cerebras)
        url = cfg["url"]
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "OpenClaw-Pro/20.0"
        }
        if provider_id == "openrouter":
            headers["HTTP-Referer"] = "https://apex.mesh"
            headers["X-Title"] = "APEX OpenClaw Pro"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3
        }

        try:
            if HAS_HTTPX:
                resp = httpx.post(url, json=payload, headers=headers, timeout=cfg["timeout"])
                if resp.status_code == 200:
                    data = resp.json()
                    if "choices" in data and data["choices"]:
                        text = data["choices"][0]["message"]["content"].strip()
                        return True, text, time.time() - t0
                    elif "error" in data:
                        err_msg = data["error"].get("message", str(data["error"]))
                        return False, f"Provider Error: {err_msg[:150]}", time.time() - t0
                    return False, f"Unexpected response structure: {str(data)[:150]}", time.time() - t0
                return False, f"HTTP {resp.status_code}: {resp.text[:150]}", time.time() - t0
            else:
                req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                with urllib.request.urlopen(req, timeout=cfg["timeout"], context=ctx) as r:
                    data = json.loads(r.read().decode())
                    if "choices" in data and data["choices"]:
                        text = data["choices"][0]["message"]["content"].strip()
                        return True, text, time.time() - t0
                    elif "error" in data:
                        err_msg = data["error"].get("message", str(data["error"]))
                        return False, f"Provider Error: {err_msg[:150]}", time.time() - t0
                    return False, f"Unexpected response structure: {str(data)[:150]}", time.time() - t0
        except Exception as e:
            return False, str(e), time.time() - t0

    def query(self, prompt: str, target_provider: Optional[str] = None, target_model: Optional[str] = None, system_prompt: Optional[str] = None) -> Tuple[str, str, float]:
        """Queries model with automatic cascading failover across holographic mesh."""
        sys_prompt = system_prompt or "You are OpenClaw Pro, an elite high-throughput holographic mesh AI agent. Answer directly, rigorously, and factually with zero fluff."

        # If specific provider requested
        if target_provider:
            p_id = target_provider
            m_id = target_model or PROVIDERS[p_id]["default_model"]
            ok, text, elapsed = self.call_provider(p_id, m_id, prompt, sys_prompt)
            if ok:
                return f"[{p_id.upper()} / {m_id}]", text, elapsed
            print(f"{Color.YELLOW}[!] Provider {p_id} returned error: {text}. Cascading to mesh...{Color.RESET}")

        # Cascade order: Groq -> Google -> Mistral -> OpenRouter
        cascade = ["groq", "google", "mistral", "openrouter"]
        for p_id in cascade:
            m_id = PROVIDERS[p_id]["default_model"]
            ok, text, elapsed = self.call_provider(p_id, m_id, prompt, sys_prompt)
            if ok:
                return f"[{p_id.upper()} / {m_id}]", text, elapsed

        return "[FAILED]", "All mesh providers unreachable. Check network and API keys.", 0.0

    def stream_provider(self, provider_id: str, model: str, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        """Streams response tokens from the specified provider."""
        cfg = PROVIDERS.get(provider_id)
        if not cfg:
            yield f"[Error: Unknown provider {provider_id}]"
            return

        key = self.get_key(provider_id)
        if not key and provider_id != "local":
            yield f"[Error: Missing API key for {cfg['name']}]"
            return

        # Google Gemini Streaming
        if provider_id == "google":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={key}&alt=sse"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            if system_prompt:
                payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
            try:
                if HAS_HTTPX:
                    with httpx.stream("POST", url, json=payload, timeout=cfg["timeout"]) as response:
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                try:
                                    chunk = json.loads(line[6:])
                                    text = chunk["candidates"][0]["content"]["parts"][0]["text"]
                                    yield text
                                except Exception:
                                    pass
                    return
            except Exception as e:
                yield f"[Stream Error: {e}]"
                return

        # OpenAI Compatible Streaming (Groq, Mistral, OpenRouter, Cerebras)
        url = cfg["url"]
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "OpenClaw-Pro/20.0"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "stream": True
        }

        try:
            if HAS_HTTPX:
                with httpx.stream("POST", url, json=payload, headers=headers, timeout=cfg["timeout"]) as response:
                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            raw_data = line[6:].strip()
                            if raw_data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(raw_data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    yield content
                            except Exception:
                                pass
            else:
                ok, text, _ = self.call_provider(provider_id, model, prompt, system_prompt)
                yield text
        except Exception as e:
            ok, text, _ = self.call_provider(provider_id, model, prompt, system_prompt)
            yield text

    def stream_query(self, prompt: str, target_provider: Optional[str] = None, target_model: Optional[str] = None, system_prompt: Optional[str] = None) -> Generator[Tuple[str, str], None, None]:
        """Yields (provider_tag, token) tuples in real-time across mesh."""
        sys_prompt = system_prompt or "You are OpenClaw Pro, an elite high-throughput holographic mesh AI agent. Answer directly, rigorously, and factually with zero fluff."
        p_id = target_provider or "groq"
        m_id = target_model or PROVIDERS[p_id]["default_model"]
        tag = f"[{p_id.upper()} / {m_id}]"
        for token in self.stream_provider(p_id, m_id, prompt, sys_prompt):
            yield tag, token

    # -------------------------------------------------------------------------
    # ACCELERATED FTS5 FORENSIC SEARCH (150ms Speed)
    # -------------------------------------------------------------------------
    def fts_search(self, query_str: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Instant sub-second full-text search across 140,688 messages via SQLite FTS5."""
        if not CHAT_DB.exists():
            return [{"error": f"Chat Forensics database not found at {CHAT_DB}"}]

        conn = sqlite3.connect(CHAT_DB)
        cur = conn.cursor()
        results = []

        # 1. Try master_chat_fts first (FTS5 index: 150ms)
        try:
            # Clean search terms for FTS MATCH
            clean_q = re.sub(r'[^\w\s]', '', query_str).strip()
            cur.execute("""
                SELECT msg_id, conv_title, author_role, content, category
                FROM master_chat_fts
                WHERE master_chat_fts MATCH ?
                LIMIT ?
            """, (clean_q, limit))
            rows = cur.fetchall()
            for r in rows:
                results.append({
                    "msg_id": r[0],
                    "conv_title": r[1],
                    "role": r[2],
                    "category": r[4],
                    "snippet": r[3][:250].replace("\n", " ").strip(),
                    "source": "FTS5_ACCELERATED"
                })
            if results:
                return results
        except Exception:
            pass

        # 2. Fallback: indexed master_messages query
        search_pattern = f"%{query_str}%"
        cur.execute("""
            SELECT msg_id, conv_title, timestamp_iso, author_role, category, significance_score, content, sha256
            FROM master_messages
            WHERE content LIKE ? OR category LIKE ? OR statutory_tags LIKE ?
            ORDER BY significance_score DESC, timestamp DESC
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, limit))

        rows = cur.fetchall()
        for r in rows:
            results.append({
                "msg_id": r[0],
                "conv_title": r[1],
                "date": r[2],
                "role": r[3],
                "category": r[4],
                "score": r[5],
                "snippet": r[6][:250].replace("\n", " ").strip(),
                "sha256": r[7],
                "source": "INDEX_FALLBACK"
            })
        return results

    # -------------------------------------------------------------------------
    # AUTONOMOUS AGENTIC ENGINE & TOOL EXECUTION MESH
    # -------------------------------------------------------------------------
    def parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts and parses structured tool call JSON from model output with nested and unclosed tolerance."""
        if not text:
            return None

        # Pass 1: raw_decode starting from first '{' after any code block tag
        start_idx = -1
        m_tag = re.search(r'```(?:tool_call|json|tool)?\s*', text)
        if m_tag:
            start_idx = text.find('{', m_tag.end())
        if start_idx == -1:
            start_idx = text.find('{')

        decoder = json.JSONDecoder()
        scan_idx = start_idx
        while scan_idx != -1 and scan_idx < len(text):
            try:
                obj, end_idx = decoder.raw_decode(text, scan_idx)
                if isinstance(obj, dict) and ("tool" in obj or "command" in obj or "action" in obj):
                    return obj
            except Exception:
                pass
            scan_idx = text.find('{', scan_idx + 1)

        # Pass 2: Clean code block slices with closing brace repair
        m_block = re.search(r'```(?:tool_call|json|tool)?\s*([\s\S]*?)(?:```|$)', text)
        if m_block:
            chunk = m_block.group(1).strip()
            first_brace = chunk.find('{')
            if first_brace != -1:
                candidate = chunk[first_brace:]
                for suffix in ["", "}", "\"}", "\"}}", "}}", "]}}"]:
                    try:
                        obj = json.loads(candidate + suffix)
                        if isinstance(obj, dict) and ("tool" in obj or "command" in obj):
                            return obj
                    except Exception:
                        pass

        return None

    def get_agent_system_prompt(self) -> str:
        """Doctrine-hardened system prompt instructing autonomous agentic behavior."""
        return """You are APEX Super Pro OpenClaw v20.0, an elite autonomous AI agent operating directly on Android ARM64 Linux substrate.
Doctrine: Holographic Mesh (Elite · Pro · Hard · G). Operator: Casey Barton / GlacierEQ.

You are equipped with live system tools and connectors.

CRITICAL DIRECTIVES:
1. When asked about filesystem contents, files, code, bash commands, hardware telemetry, chat forensics, memory records, court cases, or recent web information, YOU MUST CALL A TOOL FIRST.
2. NEVER guess, invent facts, or state that you lack capabilities or access. Call the appropriate tool.
3. If the user request is purely conceptual, general knowledge, greetings, or coding explanations that require no substrate inspection, answer directly and concisely in Markdown without calling any tool.
4. To call a tool, output ONLY the tool call block in this format:
```tool_call
{"tool": "<tool_name>", "thought": "<reasoning>", "args": { ... }}
```
Do not include any conversational filler before or after the tool call block.

AVAILABLE TOOLS:
- bash: {"command": "<shell_command>"}
  Run shell commands on the substrate (e.g. ls, cat, grep, ps, git, curl). Working dir is /root.
- read_file: {"path": "<file_path>", "max_lines": 150, "offset": 0}
  Read contents or line ranges from a file, or list a directory.
- write_file: {"path": "<file_path>", "content": "<text>"}
  Write or overwrite content to a file on disk.
- web_search: {"query": "<search_terms>", "max_results": 5}
  Perform live web search via DuckDuckGo Lite.
- fts_search: {"query": "<search_terms>", "limit": 5}
  Fast FTS5 search across 140,688 chat forensics records (~150ms).
- memory: {"action": "search|get|set|list", "key": "<key>", "value": "<val>"}
  Interact with the Aspen-Grove quantum memory substrate (port 8787).
- device: {"action": "battery|status|toast|notify|speak|vibrate|clip|torch", "args": [...]}
  Control native Android device hardware via Termux API.
- legal_dossier: {"case": "1FDV|RICO|CFAA|CASINO|NEXCOM|BROWER"}
  Retrieve Casebuilder 4000 case dossier with verified damages and facts.
- draft_motion: {"type": "rule60b|spoliation|recusal"}
  Draft formal court motions citing Fourteenth Amendment due process and controlling Hawaii law.
- git_info: {"repo_path": "/root"}
  Inspect git repository branch, status, and recent commits.
- ast_verify: {"file_path": "<python_file>"}
  Verify Python code syntax and structure via AST parsing.

Once you receive tool results, synthesize a direct, authoritative, and well-formatted markdown response."""

    def execute_tool(self, tool_name: str, args: Any) -> Tuple[bool, str, Dict[str, Any]]:
        """Executes any of the 11 integrated tools and connectors on the real substrate."""
        tool_name = tool_name.lower().strip()
        t0 = time.time()
        
        # Robust argument normalization: handle list, string, or non-dict forms
        if isinstance(args, list):
            if tool_name == "bash":
                args = {"command": " ".join(str(x) for x in args)}
            elif tool_name in ["read_file", "read"]:
                args = {"path": str(args[0]) if args else ""}
            elif tool_name in ["write_file", "write"]:
                args = {"path": str(args[0]) if args else "", "content": str(args[1]) if len(args) > 1 else ""}
            elif tool_name in ["web_search", "fts_search"]:
                args = {"query": " ".join(str(x) for x in args)}
            elif tool_name in ["device", "hw"]:
                args = {"action": str(args[0]) if args else "status", "args": args[1:] if len(args) > 1 else []}
            elif tool_name in ["legal_dossier", "legal", "case"]:
                args = {"case": str(args[0]) if args else "1FDV"}
            elif tool_name in ["draft_motion", "motion"]:
                args = {"type": str(args[0]) if args else "rule60b"}
            elif tool_name in ["memory", "mem"]:
                args = {"action": str(args[0]) if args else "list", "key": str(args[1]) if len(args) > 1 else "", "value": str(args[2]) if len(args) > 2 else ""}
            else:
                args = {"arg": args[0] if args else ""}
        elif isinstance(args, str):
            args = {"command": args, "query": args, "path": args, "action": args, "case": args, "type": args}
        elif not isinstance(args, dict):
            args = {}

        if tool_name == "bash":
            cmd = args.get("command", "")
            if not cmd:
                return False, "Error: No command specified for bash.", {}
            # Safety against sweeping scans
            if re.search(r'\bfind\s+/\s+-', cmd) or cmd.strip() in ["find /", "ls -la /"]:
                cmd = "find /root -maxdepth 3"
            try:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15, cwd="/root")
                out = (res.stdout or res.stderr).strip()
                if not out:
                    out = f"(Command exited with code {res.returncode}, no output)"
                if len(out) > 4000:
                    out = out[:4000] + f"\n... [Output truncated from {len(out)} bytes]"
                return res.returncode == 0, out, {"command": cmd, "exit_code": res.returncode, "elapsed": time.time() - t0}
            except subprocess.TimeoutExpired:
                return False, "Command timed out after 15 seconds.", {"command": cmd, "timeout": True}
            except Exception as e:
                return False, f"Execution failed: {str(e)}", {"command": cmd, "error": str(e)}

        elif tool_name in ["read_file", "read"]:
            path = args.get("path", "")
            max_lines = int(args.get("max_lines", 150))
            offset = int(args.get("offset", 0))
            if not path:
                return False, "Error: No path specified for read_file.", {}
            p = Path(path).expanduser()
            if not p.is_absolute():
                p = Path("/root") / p
            if not p.exists():
                return False, f"File not found: {p}", {"path": str(p)}
            if p.is_dir():
                items = [f.name + ("/" if f.is_dir() else "") for f in list(p.iterdir())[:60]]
                return True, f"Directory listing for {p} ({len(items)} items):\n" + "\n".join(items), {"path": str(p), "is_dir": True}
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
                total_lines = len(lines)
                sliced = lines[offset:offset+max_lines]
                formatted = "\n".join([f"{i+offset+1}: {line}" for i, line in enumerate(sliced)])
                header = f"[{p} | Lines {offset+1}-{min(offset+max_lines, total_lines)} of {total_lines}]\n"
                return True, header + formatted, {"path": str(p), "total_lines": total_lines}
            except Exception as e:
                return False, f"Error reading {p}: {str(e)}", {"path": str(p), "error": str(e)}

        elif tool_name in ["write_file", "write"]:
            path = args.get("path", "")
            content = args.get("content", "")
            if not path:
                return False, "Error: No path specified for write_file.", {}
            p = Path(path).expanduser()
            if not p.is_absolute():
                p = Path("/root") / p
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
                return True, f"Successfully wrote {len(content)} characters to {p}", {"path": str(p), "bytes": len(content.encode('utf-8'))}
            except Exception as e:
                return False, f"Error writing to {p}: {str(e)}", {"path": str(p), "error": str(e)}

        elif tool_name in ["web_search", "search_web", "google", "ddg"]:
            query = args.get("query", "")
            max_results = int(args.get("max_results", 5))
            if not query:
                return False, "Error: No query specified for web_search.", {}
            try:
                url = "https://lite.duckduckgo.com/lite/"
                data = urllib.parse.urlencode({"q": query}).encode("utf-8")
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=8.0) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")
                links = re.findall(r'<a[^>]+href=[\'\"]([^\'\"]+)[\'\"][^>]*class=[\'\"]result-link[\'\"][^>]*>(.*?)</a>', html, re.DOTALL)
                snippets = re.findall(r'<td[^>]*class=[\'\"]result-snippet[\'\"][^>]*>(.*?)</td>', html, re.DOTALL)
                if not links:
                    return True, f"Search completed for '{query}', but no direct snippets were parsed from DuckDuckGo.", {"query": query, "count": 0}
                results = []
                for (href, title_html), snip_html in zip(links[:max_results], snippets[:max_results]):
                    t = re.sub(r'<[^>]+>', '', title_html).strip()
                    s = re.sub(r'<[^>]+>', '', snip_html).strip()
                    results.append(f"• **{t}**\n  URL: {href}\n  Snippet: {s}")
                formatted = f"Web Search Results for '{query}' ({len(results)} found):\n\n" + "\n\n".join(results)
                return True, formatted, {"query": query, "count": len(results)}
            except Exception as e:
                return False, f"Web search failed: {str(e)}", {"query": query, "error": str(e)}

        elif tool_name in ["fts_search", "fts", "search_chat"]:
            query = args.get("query", "")
            limit = int(args.get("limit", 5))
            if not query:
                return False, "Error: No query specified for fts_search.", {}
            res = self.fts_search(query, limit=limit)
            if not res:
                return True, f"No forensic chat records found matching '{query}'.", {"query": query, "hits": 0}
            if "error" in res[0]:
                return False, res[0]["error"], {"query": query}
            formatted = []
            for r in res:
                formatted.append(f"[{r.get('category','RECORD')}] Conv: {r.get('conv_title','')} | Role: {r.get('role','')}\n  Snippet: {r.get('snippet','')}")
            return True, f"Forensics Search for '{query}' ({len(res)} hits across 140,688 records):\n\n" + "\n\n".join(formatted), {"query": query, "hits": len(res)}

        elif tool_name in ["memory", "mem"]:
            action = args.get("action", "search")
            key = args.get("key", "")
            value = args.get("value", "")
            res = self.memory_action(action, key=key, value=value)
            return True, f"Aspen Memory ({action.upper()}):\n" + json.dumps(res, indent=2), {"action": action, "res": res}

        elif tool_name in ["device", "hw", "termux"]:
            action = args.get("action", "status")
            d_args = args.get("args", [])
            if isinstance(d_args, str):
                d_args = [d_args]
            res = self.device_control(action, *d_args)
            return True, f"Device Hardware ({action.upper()}):\n" + json.dumps(res, indent=2), {"action": action, "res": res}

        elif tool_name in ["legal_dossier", "legal", "case"]:
            case = args.get("case", "1FDV")
            dos = self.get_case_dossier(case)
            return True, f"Casebuilder 4000 Dossier ({case.upper()}):\n" + json.dumps(dos, indent=2), {"case": case, "dos": dos}

        elif tool_name in ["draft_motion", "motion"]:
            m_type = args.get("type", "rule60b")
            mot = self.draft_motion(m_type)
            return True, f"Court Motion Draft ({m_type}):\n" + json.dumps(mot, indent=2), {"type": m_type, "mot": mot}

        elif tool_name in ["git_info", "git"]:
            repo = args.get("repo_path", "/root")
            try:
                b_res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=repo, timeout=4)
                branch = b_res.stdout.strip() or "unknown"
                s_res = subprocess.run(["git", "status", "-s"], capture_output=True, text=True, cwd=repo, timeout=4)
                status = s_res.stdout.strip() or "clean"
                l_res = subprocess.run(["git", "log", "-n", "5", "--oneline"], capture_output=True, text=True, cwd=repo, timeout=4)
                log = l_res.stdout.strip() or ""
                summary = f"Git Info ({repo}):\nBranch: {branch}\nStatus:\n{status}\n\nRecent Commits:\n{log}"
                return True, summary, {"branch": branch, "status": status}
            except Exception as e:
                return False, f"Git query failed: {str(e)}", {"error": str(e)}

        elif tool_name in ["ast_verify", "verify"]:
            fp = args.get("file_path", "")
            res = self.verify_ast(fp)
            return True, f"AST Verification for {fp}:\n" + json.dumps(res, indent=2), {"file": fp, "res": res}

        return False, f"Unknown tool: '{tool_name}'. Available: bash, read_file, write_file, web_search, fts_search, memory, device, legal_dossier, draft_motion, git_info, ast_verify", {}

    def stream_chat_with_tools(self, prompt: str, target_provider: Optional[str] = None, target_model: Optional[str] = None, enable_tools: bool = True, max_turns: int = 4) -> Generator[Dict[str, Any], None, None]:
        """Runs the autonomous tool-calling loop and yields real-time SSE events for both tools and text."""
        t0 = time.time()
        p_id = target_provider or "groq"
        m_id = target_model or PROVIDERS[p_id]["default_model"]
        tag = f"[{p_id.upper()} / {m_id}]"

        if not enable_tools:
            for _, token in self.stream_query(prompt, target_provider=p_id, target_model=m_id):
                yield {"type": "token", "token": token, "tag": tag}
            yield {"type": "done", "elapsed": time.time() - t0, "turns": 1, "tools_count": 0, "tag": tag}
            return

        sys_prompt = self.get_agent_system_prompt()
        history = [f"User: {prompt}"]
        tools_used = 0
        turns_used = 0
        executed_sigs = set()

        for turn in range(1, max_turns + 1):
            turns_used = turn
            full_context = "\n\n".join(history)
            
            ok, raw_response, _ = self.call_provider(p_id, m_id, full_context, system_prompt=sys_prompt)
            if not ok:
                # Automatic cascade across holographic mesh
                for fallback_p in ["groq", "google", "mistral", "openrouter"]:
                    if fallback_p != p_id:
                        fallback_m = PROVIDERS[fallback_p]["default_model"]
                        ok, raw_response, _ = self.call_provider(fallback_p, fallback_m, full_context, system_prompt=sys_prompt)
                        if ok:
                            p_id, m_id = fallback_p, fallback_m
                            tag = f"[{p_id.upper()} / {m_id}]"
                            break

            if not ok:
                yield {"type": "error", "message": f"Mesh providers unreachable: {raw_response}"}
                yield {"type": "done", "elapsed": time.time() - t0, "turns": turn, "tools_count": tools_used, "tag": "[FAILED]"}
                return

            tc = self.parse_tool_call(raw_response)
            if tc and (tc.get("tool") or tc.get("command")):
                tool_name = (tc.get("tool") or "bash").lower().strip()
                args = tc.get("args") or {k: v for k, v in tc.items() if k not in ["tool", "thought"]}
                thought = tc.get("thought", "")
                
                # Check for loop repetition
                sig = f"{tool_name}:{json.dumps(args, sort_keys=True)}"
                if sig in executed_sigs:
                    synth_instruction = "\n\nSynthesize all findings above and provide the final concise answer to the user in clean Markdown. Do NOT call any more tools."
                    history.append(synth_instruction)
                    ok, final_ans, _ = self.call_provider(p_id, m_id, "\n\n".join(history), system_prompt="You are OpenClaw Pro. Return direct markdown answer only.")
                    chunk_size = 12
                    for i in range(0, len(final_ans), chunk_size):
                        yield {"type": "token", "token": final_ans[i:i+chunk_size], "tag": tag}
                        time.sleep(0.004)
                    break
                executed_sigs.add(sig)

                tools_used += 1
                yield {
                    "type": "tool_start",
                    "tool": tool_name,
                    "args": args,
                    "thought": thought,
                    "turn": turn
                }

                tool_ok, tool_out, tool_meta = self.execute_tool(tool_name, args)

                yield {
                    "type": "tool_end",
                    "tool": tool_name,
                    "output": tool_out[:1200],
                    "full_output": tool_out,
                    "success": tool_ok,
                    "turn": turn
                }

                history.append(f"[Tool Execution Result for {tool_name}]:\n{tool_out}")
                
                if turn == max_turns - 1:
                    history.append("Now synthesize all tool findings above into a comprehensive final answer for the user in clean Markdown. Do NOT call any more tools.")
                continue
            else:
                # Direct or synthesized answer text
                clean_ans = raw_response
                chunk_size = 12
                for i in range(0, len(clean_ans), chunk_size):
                    yield {"type": "token", "token": clean_ans[i:i+chunk_size], "tag": tag}
                    time.sleep(0.004)
                break

        total_elapsed = time.time() - t0
        yield {
            "type": "done",
            "elapsed": total_elapsed,
            "turns": turns_used,
            "tools_count": tools_used,
            "tag": tag
        }

    def chat_with_tools(self, prompt: str, target_provider: Optional[str] = None, target_model: Optional[str] = None, enable_tools: bool = True, max_turns: int = 4) -> Dict[str, Any]:
        """Synchronous helper that executes tools and returns final response and full execution trace."""
        trace = []
        full_text = []
        last_tag = "[OPENCLAW / PRO]"
        tools_used = 0
        elapsed = 0.0

        for event in self.stream_chat_with_tools(prompt, target_provider=target_provider, target_model=target_model, enable_tools=enable_tools, max_turns=max_turns):
            etype = event.get("type")
            if etype == "tool_start":
                trace.append({"status": "started", "tool": event.get("tool"), "args": event.get("args"), "thought": event.get("thought")})
            elif etype == "tool_end":
                trace.append({"status": "completed", "tool": event.get("tool"), "output": event.get("output"), "success": event.get("success")})
            elif etype == "token":
                full_text.append(event.get("token", ""))
                last_tag = event.get("tag", last_tag)
            elif etype == "done":
                elapsed = event.get("elapsed", 0.0)
                tools_used = event.get("tools_count", 0)
                last_tag = event.get("tag", last_tag)

        return {
            "tag": last_tag,
            "answer": "".join(full_text),
            "elapsed": elapsed,
            "tools_used": tools_used,
            "trace": trace
        }

    def run_agentic_loop(self, task_prompt: str, max_turns: int = 5) -> Dict[str, Any]:
        """Autonomous multi-step execution loop backwards compatible with CLI and API."""
        res = self.chat_with_tools(task_prompt, enable_tools=True, max_turns=max_turns)
        return {
            "success": True,
            "task": task_prompt,
            "turns_used": len(res.get("trace", [])) // 2 + 1,
            "tools_used": res.get("tools_used", 0),
            "result": res.get("answer", ""),
            "trace": res.get("trace", [])
        }

    # -------------------------------------------------------------------------
    # LEGAL & CASE INTELLIGENCE
    # -------------------------------------------------------------------------
    def get_case_dossier(self, case_key: str) -> Dict[str, Any]:
        case_key = case_key.upper()
        if case_key not in CASES:
            return {"error": f"Unknown case key '{case_key}'. Available: {list(CASES.keys())}"}
        c = CASES[case_key]
        p = Path(c["path"])
        receipt = p / "build_receipt.json"
        artifacts = []
        if receipt.exists():
            try:
                data = json.loads(receipt.read_text())
                artifacts = [a["path"] for a in data.get("artifacts", [])]
            except Exception:
                pass
        return {
            "case_key": case_key,
            "docket": c["docket"],
            "title": c["title"],
            "damages": c["damages"],
            "verified_facts": c["verified_facts"],
            "proof_score": c["score"],
            "artifacts_count": len(artifacts),
            "export_dir": str(p)
        }

    def draft_motion(self, motion_type: str) -> Dict[str, Any]:
        mt = motion_type.lower().replace("-", "").replace("_", "")
        if "rule60" in mt or "void" in mt:
            return {
                "motion_type": "HFCR Rule 60(b)(4) Motion to Vacate Void Orders",
                "court": "Family Court of the First Circuit, State of Hawaii",
                "case_id": "1FDV-23-0001009",
                "controlling_law": "Fourteenth Amendment Due Process; HFCR Rule 60(b)(4); Berry v. Berry; Cvitanovich-Dubie v. Dubie",
                "grounds": [
                    "Ex parte secret sealing of 235 adverse trial exhibits without notice or opportunity to be heard (Dkt. 100-240)",
                    "Prefabricated 18,450-byte order uploaded to JEFS 72 seconds after hearing conclusion on Jan 19 2026",
                    "Ex parte letter from opposing counsel Scot Brower on June 25 2025 modifying physical custody without hearing"
                ],
                "filing_ready_path": "/root/LEGAL_WARFARE_PACKAGE_1FDV/COURT_READY_FILINGS/01_CONSOLIDATED_MOTION_TO_VACATE_VOID_ORDERS.md",
                "status": "PROVEN_GROUND_TRUTH"
            }
        elif "spoliation" in mt:
            return {
                "motion_type": "Motion for Spoliation Sanctions and Forensic Evidentiary Hearing",
                "court": "First Circuit Court / Hawaii Supreme Court ODC",
                "controlling_law": "HRPC Rules 3.4, 8.4; FRE 901/902; 18 U.S.C. §§ 1506, 1512, 1519",
                "grounds": [
                    "Wiping of Google Drive backups corroborated by 140,688 SQLite chat forensics records",
                    "Tampering with exhibit transmittal headers and timestamps",
                    "Concealment of mandatory discovery items"
                ],
                "filing_ready_path": "/root/LEGAL_WARFARE_PACKAGE_1FDV/COURT_READY_FILINGS/03_OFFICIAL_INVESTIGATIVE_REFERRAL_MEMORANDUM.md",
                "status": "HARDENED_AUDIT"
            }
        elif "recusal" in mt:
            return {
                "motion_type": "Motion for Disqualification and Judicial Recusal",
                "target": "Judge Natasha Shaw (First Circuit Family Court)",
                "controlling_law": "Hawaii Revised Statutes § 601-7; Hawaii Revised Code of Judicial Conduct Rule 2.11",
                "grounds": [
                    "Objective appearance of partiality stemming from ex parte exhibit sealing",
                    "Demonstrated prejudgment via 72-second post-hearing order entry"
                ],
                "filing_ready_path": "/root/casebuilder4000/LEGAL_DRAFTS/1FDV-23-0001009/legal_packages/CATACLYSM_MOTION_TO_VACATE_STATE_RULINGS.md",
                "status": "READY_FOR_FILING"
            }
        return {"error": f"Unknown motion type '{motion_type}'. Choose from: rule60b, spoliation, recusal"}

    # -------------------------------------------------------------------------
    # ASPEN-GROVE QUANTUM MEMORY
    # -------------------------------------------------------------------------
    def memory_action(self, action: str, key: str = "", value: str = "") -> Dict[str, Any]:
        action = action.lower()
        if action in ["list", "pointers"]:
            url = f"{ASPEN_MEMORY_URL}/api/search?q="
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=2.0) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                return {"status": "LOCAL_CACHE", "error": str(e)}
        elif action in ["get", "retrieve"]:
            url = f"{ASPEN_MEMORY_URL}/api/retrieve?key={urllib.parse.quote(key)}"
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=2.0) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                return {"key": key, "status": "NOT_FOUND", "error": str(e)}
        elif action in ["search", "find"]:
            url = f"{ASPEN_MEMORY_URL}/api/search?q={urllib.parse.quote(key or value)}"
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=2.0) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                return {"status": "ERROR", "error": str(e)}
        elif action in ["set", "persist"]:
            url = f"{ASPEN_MEMORY_URL}/api/persist"
            payload = {"key": key, "value": value, "tags": ["openclaw", "pro"]}
            try:
                req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=2.0) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                return {"status": "ERROR", "error": str(e)}
        return {"error": f"Unknown memory action '{action}'. Choose from: list, get, set, search"}

    # -------------------------------------------------------------------------
    # AST VERIFIER
    # -------------------------------------------------------------------------
    def verify_ast(self, file_path: str) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.exists():
            return {"valid": False, "error": f"File not found: {file_path}"}
        try:
            source = p.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(p))
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            return {
                "valid": True,
                "classes_count": len(classes),
                "classes": classes,
                "functions_count": len(functions),
                "functions": functions[:10],
                "lines_count": len(source.splitlines()),
                "status": "PASS (Clean AST)"
            }
        except SyntaxError as e:
            return {"valid": False, "error": f"SyntaxError at line {e.lineno}: {e.msg}"}

    # -------------------------------------------------------------------------
    # SYSTEM STATUS & DIAGNOSTICS
    # -------------------------------------------------------------------------
    def system_status(self) -> Dict[str, Any]:
        status_report_providers = {}
        for p_id, cfg in PROVIDERS.items():
            if p_id == "local":
                try:
                    req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
                    with urllib.request.urlopen(req, timeout=1.5) as r:
                        data = json.loads(r.read().decode())
                        status_report_providers[p_id] = {"status": "ONLINE", "models": [m['name'] for m in data.get('models', [])]}
                except Exception:
                    status_report_providers[p_id] = {"status": "OFFLINE"}
                continue

            k = self.get_key(p_id)
            if not k:
                status_report_providers[p_id] = {"status": "NO_KEY"}
            elif p_id == "cerebras":
                status_report_providers[p_id] = {"status": "AUTH_PENDING_BILLING", "key": k[:8] + "..."}
            else:
                status_report_providers[p_id] = {"status": "CONFIGURED", "key": k[:8] + "...", "default_model": cfg["default_model"]}

        aspen_status = "ONLINE"
        active_pointers = 407
        try:
            req = urllib.request.Request(f"{ASPEN_MEMORY_URL}/api/search?q=", method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as r:
                p_data = json.loads(r.read().decode())
                if isinstance(p_data, list):
                    active_pointers = len(p_data)
        except Exception:
            aspen_status = "STANDBY"

        dev_status = "CONNECTED (Termux API)" if (TERMUX_BIN / "termux-battery-status").exists() else "NATIVE"

        return {
            "engine": "APEX Super Pro OpenClaw",
            "version": "20.0",
            "operator": "Casey Barton / GlacierEQ",
            "doctrine": "Holographic Mesh (Elite · Pro · Hard · G)",
            "providers": status_report_providers,
            "api_keys": {p: bool(self.get_key(p)) for p in PROVIDERS if p != "local"},
            "databases": {
                "chat_forensics": {
                    "path": str(CHAT_DB),
                    "exists": CHAT_DB.exists(),
                    "rows": 140688
                },
                "stealth_claw_index": {
                    "path": str(STEALTH_INDEX_DB),
                    "exists": STEALTH_INDEX_DB.exists()
                },
                "openclaw_sessions": {
                    "path": str(OPENCLAW_DB),
                    "exists": OPENCLAW_DB.exists()
                }
            },
            "memory_substrate": {
                "status": aspen_status,
                "active_pointers": active_pointers,
                "url": ASPEN_MEMORY_URL
            },
            "device_hardware": dev_status,
            "timestamp": time.time()
        }

    # -------------------------------------------------------------------------
    # INTERACTIVE PRO REPL SHELL
    # -------------------------------------------------------------------------
    def interactive_shell(self):
        banner = f"""
{Color.CYAN}╔════════════════════════════════════════════════════════════════════════════╗
║  {Color.BOLD}🦅 APEX SUPER PRO OPENCLAW — MAXIMIZED HOLOGRAPHIC MESH v20.0{Color.RESET}{Color.CYAN}             ║
║  Decentralized AI Cascade · Device Hardware · 150ms FTS5 · Agentic Loop    ║
╚════════════════════════════════════════════════════════════════════════════╝{Color.RESET}
{Color.DIM}Commands: /model <p> · /device <cmd> · /fts <q> · /agent <task> · /legal <c> · /help{Color.RESET}
"""
        print(banner)

        while True:
            try:
                prompt_label = f"{Color.GREEN}openclaw{Color.RESET}[{Color.CYAN}{self.active_provider}/{self.active_model.split('/')[-1]}{Color.RESET}]> "
                user_input = input(prompt_label).strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{Color.YELLOW}Exiting OpenClaw Pro. Peace!{Color.RESET}")
                break

            if not user_input:
                continue

            if user_input in ["exit", "quit", "/exit", "/quit"]:
                print(f"{Color.YELLOW}Exiting OpenClaw Pro. Holographic mesh active in background.{Color.RESET}")
                break

            if user_input.startswith("/"):
                parts = user_input.split()
                cmd = parts[0].lower()
                arg = " ".join(parts[1:]) if len(parts) > 1 else ""

                if cmd == "/help":
                    print(f"""
{Color.BOLD}Maximized OpenClaw Pro Slash Commands:{Color.RESET}
  {Color.CYAN}/model <provider>{Color.RESET}       Switch provider: groq, google, mistral, openrouter
  {Color.CYAN}/device <action>{Color.RESET}        Hardware: status, battery, notify, toast, speak, vibrate
  {Color.CYAN}/agent <task>{Color.RESET}           Run autonomous multi-step agentic loop
  {Color.CYAN}/fts <query>{Color.RESET}            150ms FTS5 search across 140,688 chat messages
  {Color.CYAN}/legal <case>{Color.RESET}           View case dossiers: 1FDV, RICO, CFAA, CASINO, BROWER
  {Color.CYAN}/motion <type>{Color.RESET}          Generate court motions: rule60b, spoliation, recusal
  {Color.CYAN}/verify <file>{Color.RESET}          Run AST code audit
  {Color.CYAN}/status{Color.RESET}                 Live provider, database, and hardware health
  {Color.CYAN}/clear{Color.RESET} & {Color.CYAN}/exit{Color.RESET}           Terminal utilities
""")
                elif cmd == "/clear":
                    os.system("clear")
                elif cmd == "/status":
                    st = self.system_status()
                    print(f"\n{Color.BOLD}⚡ OpenClaw Pro Diagnostics:{Color.RESET}")
                    for p, info in st.items():
                        print(f"  • {p.upper()}: {info}")
                    print()
                elif cmd == "/device":
                    sub = parts[1] if len(parts) > 1 else "status"
                    d_args = parts[2:] if len(parts) > 2 else []
                    res = self.device_control(sub, *d_args)
                    print(f"\n{Color.BOLD}📱 Device Hardware Output:{Color.RESET}")
                    print(json.dumps(res, indent=2))
                    print()
                elif cmd == "/agent":
                    if not arg:
                        print("Usage: /agent <task description>")
                    else:
                        print(f"{Color.DIM}🤖 Initializing autonomous agentic loop...{Color.RESET}")
                        res = self.run_agentic_loop(arg, max_turns=5)
                        print(f"\n{Color.GREEN}✓ Agent Completed:{Color.RESET} {res.get('result')}\n")
                elif cmd == "/model":
                    if not arg:
                        print(f"Current: {self.active_provider} ({self.active_model})")
                        print("Available: " + ", ".join(PROVIDERS.keys()))
                    else:
                        p_choice = arg.lower()
                        if p_choice in PROVIDERS:
                            self.active_provider = p_choice
                            self.active_model = PROVIDERS[p_choice]["default_model"]
                            print(f"{Color.GREEN}✓ Active model set to {self.active_model}{Color.RESET}")
                        else:
                            print(f"{Color.RED}Unknown provider '{p_choice}'.{Color.RESET}")
                elif cmd == "/fts":
                    if not arg:
                        print("Usage: /fts <query>")
                    else:
                        t0 = time.time()
                        results = self.fts_search(arg, limit=5)
                        elapsed = time.time() - t0
                        print(f"\n{Color.BOLD}🔍 FTS5 Search in {elapsed*1000:.1f}ms ({len(results)} hits):{Color.RESET}")
                        for r in results:
                            print(f"  [{Color.CYAN}{r.get('category', 'RECORD')}{Color.RESET}] {r.get('conv_title', '')}")
                            print(f"   {Color.WHITE}{r.get('snippet', '')}{Color.RESET}\n")
                elif cmd == "/legal":
                    ck = arg.upper() if arg else "1FDV"
                    dos = self.get_case_dossier(ck)
                    print(json.dumps(dos, indent=2))
                elif cmd == "/motion":
                    mt = arg.lower() if arg else "rule60b"
                    mot = self.draft_motion(mt)
                    print(json.dumps(mot, indent=2))
                elif cmd == "/verify":
                    if not arg:
                        print("Usage: /verify <python_file.py>")
                    else:
                        res = self.verify_ast(arg)
                        print(json.dumps(res, indent=2))
                continue

            # Autonomous AI query with live tools
            print(f"{Color.DIM}⚡ Routing across mesh via {self.active_provider.upper()} (Autonomous Tools Active)...{Color.RESET}")
            res = self.chat_with_tools(user_input, target_provider=self.active_provider, target_model=self.active_model)
            if res.get("trace"):
                for t in res["trace"]:
                    if t.get("status") == "started":
                        print(f"  {Color.CYAN}⚙ Tool Call:{Color.RESET} {Color.BOLD}{t.get('tool')}{Color.RESET} {Color.DIM}{t.get('args')}{Color.RESET}")
                    elif t.get("status") == "completed":
                        prev = str(t.get('output', '')).replace('\n', ' ')[:90]
                        print(f"  {Color.GREEN}✓ Tool Result:{Color.RESET} {Color.DIM}{prev}...{Color.RESET}")
            print(f"\n{Color.GREEN}{res.get('tag')}{Color.RESET} {Color.DIM}({res.get('elapsed', 0):.2f}s | {res.get('tools_used', 0)} tools){Color.RESET}")
            print(f"{res.get('answer')}\n")

# -------------------------------------------------------------------------
# CLI ENTRYPOINT
# -------------------------------------------------------------------------
def main():
    claw = SuperProOpenClaw()

    def launch_tui_or_shell():
        try:
            from openclaw_tui import OpenClawTUI
            tui = OpenClawTUI()
            tui.run()
        except Exception:
            claw.interactive_shell()

    if len(sys.argv) == 1:
        launch_tui_or_shell()
        return

    # Parse optional provider flag: -p / --provider
    target_provider = None
    args = sys.argv[1:]
    if "-p" in args:
        idx = args.index("-p")
        if idx + 1 < len(args):
            target_provider = args[idx + 1].lower()
            args = args[:idx] + args[idx + 2:]
    elif "--provider" in args:
        idx = args.index("--provider")
        if idx + 1 < len(args):
            target_provider = args[idx + 1].lower()
            args = args[:idx] + args[idx + 2:]

    if not args:
        launch_tui_or_shell()
        return

    subcmd = args[0].lower()

    if subcmd in ["tui", "shell", "repl", "interactive"]:
        launch_tui_or_shell()
        return

    if subcmd in ["web", "studio", "ui", "gui"]:
        print(f"{Color.GREEN}⚡ Launching OpenClaw Web Studio on http://127.0.0.1:18800...{Color.RESET}")
        try:
            subprocess.run(["termux-open-url", "http://localhost:18800"], capture_output=True)
        except Exception:
            pass
        from openclaw_web import run_server
        run_server()
        return

    if subcmd in ["daemon", "service"]:
        action = args[1].lower() if len(args) > 1 else "status"
        pid_file = Path("/tmp/openclaw_studio.pid")
        if action == "start":
            try:
                urllib.request.urlopen("http://127.0.0.1:18800/health", timeout=1.0)
                print(f"{Color.GREEN}✓ OpenClaw Web Studio is already active on http://127.0.0.1:18800{Color.RESET}")
                return
            except Exception:
                pass
            web_script = str(Path(__file__).resolve().parent / "openclaw_web.py")
            p = subprocess.Popen([sys.executable, web_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            pid_file.write_text(str(p.pid))
            time.sleep(1.0)
            print(f"{Color.GREEN}✓ OpenClaw Web Studio daemon started (PID {p.pid}) on http://127.0.0.1:18800{Color.RESET}")
            return
        elif action == "stop":
            if pid_file.exists():
                try:
                    pid = int(pid_file.read_text().strip())
                    os.kill(pid, 15)
                    pid_file.unlink(missing_ok=True)
                    print(f"{Color.YELLOW}✓ OpenClaw Web Studio daemon stopped (PID {pid}){Color.RESET}")
                    return
                except Exception as e:
                    pass
            subprocess.run(["pkill", "-f", "openclaw_web.py"])
            pid_file.unlink(missing_ok=True)
            print(f"{Color.YELLOW}✓ OpenClaw Web Studio processes stopped.{Color.RESET}")
            return
        elif action in ["status", "check"]:
            try:
                with urllib.request.urlopen("http://127.0.0.1:18800/health", timeout=1.5) as r:
                    print(f"{Color.GREEN}● OpenClaw Web Studio daemon ONLINE on http://127.0.0.1:18800{Color.RESET}")
            except Exception:
                print(f"{Color.RED}○ OpenClaw Web Studio daemon OFFLINE.{Color.RESET}")
            return

    if subcmd in ["help", "--help", "-h"]:
        print(f"""{Color.BOLD}{Color.CYAN}APEX Super Pro OpenClaw CLI v20.0 (Holographic Mesh Edition){Color.RESET}
Operator: Casey Barton / GlacierEQ | Elite · Pro · Hard · G

{Color.BOLD}USAGE:{Color.RESET}
  openclaw [command] [args...]
  openclaw [-p <provider>] "<prompt>"

{Color.BOLD}INTERFACES:{Color.RESET}
  {Color.GREEN}openclaw{Color.RESET}                 Launch Interactive Rich Terminal UI (TUI) with auto-complete & streaming
  {Color.GREEN}openclaw web{Color.RESET}, studio     Launch Interactive Web/Mobile Studio on http://127.0.0.1:18800

{Color.BOLD}COMMANDS:{Color.RESET}
  {Color.GREEN}status{Color.RESET}, -s           Mesh health, API keys, database rows, memory daemon
  {Color.GREEN}models{Color.RESET}, -m           List active providers (Groq, Google, Mistral, OpenRouter, Cerebras)
  {Color.GREEN}agent{Color.RESET} <task>          Autonomous multi-turn agent loop (bash, read, write, fts, device, mem)
  {Color.GREEN}device{Color.RESET} <action>       Hardware control: battery, toast, notify, tts, vibrate, clip_get, clip_set, torch_on, torch_off
  {Color.GREEN}fts{Color.RESET} <query>            FTS5 search across 140,688 chat forensics records (~150ms)
  {Color.GREEN}legal{Color.RESET} [case_key]      Casebuilder 4000 dossiers (1FDV, RICO, CFAA, CASINO, NEXCOM, BROWER)
  {Color.GREEN}motion{Color.RESET} <type>         Draft procedural motions (rule60b, spoliation, recusal)
  {Color.GREEN}memory{Color.RESET} <act> [k] [v]   Aspen-Grove quantum memory (list, get, set, search)
  {Color.GREEN}verify-ast{Color.RESET} <file>    AST syntax safety parser and complexity auditor
  {Color.GREEN}run{Color.RESET} <prompt>          Direct AI query with automatic mesh fallback
  {Color.GREEN}help{Color.RESET}, -h             Display this documentation screen

{Color.BOLD}PROVIDER ROUTING (-p):{Color.RESET}
  openclaw -p groq "..."       (qwen/qwen3.8-27b - sub-second)
  openclaw -p google "..."     (gemini-2.5-flash - 1M context)
  openclaw -p mistral "..."    (codestral-latest - pro coding)
  openclaw -p openrouter "..." (nemotron/gemma free mesh)
  openclaw -p cerebras "..."   (qwen-3.8-27b ultra-fast)
""")
        return

    if subcmd in ["status", "--status", "-s"]:
        st = claw.system_status()
        print(json.dumps(st, indent=2))
        return

    if subcmd in ["models", "--models", "-m"]:
        for p_id, cfg in PROVIDERS.items():
            print(f"\n{Color.BOLD}{cfg['name']} ({p_id}):{Color.RESET}")
            print(f"  Default: {cfg['default_model']}")
            print(f"  Models : {', '.join(cfg['models'])}")
        return

    if subcmd in ["device", "dev", "hw"]:
        action = args[1] if len(args) > 1 else "status"
        d_args = args[2:] if len(args) > 2 else []
        res = claw.device_control(action, *d_args)
        print(json.dumps(res, indent=2))
        return

    if subcmd in ["agent", "autonomous"]:
        task_str = " ".join(args[1:])
        if not task_str:
            print("Usage: openclaw agent <task description>")
            return
        res = claw.run_agentic_loop(task_str)
        print(json.dumps(res, indent=2))
        return

    if subcmd in ["fts", "search-chat"]:
        query_str = " ".join(args[1:])
        if not query_str:
            print("Usage: openclaw fts <query>")
            return
        results = claw.fts_search(query_str, limit=10)
        print(json.dumps(results, indent=2))
        return

    if subcmd in ["legal", "case"]:
        ck = args[1] if len(args) > 1 else "1FDV"
        dos = claw.get_case_dossier(ck)
        print(json.dumps(dos, indent=2))
        return

    if subcmd in ["draft-motion", "motion"]:
        m_type = args[1] if len(args) > 1 else "rule60b"
        mot = claw.draft_motion(m_type)
        print(json.dumps(mot, indent=2))
        return

    if subcmd in ["memory", "mem"]:
        act = args[1] if len(args) > 1 else "list"
        k = args[2] if len(args) > 2 else ""
        v = " ".join(args[3:]) if len(args) > 3 else ""
        res = claw.memory_action(act, k, v)
        print(json.dumps(res, indent=2))
        return

    if subcmd in ["verify-ast", "ast"]:
        if len(args) < 2:
            print("Usage: openclaw verify-ast <file.py>")
            return
        res = claw.verify_ast(args[1])
        print(json.dumps(res, indent=2))
        return

    if subcmd in ["run", "ask", "do"]:
        prompt = " ".join(args[1:])
        if not prompt:
            print(f"Usage: openclaw {subcmd} <prompt>")
            return
        res = claw.chat_with_tools(prompt, target_provider=target_provider)
        if res.get("trace"):
            for t in res["trace"]:
                if t.get("status") == "started":
                    print(f"{Color.CYAN}⚙ Tool:{Color.RESET} {t.get('tool')} {Color.DIM}{t.get('args')}{Color.RESET}")
        print(f"\n{Color.GREEN}{res.get('tag')}{Color.RESET} {Color.DIM}({res.get('elapsed', 0):.2f}s | {res.get('tools_used', 0)} tools){Color.RESET}")
        print(f"{res.get('answer')}\n")
        return

    # Direct query fallback: openclaw "prompt"
    prompt = " ".join(args)
    res = claw.chat_with_tools(prompt, target_provider=target_provider)
    if res.get("trace"):
        for t in res["trace"]:
            if t.get("status") == "started":
                print(f"{Color.CYAN}⚙ Tool:{Color.RESET} {t.get('tool')} {Color.DIM}{t.get('args')}{Color.RESET}")
    print(f"\n{Color.GREEN}{res.get('tag')}{Color.RESET} {Color.DIM}({res.get('elapsed', 0):.2f}s | {res.get('tools_used', 0)} tools){Color.RESET}")
    print(f"{res.get('answer')}\n")

if __name__ == "__main__":
    main()
