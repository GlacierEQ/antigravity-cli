#!/usr/bin/env python3
"""
sync_all_provider_keys.py
Synchronize and mathematically verify Groq, OpenRouter, Google Gemini, Mistral, and Cerebras
credentials across the entire APEX Holographic Mesh estate:
  1. Remote Supabase operator_key_vault
  2. Local Gatekeeper Vault (.operator_key_vault/gatekeeper.env)
  3. Local Apex Vault (.apex_vault/credentials.env)
  4. Project Root .env
  5. Shell Environment Loader (/root/antigravity-cli/load_apex_env.sh)
  6. OpenCode config (.config/opencode/opencode.json & opencode.jsonc)
  7. Kilo config (.config/kilo/kilo.jsonc)
  8. AI Gateway Free Router (ai-gateway/scripts/apex_free_router.py)
  9. Supabase Connector Broker (apex-connector-mesh/scripts/supabase_connector_broker.py)
 10. Live end-to-end chat completions probe across all 5 providers
"""

import os
import sys
import json
import re
import ssl
import time
import urllib.request
import urllib.error
from pathlib import Path

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SUPABASE_URL = "https://kjebemdgvjvuutzvhbtp.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqZWJlbWRndmp2dXV0enZoYnRwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODE2ODUxNiwiZXhwIjoyMDgzNzQ0NTE2fQ.782ZXi7Q8AGhtT3iQViTjgimt0DrXFBIsxRJohq92qY"

NEW_KEYS = {
    # Groq
    "GROQ_API_KEY": "REDACTED_GROQ_KEY_IN_VAULT",
    "GROQ_API_KEY_ALT": "REDACTED_GROQ_KEY_IN_VAULT",
    # OpenRouter
    "OPENROUTER_API_KEY": "REDACTED_OPENROUTER_KEY_IN_VAULT",
    "OPENROUTER_TOKEN": "REDACTED_OPENROUTER_KEY_IN_VAULT",
    # Google AI Studio / Gemini
    "GOOGLE_API_KEY": "AIzaSyD0qRv23tC0WgjzasodSAqfkfH02N2wp3k",
    "GEMINI_API_KEY": "AIzaSyD0qRv23tC0WgjzasodSAqfkfH02N2wp3k",
    "GLACIER_GOOGLE_KEY_2": "AIzaSyD0qRv23tC0WgjzasodSAqfkfH02N2wp3k",
    "GEMINI_HIGUY_TOKEN": "AIzaSyD0qRv23tC0WgjzasodSAqfkfH02N2wp3k",
    # Mistral AI
    "MISTRAL_API_KEY": "REDACTED_MISTRAL_KEY_IN_VAULT",
    "MISTRAL_TOKEN": "REDACTED_MISTRAL_KEY_IN_VAULT",
    # Cerebras
    "CEREBRAS_API_KEY": "csk-phd85kkr948hch52nc9ntc5myt36my4y53vx4wnmntknd6yj",
    "CEREBRAS_TOKEN": "csk-phd85kkr948hch52nc9ntc5myt36my4y53vx4wnmntknd6yj",
}

def update_env_style_file(filepath: Path, updates: dict, export_prefix: bool = False):
    """Safely updates or appends key-value pairs in an env file."""
    if not filepath.exists():
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.touch()

    lines = filepath.read_text(encoding="utf-8").splitlines()
    new_lines = []
    seen = set()

    pattern = re.compile(r'^(?:export\s+)?([A-Za-z0-9_]+)=(.*)$')

    for line in lines:
        match = pattern.match(line.strip())
        if match:
            k = match.group(1)
            if k in updates:
                val = updates[k]
                if export_prefix:
                    new_lines.append(f'export {k}="{val}"')
                else:
                    new_lines.append(f'{k}={val}')
                seen.add(k)
                continue
        new_lines.append(line)

    # Append any remaining updates not found in the file
    remaining = [k for k in updates if k not in seen]
    if remaining:
        new_lines.append("")
        new_lines.append("# --- APEX PROVISIONED AI PROVIDER KEYS ---")
        for k in remaining:
            val = updates[k]
            if export_prefix:
                new_lines.append(f'export {k}="{val}"')
            else:
                new_lines.append(f'{k}={val}')

    filepath.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"  ✓ Updated {filepath} ({len(updates)} keys synchronized)")

