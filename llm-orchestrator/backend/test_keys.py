"""
Key validation script — tests each configured API key with a minimal request.
Run: python test_keys.py
Safe: sends only "Say hello in 5 words" to each provider.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import settings, PROVIDERS
from adapters import ADAPTER_MAP

TEST_MESSAGES = [{"role": "user", "content": "Say hello in exactly 5 words."}]

COLORS = {
    "ok": "\033[92m",     # green
    "fail": "\033[91m",   # red
    "skip": "\033[93m",   # yellow
    "reset": "\033[0m",
    "bold": "\033[1m",
}


async def test_provider(name: str) -> tuple[str, str, str]:
    """Returns (provider, status, detail)."""
    key = settings.api_key_for(name)
    if not key:
        return name, "SKIP", "no key configured"

    cls = ADAPTER_MAP.get(name)
    if not cls:
        return name, "SKIP", "no adapter"

    client = cls(api_key=key)
    model = PROVIDERS.get(name, {}).get("default_model", "")

    try:
        resp = await client.chat(TEST_MESSAGES, model, max_tokens=30)
        preview = resp.content[:60].replace("\n", " ")
        return name, "OK", f"model={resp.model}  tokens={resp.tokens_used}  \"{preview}\""
    except Exception as e:
        err = str(e)
        # Extract useful bit from HTTP errors
        if "status_code" in err.lower() or "HTTP" in err:
            return name, "FAIL", err[:120]
        return name, "FAIL", err[:120]


async def main():
    print(f"\n{COLORS['bold']}=== LLM Orchestrator — Key Validation ==={COLORS['reset']}\n")

    providers = list(PROVIDERS.keys())
    tasks = [test_provider(p) for p in providers]
    results = await asyncio.gather(*tasks)

    ok_count = 0
    for name, status, detail in results:
        if status == "OK":
            icon = f"{COLORS['ok']}PASS{COLORS['reset']}"
            ok_count += 1
        elif status == "SKIP":
            icon = f"{COLORS['skip']}SKIP{COLORS['reset']}"
        else:
            icon = f"{COLORS['fail']}FAIL{COLORS['reset']}"

        print(f"  [{icon}] {name:14s}  {detail}")

    total = len(providers)
    skipped = sum(1 for _, s, _ in results if s == "SKIP")
    failed = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"\n  {ok_count}/{total} passed, {skipped} skipped, {failed} failed\n")


if __name__ == "__main__":
    asyncio.run(main())
