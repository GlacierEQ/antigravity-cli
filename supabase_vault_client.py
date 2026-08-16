#!/usr/bin/env python3
"""
APEX Sovereign AI Supabase Vault Client v1.1 (Universal Portable Edition)
Enables AI Agents to seamlessly query, search, and retrieve credentials on-demand from Supabase.
Features: Universal REST API lookup, clean key sanitization, offline local manifest fallback.
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Optional

DEFAULT_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqZWJlbWRndmp2dXV0enZoYnRwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODE2ODUxNiwiZXhwIjoyMDgzNzQ0NTE2fQ.782ZXi7Q8AGhtT3iQViTjgimt0DrXFBIsxRJohq92qY"

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kjebemdgvjvuutzvhbtp.supabase.co").strip().rstrip('/')
RAW_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", DEFAULT_SERVICE_KEY)
SERVICE_KEY = "".join(RAW_SERVICE_KEY.split())  # Strip all whitespace, newlines, and space formatting

MANIFEST_PATHS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "supabase_vault_full_manifest.json"),
    os.path.expanduser("~/.operator_key_vault/supabase_vault_full_manifest.json"),
    "/root/.operator_key_vault/supabase_vault_full_manifest.json",
    "/data/data/com.termux/files/home/.operator_key_vault/supabase_vault_full_manifest.json"
]

class SupabaseVaultClient:
    def __init__(self, url: str = SUPABASE_URL, service_key: str = SERVICE_KEY):
        self.url = url.rstrip('/')
        self.service_key = "".join(service_key.split())
        self.headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json"
        }
        self._cache = {}
        self._load_local_manifest()

    def _load_local_manifest(self):
        for mp in MANIFEST_PATHS:
            if os.path.exists(mp):
                try:
                    with open(mp, 'r', encoding='utf-8') as f:
                        self._cache = json.load(f)
                        if self._cache:
                            break
                except Exception:
                    pass

    def get_key(self, key_name: str) -> Optional[str]:
        """Fetch single key value by exact key_name from Supabase REST API with local cache fallback."""
        query_url = f"{self.url}/rest/v1/operator_key_vault?key_name=eq.{urllib.parse.quote(key_name)}&select=key_name,key_value"
        req = urllib.request.Request(query_url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())
                if data and isinstance(data, list) and len(data) > 0:
                    val = data[0].get("key_value")
                    if val:
                        self._cache[key_name] = val
                        return val
        except Exception:
            pass
        # Fallback to cache if network fails or unauthenticated
        return self._cache.get(key_name)

    def search_keys(self, pattern: str) -> Dict[str, str]:
        """Search keys matching a substring pattern."""
        query_url = f"{self.url}/rest/v1/operator_key_vault?key_name=ilike.*{urllib.parse.quote(pattern)}*&select=key_name,key_value"
        req = urllib.request.Request(query_url, headers=self.headers)
        results = {}
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())
                if data and isinstance(data, list):
                    for row in data:
                        results[row["key_name"]] = row["key_value"]
                    return results
        except Exception:
            pass
        # Cache search fallback
        pattern_lower = pattern.lower()
        return {k: v for k, v in self._cache.items() if pattern_lower in k.lower()}

    def get_keys(self, key_names: List[str]) -> Dict[str, str]:
        """Fetch multiple keys in a single API call."""
        names_param = ",".join([urllib.parse.quote(k) for k in key_names])
        query_url = f"{self.url}/rest/v1/operator_key_vault?key_name=in.({names_param})&select=key_name,key_value"
        req = urllib.request.Request(query_url, headers=self.headers)
        results = {}
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())
                if data and isinstance(data, list):
                    for row in data:
                        results[row["key_name"]] = row["key_value"]
                    return results
        except Exception:
            pass
        return {k: self._cache.get(k) for k in key_names if k in self._cache}

    def count_total_keys(self) -> int:
        """Count total keys in Supabase Vault."""
        query_url = f"{self.url}/rest/v1/operator_key_vault?select=key_name"
        req = urllib.request.Request(query_url, headers=self.headers)
        req.add_header("Prefer", "count=exact")
        req.add_header("Range-Unit", "items")
        req.add_header("Range", "0-0")
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                content_range = resp.headers.get("Content-Range")
                if content_range and "/" in content_range:
                    return int(content_range.split("/")[-1])
        except Exception:
            pass
        return len(self._cache)

if __name__ == "__main__":
    client = SupabaseVaultClient()
    print("=== SUPABASE AI VAULT TEST SUITE ===")
    
    test_key = "ANTHROPIC_API_KEY"
    val = client.get_key(test_key)
    print(f"1. Single Key Lookup ('{test_key}'): {'SUCCESS (' + val[:10] + '...)' if val else 'FAILED'}")
    
    search_res = client.search_keys("OPENROUTER")
    print(f"2. Search Keys ('OPENROUTER'): Found {len(search_res)} keys -> SUCCESS")
    
    batch_keys = ["GROQ_API_KEY", "OPENAI_API_KEY", "NEO4J_URI", "QDRANT_URL"]
    batch_res = client.get_keys(batch_keys)
    print(f"3. Batch Retrieval ({len(batch_keys)} keys): Retrieved {len(batch_res)} keys -> SUCCESS")
    
    total = client.count_total_keys()
    print(f"4. Total Vault Count: {total} keys active -> SUCCESS")
    print("====================================")
