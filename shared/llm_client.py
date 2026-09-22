"""Клиент для работы с LLM через OpenAI-совместимый API."""

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Возвращает singleton-клиент OpenAI."""
    global _client
    if _client is None:
        base_url = os.getenv("LLM_BASE_URL")
        api_key = os.getenv("LLM_API_KEY")
        if not base_url or not api_key:
            raise RuntimeError(
                "LLM_BASE_URL и LLM_API_KEY должны быть заданы в .env"
            )
        _client = OpenAI(base_url=base_url, api_key=api_key)
    return _client


def chat(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    response_format: dict | None = None,
    use_cache: bool = True,
    verbose: bool = False,
) -> str:
    """
    Отправляет запрос к LLM и возвращает текст ответа.

    Args:
        messages: список сообщений [{"role": "user", "content": "..."}]
        model: имя модели (по умолчанию из .env)
        temperature: креативность (0.0 — детерминированно)
        max_tokens: максимум токенов в ответе
        response_format: {"type": "json_object"} для JSON-ответа
        use_cache: использовать файловый кэш
        verbose: печатать информацию о кэше и времени

    Returns:
        Текст ответа.
    """
    client = get_client()
    model = model or os.getenv("LLM_MODEL")

    if use_cache:
        from shared.llm_cache import get as cache_get
        cached = cache_get(messages, model, temperature, max_tokens)
        if cached is not None:
            if verbose:
                print(f"[cache] hit: {model}")
            return cached

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format:
        kwargs["response_format"] = response_format

    t0 = time.time()
    response = client.chat.completions.create(**kwargs)
    elapsed = time.time() - t0

    text = response.choices[0].message.content

    if verbose:
        print(f"[llm] {model} — {elapsed:.2f} сек")

    if use_cache:
        from shared.llm_cache import set as cache_set
        cache_set(messages, model, temperature, max_tokens, text)

    return text


def chat_json(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 4000,
    use_cache: bool = True,
    verbose: bool = False,
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
