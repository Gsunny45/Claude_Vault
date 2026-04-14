"""
Quick utility: list all Gemini models available on your API key.
Run: python list_gemini_models.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import httpx
from config import settings

key = settings.gemini_api_key or settings.user_gemini_key
if not key:
    print("No GEMINI_API_KEY set"); sys.exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
resp = httpx.get(url, timeout=15)
resp.raise_for_status()

models = resp.json().get("models", [])
print(f"Found {len(models)} models:\n")
for m in models:
    name = m["name"].replace("models/", "")
    methods = ", ".join(m.get("supportedGenerationMethods", []))
    print(f"  {name:45s}  [{methods}]")
