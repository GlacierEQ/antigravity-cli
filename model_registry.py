#!/usr/bin/env python3
"""
Antigravity Central Model Registry & Provider Orchestrator v1.0
Enables dynamic addition, configuration, alias routing, and execution across all major AI models.
Supports Gemini, Anthropic, OpenAI, Groq, DeepSeek, Ollama, and custom user models.
Integrated directly with Supabase Vault for zero-hardcode credential management.
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional

# Integrate with Supabase Vault Client (Universal Resolution)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.expanduser("~"))
sys.path.insert(0, "/root")

try:
    from supabase_vault_client import SupabaseVaultClient
    vault = SupabaseVaultClient()
except Exception:
    vault = None

class ModelRegistry:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(SCRIPT_DIR, "models_config.json")
        self.models: Dict[str, Dict[str, Any]] = {}
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.aliases: Dict[str, str] = {}
        self._load_default_registry()
        self._load_custom_config()

    def _load_default_registry(self):
        """Pre-populate sovereign models across major providers."""
        self.providers = {
            "google": {
                "name": "Google Gemini",
                "api_key_env": "GEMINI_API_KEY",
                "vault_keys": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
                "base_url": "https://generativelanguage.googleapis.com/v1beta"
            },
            "anthropic": {
                "name": "Anthropic Claude",
                "api_key_env": "ANTHROPIC_API_KEY",
                "vault_keys": ["ANTHROPIC_API_KEY"],
                "base_url": "https://api.anthropic.com/v1"
            },
            "openai": {
                "name": "OpenAI",
                "api_key_env": "OPENAI_API_KEY",
                "vault_keys": ["OPENAI_API_KEY"],
                "base_url": "https://api.openai.com/v1"
            },
            "groq": {
                "name": "Groq Cloud",
                "api_key_env": "GROQ_API_KEY",
                "vault_keys": ["GROQ_API_KEY"],
                "base_url": "https://api.groq.com/openai/v1"
            },
            "deepseek": {
                "name": "DeepSeek AI",
                "api_key_env": "DEEPSEEK_API_KEY",
                "vault_keys": ["DEEPSEEK_API_KEY", "DEEPSEEK_API_KEY2"],
                "base_url": "https://api.deepseek.com/v1"
            },
            "openrouter": {
                "name": "OpenRouter Free Mesh",
                "api_key_env": "OPENROUTER_API_KEY",
                "vault_keys": ["OPENROUTER_API_KEY", "OPENROUTER_API_KEY2", "OPENROUTER_MANAGEMENT_KEY"],
                "base_url": "https://openrouter.ai/api/v1"
            },
            "mimo": {
                "name": "MiMo Code Engine",
                "api_key_env": "MIMO_API_KEY",
                "vault_keys": ["MIMO_API_KEY", "MIMO_V2_PRO_KEY", "MIMO_GLASS_API_KEY"],
                "base_url": "https://api.mimo.com/v1"
            },
            "kilo": {
                "name": "Kilo Code Engine",
                "api_key_env": "KILO_CODE_KEY",
                "vault_keys": ["KILO_CODE_KEY"],
                "base_url": "https://api.kilo.ai/v1"
            },
            "highlight": {
                "name": "Highlight AI Mesh",
                "api_key_env": "HIGHLIGHTAI_JWT",
                "vault_keys": ["HIGHLIGHTAI_JWT", "HIGHLIGHT_AI_TOKEN"],
                "base_url": "https://api.highlight.ai/v1"
            },
            "local_ollama": {
                "name": "Local Ollama Engine",
                "api_key_env": None,
                "base_url": "http://localhost:11434/v1"
            }
        }

        # Pre-populate sovereign models
        default_models = [
            # Google Gemini
            {"id": "gemini-3.6-flash", "name": "Gemini 3.6 Flash (High)", "provider": "google", "tier": "flash", "context_window": 1048576, "aliases": ["3.6-flash", "flash-high", "default-flash"]},
            {"id": "gemini-3.5-pro", "name": "Gemini 3.5 Pro", "provider": "google", "tier": "pro", "context_window": 2097152, "aliases": ["3.5-pro", "gemini-pro"]},
            {"id": "gemini-3.5-flash", "name": "Gemini 3.5 Flash", "provider": "google", "tier": "flash", "context_window": 1048576, "aliases": ["3.5-flash"]},
            {"id": "gemini-flash-lite", "name": "Gemini Flash Lite", "provider": "google", "tier": "flash_lite", "context_window": 524288, "aliases": ["flash-lite"]},

            # Anthropic Claude
            {"id": "claude-3-7-sonnet", "name": "Claude 3.7 Sonnet (Hybrid Reasoning)", "provider": "anthropic", "tier": "pro", "context_window": 200000, "aliases": ["claude-3.7", "3.7-sonnet", "sonnet-3.7"]},
            {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet", "provider": "anthropic", "tier": "pro", "context_window": 200000, "aliases": ["claude-3.5", "sonnet"]},
            {"id": "claude-3-5-haiku", "name": "Claude 3.5 Haiku", "provider": "anthropic", "tier": "flash", "context_window": 200000, "aliases": ["haiku"]},

            # OpenAI
            {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai", "tier": "pro", "context_window": 128000, "aliases": ["4o", "gpt4o"]},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "openai", "tier": "flash", "context_window": 128000, "aliases": ["4o-mini"]},
            {"id": "o3-mini", "name": "OpenAI o3-mini Reasoning", "provider": "openai", "tier": "pro", "context_window": 200000, "aliases": ["o3"]},

            # Groq & DeepSeek
            {"id": "deepseek-r1-distill-llama-70b", "name": "DeepSeek R1 Distill (Groq)", "provider": "groq", "tier": "pro", "context_window": 128000, "aliases": ["deepseek-r1", "r1"]},
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B (Groq)", "provider": "groq", "tier": "pro", "context_window": 128000, "aliases": ["llama-3.3", "llama-70b"]},
            {"id": "deepseek-chat", "name": "DeepSeek V3 Chat", "provider": "deepseek", "tier": "pro", "context_window": 64000, "aliases": ["deepseek-v3"]},

            # Local Models
            {"id": "qwen2.5-coder-7b", "name": "Qwen 2.5 Coder 7B (Local)", "provider": "local_ollama", "tier": "flash", "context_window": 32768, "aliases": ["qwen-coder", "local-coder"]}
        ]

        for m in default_models:
            self.register_model(m)

    def _load_custom_config(self):
        """Load user-defined models or custom config JSON if available."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    for m in data.get("models", []):
                        self.register_model(m)
                    for alias, target in data.get("aliases", {}).items():
                        self.aliases[alias.lower()] = target
            except Exception as e:
                print(f"Notice loading custom model config: {e}")

    def save_custom_config(self):
        """Persist user custom models and aliases to JSON config."""
        data = {
            "models": list(self.models.values()),
            "aliases": self.aliases
        }
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    def register_model(self, model_info: Dict[str, Any]):
        """Register or update a model definition dynamically."""
        model_id = model_info["id"].lower()
        self.models[model_id] = model_info
        for alias in model_info.get("aliases", []):
            self.aliases[alias.lower()] = model_id

    def add_alias(self, alias: str, target_model_id: str):
        """Add a custom shortcut alias for a model."""
        target_id = self.resolve_model(target_model_id)
        if target_id:
            self.aliases[alias.lower()] = target_id
            self.save_custom_config()
            return True
        return False

    def resolve_model(self, name_or_alias: str) -> Optional[str]:
        """Resolve an alias or model name to exact model_id."""
        query = name_or_alias.lower().strip()
        if query in self.models:
            return query
        if query in self.aliases:
            return self.aliases[query]
        # Partial match fallback
        for mid in self.models:
            if query in mid:
                return mid
        return None

    def get_model_info(self, name_or_alias: str) -> Optional[Dict[str, Any]]:
        mid = self.resolve_model(name_or_alias)
        return self.models.get(mid) if mid else None

    def get_api_key(self, provider_id: str) -> Optional[str]:
        """Fetch active API key for provider from environment or Supabase Vault."""
        prov = self.providers.get(provider_id)
        if not prov:
            return None
        
        # Check environment first
        env_var = prov.get("api_key_env")
        if env_var and os.getenv(env_var):
            return os.getenv(env_var)
            
        # Fallback to Supabase Vault lookup
        if vault:
            for vk in prov.get("vault_keys", []):
                val = vault.get_key(vk)
                if val:
                    return val
        return None

    def list_models(self, provider_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List registered models with active key status."""
        result = []
        for m_id, m in self.models.items():
            prov_id = m["provider"]
            if provider_filter and prov_id.lower() != provider_filter.lower():
                continue
            has_key = bool(self.get_api_key(prov_id)) if prov_id != "local_ollama" else True
            item = dict(m)
            item["has_active_key"] = has_key
            result.append(item)
        return result

if __name__ == "__main__":
    reg = ModelRegistry()
    print("=== ANTIGRAVITY CENTRAL MODEL REGISTRY ===")
    models = reg.list_models()
    print(f"Total Registered Models: {len(models)}\n")
    
    print(f"{'Model ID':<32} | {'Provider':<12} | {'Tier':<10} | {'Vault Key Status'}")
    print("-" * 75)
    for m in models:
        key_status = "🟢 ACTIVE" if m["has_active_key"] else "🔴 MISSING KEY"
        print(f"{m['id']:<32} | {m['provider']:<12} | {m['tier']:<10} | {key_status}")
    
    print("\n--- ALIAS RESOLUTION TEST ---")
    test_aliases = ["3.6-flash", "claude-3.7", "4o", "r1", "sonnet"]
    for a in test_aliases:
        resolved = reg.resolve_model(a)
        print(f"Alias '{a:<12}' -> Resolved Model ID: '{resolved}'")
    print("==========================================")