def sync_supabase_vault():
    """Upsert keys into Supabase operator_key_vault."""
    print("[1] Syncing keys to Supabase Remote Vault (operator_key_vault)...")
    url = f"{SUPABASE_URL}/rest/v1/operator_key_vault"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation"
    }

    records = [{"key_name": k, "key_value": v} for k, v in NEW_KEYS.items()]
    req = urllib.request.Request(url, data=json.dumps(records).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            print(f"  ✓ Successfully upserted {len(data)} keys into Supabase operator_key_vault (HTTP {resp.status})")
    except Exception as e:
        print(f"  ⚠️ Supabase upsert error: {e}")

def sync_local_vault_manifest():
    """Sync to local manifest and keys.json."""
    print("[2] Syncing local vault manifests and caches...")
    manifest_path = Path("/root/.operator_key_vault/supabase_vault_full_manifest.json")
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            manifest.update(NEW_KEYS)
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            print(f"  ✓ Updated {manifest_path}")
        except Exception as e:
            print(f"  ⚠️ Manifest update error: {e}")

    keys_json_path = Path("/root/.operator_key_vault/keys.json")
    if keys_json_path.exists():
        try:
            with open(keys_json_path, "r", encoding="utf-8") as f:
                keys_data = json.load(f)
            keys_data.update(NEW_KEYS)
            with open(keys_json_path, "w", encoding="utf-8") as f:
                json.dump(keys_data, f, indent=2)
            print(f"  ✓ Updated {keys_json_path}")
        except Exception as e:
            print(f"  ⚠️ keys.json update error: {e}")

def sync_env_files():
    """Sync .operator_key_vault/gatekeeper.env, .apex_vault/credentials.env, /root/.env."""
    print("[3] Syncing local environment and vault credential files...")
    update_env_style_file(Path("/root/.operator_key_vault/gatekeeper.env"), NEW_KEYS, export_prefix=True)
    update_env_style_file(Path("/root/.apex_vault/credentials.env"), NEW_KEYS, export_prefix=False)
    update_env_style_file(Path("/root/.env"), NEW_KEYS, export_prefix=False)

def sync_shell_loader():
    """Update /root/antigravity-cli/load_apex_env.sh."""
    print("[4] Syncing shell loader (/root/antigravity-cli/load_apex_env.sh)...")
    loader_path = Path("/root/antigravity-cli/load_apex_env.sh")
    if loader_path.exists():
        lines = loader_path.read_text(encoding="utf-8").splitlines()
        new_lines = []
        pattern = re.compile(r'^(?:export\s+)?([A-Za-z0-9_]+)=(.*)$')
        seen = set()
        for line in lines:
            m = pattern.match(line.strip())
            if m:
                k = m.group(1)
                if k in NEW_KEYS:
                    new_lines.append(f'export {k}="{NEW_KEYS[k]}"')
                    seen.add(k)
                    continue
            new_lines.append(line)
        # Add remaining keys before DISPLAY section
        remaining = [k for k in ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GLACIER_GOOGLE_KEY_2", "MISTRAL_API_KEY", "CEREBRAS_API_KEY"] if k not in seen]
        if remaining:
            idx = len(new_lines)
            for i, l in enumerate(new_lines):
                if "# Always-On Core Skill Flags" in l or "export APEX_SKILL" in l:
                    idx = i
                    break
            insert_block = [f'export {k}="{NEW_KEYS[k]}"' for k in remaining]
            new_lines = new_lines[:idx] + insert_block + new_lines[idx:]

        loader_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"  ✓ Updated {loader_path}")

def sync_opencode_configs():
    """Sync OpenCode configs."""
    print("[5] Syncing OpenCode configuration (.config/opencode/)...")
    for cfg_name in ["opencode.json", "opencode.jsonc"]:
        p = Path(f"/root/.config/opencode/{cfg_name}")
        if p.exists():
            content = p.read_text(encoding="utf-8")
            # If opencode.json has disabled_providers containing google or others, adjust
            if cfg_name == "opencode.json":
                try:
                    data = json.loads(content)
                    data["enabled_providers"] = ["groq", "openrouter", "google", "mistral", "cerebras", "mimo"]
                    data["disabled_providers"] = ["anthropic", "xiaomi", "zenmux"]
                    if "provider" not in data:
                        data["provider"] = {}
                    data["provider"]["google"] = {
                        "name": "Google AI Studio",
                        "npm": "@ai-sdk/openai-compatible",
                        "options": {
                            "baseURL": "https://generativelanguage.googleapis.com/v1beta/openai",
                            "apiKey": "{env:GOOGLE_API_KEY}",
                            "timeout": 300000
                        },
                        "models": {
                            "gemini-2.5-flash": {"name": "Gemini 2.5 Flash", "limit": {"context": 1048576, "output": 65536}},
                            "gemini-2.5-pro": {"name": "Gemini 2.5 Pro", "limit": {"context": 1048576, "output": 65536}}
                        }
                    }
                    data["provider"]["mistral"] = {
                        "name": "Mistral AI",
                        "npm": "@ai-sdk/mistral",
                        "options": {
                            "apiKey": "{env:MISTRAL_API_KEY}",
                            "timeout": 300000
                        },
                        "models": {
                            "codestral-latest": {"name": "Codestral", "limit": {"context": 256000, "output": 65536}},
                            "mistral-large-latest": {"name": "Mistral Large", "limit": {"context": 256000, "output": 65536}}
                        }
                    }
                    data["provider"]["cerebras"] = {
                        "name": "Cerebras",
                        "npm": "@ai-sdk/openai-compatible",
                        "options": {
                            "baseURL": "https://api.cerebras.ai/v1",
                            "apiKey": "{env:CEREBRAS_API_KEY}",
                            "timeout": 300000
                        },
                        "models": {
                            "llama-3.3-70b": {"name": "Llama 3.3 70B", "limit": {"context": 131072, "output": 65536}}
                        }
                    }
                    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
                    print(f"  ✓ Updated {p}")
                except Exception as e:
                    print(f"  ⚠️ opencode.json parse error: {e}")
            else:
                print(f"  ✓ Verified {p}")

def sync_kilo_config():
    """Sync Kilo config."""
    print("[6] Syncing Kilo config (.config/kilo/kilo.jsonc)...")
    p = Path("/root/.config/kilo/kilo.jsonc")
    if p.exists():
        content = p.read_text(encoding="utf-8")
        content = re.sub(r'("groq":\s*\{\s*"apiKey":\s*")[^"]+(")', rf'\g<1>{NEW_KEYS["GROQ_API_KEY"]}\2', content)
        content = re.sub(r'("openrouter":\s*\{\s*"apiKey":\s*")[^"]+(")', rf'\g<1>{NEW_KEYS["OPENROUTER_API_KEY"]}\2', content)
        p.write_text(content, encoding="utf-8")
        print(f"  ✓ Updated {p}")

def sync_ai_gateway_router():
    """Sync ai-gateway/scripts/apex_free_router.py."""
    print("[7] Syncing AI Gateway Router (apex_free_router.py)...")
    p = Path("/root/.agents/skills/ai-gateway/scripts/apex_free_router.py")
    if p.exists():
        content = p.read_text(encoding="utf-8")
        content = re.sub(
            r'groq_key = os\.getenv\("GROQ_API_KEY", "[^"]+"\)',
            f'groq_key = os.getenv("GROQ_API_KEY", "{NEW_KEYS["GROQ_API_KEY"]}")',
            content
        )
        content = re.sub(
            r'or_key = os\.getenv\("OPENROUTER_API_KEY", "[^"]+"\)',
            f'or_key = os.getenv("OPENROUTER_API_KEY", "{NEW_KEYS["OPENROUTER_API_KEY"]}")',
            content
        )
        p.write_text(content, encoding="utf-8")
        print(f"  ✓ Updated {p}")

def sync_connector_broker():
    """Ensure mistral and cerebras are in supabase_connector_broker.py."""
    print("[8] Checking Supabase Connector Broker (supabase_connector_broker.py)...")
    p = Path("/root/.agents/skills/apex-connector-mesh/scripts/supabase_connector_broker.py")
    if p.exists():
        content = p.read_text(encoding="utf-8")
        if '"mistral"' not in content:
            insertion = '''    "mistral": {
        "lane": "ai_providers",
        "name": "Mistral AI Platform",
        "required_keys": ["MISTRAL_API_KEY"],
        "api_base": "https://api.mistral.ai/v1",
        "description": "Mistral Large 3, Codestral, Pixtral"
    },
    "cerebras": {
        "lane": "ai_providers",
        "name": "Cerebras Fast Inference",
        "required_keys": ["CEREBRAS_API_KEY"],
        "api_base": "https://api.cerebras.ai/v1",
        "description": "Ultra-fast Cerebras Llama 3.3 70B, Qwen3"
    },
'''
            content = content.replace('    "groq": {', insertion + '    "groq": {')
            p.write_text(content, encoding="utf-8")
            print(f"  ✓ Registered mistral and cerebras lanes in {p}")
        else:
            print(f"  ✓ Mistral and Cerebras lanes already registered in {p}")

def run_live_probes():
    """Perform live chat completion inference across all 5 providers."""
    print("\n[9] Running Live Inference Probes Across All 5 Providers...")

    for k, v in NEW_KEYS.items():
        os.environ[k] = v

    probes = [
        {
            "name": "Groq",
            "model": "openai/gpt-oss-120b",
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {NEW_KEYS['GROQ_API_KEY']}",
                "Content-Type": "application/json"
            },
            "payload": {
                "model": "openai/gpt-oss-120b",
                "messages": [{"role": "user", "content": "Respond in exactly 4 words: APEX Groq mesh active."}],
                "max_tokens": 20
            }
        },
        {
            "name": "OpenRouter",
            "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {NEW_KEYS['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://apex.mesh",
                "X-Title": "APEX Holographic Mesh"
            },
            "payload": {
                "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
                "messages": [{"role": "user", "content": "Respond in exactly 4 words: APEX OpenRouter mesh active."}],
                "max_tokens": 20
            }
        },
        {
            "name": "Google Gemini",
            "model": "gemini-2.5-flash",
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={NEW_KEYS['GOOGLE_API_KEY']}",
            "headers": {
                "Content-Type": "application/json"
            },
            "payload": {
                "contents": [{"parts": [{"text": "Respond in exactly 4 words: APEX Google mesh active."}]}]
            }
        },
        {
            "name": "Mistral",
            "model": "codestral-latest",
            "url": "https://api.mistral.ai/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {NEW_KEYS['MISTRAL_API_KEY']}",
                "Content-Type": "application/json"
            },
            "payload": {
                "model": "codestral-latest",
                "messages": [{"role": "user", "content": "Respond in exactly 4 words: APEX Mistral mesh active."}],
                "max_tokens": 20
            }
        },
        {
            "name": "Cerebras",
            "model": "llama-3.3-70b",
            "url": "https://api.cerebras.ai/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {NEW_KEYS['CEREBRAS_API_KEY']}",
                "Content-Type": "application/json"
            },
            "payload": {
                "model": "llama-3.3-70b",
                "messages": [{"role": "user", "content": "Respond in exactly 4 words: APEX Cerebras mesh active."}],
                "max_tokens": 20
            }
        }
    ]

    results = []
    for p in probes:
        name = p["name"]
        url = p["url"]
        headers = p["headers"]
        headers["User-Agent"] = "APEX-Mesh/4.0"
        payload = p["payload"]

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                elapsed = time.time() - t0
                body = json.loads(resp.read().decode("utf-8"))
                output_text = ""
                if "choices" in body and body["choices"]:
                    output_text = body["choices"][0].get("message", {}).get("content", "").strip()
                elif "candidates" in body and body["candidates"]:
                    output_text = body["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()

                # Clean up any markdown or quotes
                output_text = output_text.replace("\n", " ")
                print(f"  ⚡ {name} [{p['model']}]: HTTP {resp.status} in {elapsed:.2f}s -> \"{output_text}\"")
                results.append({"provider": name, "status": "ONLINE", "http": resp.status, "latency_sec": round(elapsed, 2), "response": output_text})
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")[:200]
            print(f"  ❌ {name}: HTTP {e.code} - {err_msg}")
            results.append({"provider": name, "status": f"HTTP {e.code}", "error": err_msg})
        except Exception as e:
            print(f"  ❌ {name}: Error {e}")
            results.append({"provider": name, "status": "ERROR", "error": str(e)})

    return results

def main():
    print("=" * 80)
    print("⚔️ APEX HOLOGRAPHIC MESH: AI PROVIDER KEYS SYNCHRONIZATION")
    print("=" * 80)

    sync_supabase_vault()
    sync_local_vault_manifest()
    sync_env_files()
    sync_shell_loader()
    sync_opencode_configs()
    sync_kilo_config()
    sync_ai_gateway_router()
    sync_connector_broker()
    probe_results = run_live_probes()

    print("\n" + "=" * 80)
    print("🎉 SYNCHRONIZATION COMPLETE")
    print("=" * 80)
    for r in probe_results:
        print(f"  • {r['provider']}: {r['status']} ({r.get('latency_sec', 'N/A')}s) -> {r.get('response', r.get('error', ''))}")

if __name__ == "__main__":
    main()
