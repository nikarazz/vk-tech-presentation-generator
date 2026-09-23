"""Клиент для работы с LLM через OpenAI-совместимый API."""

import os
import json
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Ищем .env в корне проекта (на 2 уровня выше shared/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


def _get_proxies():
    proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    if proxy:
        return {"http": proxy, "https": proxy}
    return None


def chat(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    response_format: dict | None = None,
    use_cache: bool = True,
    verbose: bool = False,
) -> str:
    """Отправляет запрос к LLM и возвращает текст ответа."""

    base_url = os.getenv("LLM_API_URL")
    api_key = os.getenv("LLM_API_KEY")
    model = model or os.getenv("LLM_MODEL")

    if not base_url or not api_key:
        raise RuntimeError(
            f"LLM_API_URL и LLM_API_KEY должны быть в .env. "
            f"Искали в: {_env_path}. Существует: {_env_path.exists()}"
        )

    if use_cache:
        try:
            from shared.llm_cache import get as cache_get
            cached = cache_get(messages, model, temperature, max_tokens)
            if cached is not None:
                if verbose:
                    print(f"[cache] hit: {model}")
                return cached
        except ImportError:
            pass

    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format:
        body["response_format"] = response_format

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    t0 = time.time()
    response = requests.post(
        url,
        headers=headers,
        json=body,
        proxies=_get_proxies(),
        timeout=60,
    )
    elapsed = time.time() - t0

    if verbose:
        print(f"[llm] {model} — {elapsed:.2f} сек, status={response.status_code}")

    response.raise_for_status()
    data = response.json()
    text = data["choices"][0]["message"]["content"]

    if use_cache:
        try:
            from shared.llm_cache import set as cache_set
            cache_set(messages, model, temperature, max_tokens, text)
        except ImportError:
            pass

    return text


def chat_json(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 4000,
    use_cache: bool = True,
    verbose: bool = False,
    max_retries=5,
) -> str:
    """Отправляет запрос и просит JSON-ответ."""
    return chat(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
        use_cache=use_cache,
        verbose=verbose,
    )
