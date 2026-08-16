#!/usr/bin/env python3
"""
Antigravity CLI - Add Custom Model Tool
Allows instant CLI registration of custom AI models, local endpoints, or fine-tuned model variants.
Usage: python3 add_model.py --id "claude-3-7-opus" --name "Claude 3.7 Opus" --provider "anthropic" --aliases "opus-3.7,opus"
"""

import sys
import argparse
from model_registry import ModelRegistry

def main():
    parser = argparse.ArgumentParser(description="Register a custom AI model in Antigravity Model Registry.")
    parser.add_argument("--id", required=True, help="Unique model identifier (e.g. claude-3-7-opus)")
    parser.add_argument("--name", required=True, help="Human-readable model name")
    parser.add_argument("--provider", required=True, choices=["google", "anthropic", "openai", "groq", "deepseek", "local_ollama", "custom"], help="Provider name")
    parser.add_argument("--tier", default="pro", choices=["flash_lite", "flash", "pro"], help="Performance tier")
    parser.add_argument("--context-window", type=int, default=128000, help="Context window size in tokens")
    parser.add_argument("--aliases", default="", help="Comma-separated alias shortcuts")

    args = parser.parse_args()

    alias_list = [a.strip() for a in args.aliases.split(",") if a.strip()]

    model_info = {
        "id": args.id.lower().strip(),
        "name": args.name.strip(),
        "provider": args.provider.lower().strip(),
        "tier": args.tier,
        "context_window": args.context_window,
        "aliases": alias_list
    }

    reg = ModelRegistry()
    reg.register_model(model_info)
    reg.save_custom_config()

    print(f"🟢 Successfully registered model '{args.name}' ({args.id}) under provider '{args.provider}'!")
    if alias_list:
        print(f"  └─ Registered aliases: {', '.join(alias_list)}")

if __name__ == "__main__":
    main()
