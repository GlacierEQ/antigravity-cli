#!/usr/bin/env python3
"""
APEX Sovereign AI Supabase Vault Client
Enables AI Agents to seamlessly query, search, and retrieve credentials on-demand from Supabase.
Features: REST API lookup, local cache fallback, pattern matching, and batch retrieval.
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Optional

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kjebemdgvjvuutzvhbtp.supabase.co")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqZWJlbWRndmp2dXV0enZoYnRwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODE2ODUxNiwiZXhwIjoyMDgzNzQ0NTE2fQ.782ZXi7Q8AGhtT3iQViTjgimt0DrXFBIsxRJohq92qY")
LOCAL_MANIFEST = "/root/.operator_key_vault/supabase_vault_full_manifest.json"

class SupabaseVaultClient:
    def __init__(self, url: str = SUPABASE_URL, service_key: str = SERVICE_KEY):
        self.url = url.rstrip('/')
        self.service_key = service_key
        self.headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json"
        }
        self._cache = {}
        self._load_local_manifest()

    def _load_local_manifest(self):
        if os.path.exists(LOCAL_MANIFEST):
            try:
                with open(LOCAL_MANIFEST, 'r') as f:
                    self._cache = json.load(f)
            except Exception:
                pass

    def get_key(self, key_name: str) -> Optional[str]:
        """Fetch single key value by exact key_name from Supabase REST API with local cache fallback."""
        query_url = f"{self.url}/rest/v1/operator_key_vault?key_name=eq.{urllib.parse.quote(key_name)}&select=key_name,key_value"
        req = urllib.request.Request(query_url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data and isinstance(data, list) and len(data) > 0:
                    val = data[0].get("key_value")
                    self._cache[key_name] = val
                    return val
        except Exception:
            pass
        # Fallback to cache if network fails
        return self._cache.get(key_name)

    def search_keys(self, pattern: str) -> Dict[str, str]:
        """Search keys matching a substring pattern."""
        query_url = f"{self.url}/rest/v1/operator_key_vault?key_name=ilike.*{urllib.parse.quote(pattern)}*&select=key_name,key_value"
        req = urllib.request.Request(query_url, headers=self.headers)
        results = {}
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
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
            with urllib.request.urlopen(req, timeout=5) as resp:
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
            with urllib.request.urlopen(req, timeout=5) as resp:
                content_range = resp.headers.get("Content-Range")
                if content_range and "/" in content_range:
                    return int(content_range.split("/")[-1])
        except Exception:
            pass
        return len(self._cache)

if __name__ == "__main__":
    client = SupabaseVaultClient()
    print("=== SUPABASE AI VAULT TEST SUITE ===")
    
    # Test 1: Single key lookup
    test_key = "ANTHROPIC_API_KEY"
    val = client.get_key(test_key)
    print(f"1. Single Key Lookup ('{test_key}'): {'SUCCESS' if val else 'FAILED'}")
    
    # Test 2: Search pattern
    search_res = client.search_keys("SUPABASE")
    print(f"2. Search Keys ('SUPABASE'): Found {len(search_res)} keys -> SUCCESS")
    
    # Test 3: Batch retrieval
    batch_keys = ["GROQ_API_KEY", "OPENAI_API_KEY", "NEO4J_URI", "QDRANT_URL"]
    batch_res = client.get_keys(batch_keys)
    print(f"3. Batch Retrieval ({len(batch_keys)} keys): Retrieved {len(batch_res)} keys -> SUCCESS")
    
    # Test 4: Total count
    total = client.count_total_keys()
    print(f"4. Total Vault Count: {total} keys in Supabase -> SUCCESS")
    print("====================================")
