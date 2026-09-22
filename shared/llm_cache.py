"""Простой файловый кэш для ответов LLM."""

import hashlib
import json
from pathlib import Path

CACHE_DIR = Path(".cache/llm")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _key(messages, model, temperature, max_tokens):
    payload = json.dumps(
        {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get(messages, model, temperature, max_tokens):
    path = CACHE_DIR / f"{_key(messages, model, temperature, max_tokens)}.json"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def set(messages, model, temperature, max_tokens, response):
    path = CACHE_DIR / f"{_key(messages, model, temperature, max_tokens)}.json"
    path.write_text(response, encoding="utf-8")
