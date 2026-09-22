"""Проверка подключения к LLM: базовый запрос и JSON-режим."""

import sys
import os
import json
import time

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)

from shared.llm_client import chat, chat_json


def test_basic():
    print("Тест 1: базовый запрос")
    t0 = time.time()
    try:
        r = chat(
            [{"role": "user", "content": "Скажи 'привет' одним словом."}],
            temperature=0.0,
            max_tokens=50,
        )
        elapsed = time.time() - t0
        print(f"  Ответ: {r}")
        print(f"  Время: {elapsed:.2f} сек")
        return True
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  Ошибка: {e}")
        print(f"  Время: {elapsed:.2f} сек")
        return False


def test_json():
    print("\nТест 2: JSON-ответ")
    t0 = time.time()
    try:
        r = chat_json(
            [{"role": "user", "content": 'Верни JSON: {"ok": true}'}],
            max_tokens=100,
        )
        elapsed = time.time() - t0
        parsed = json.loads(r)
        print(f"  Ответ: {r}")
        print(f"  Распарсено: {parsed}")
        print(f"  Время: {elapsed:.2f} сек")
        return True
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  Ошибка: {e}")
        print(f"  Время: {elapsed:.2f} сек")
        return False


def test_config():
    print("\nКонфигурация:")
    print(f"  LLM_MODEL: {os.getenv('LLM_MODEL')}")
    print(f"  LLM_BASE_URL: {os.getenv('LLM_BASE_URL')}")
    api_key = os.getenv("LLM_API_KEY", "")
    if api_key:
        masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"  LLM_API_KEY: {masked}")
    else:
        print("  LLM_API_KEY: не задан")


def main():
    print("Проверка подключения к LLM\n")
    ok1 = test_basic()
    ok2 = test_json()
    test_config()
    print("\nИтог:")
    print(f"  Тест 1: {'✓' if ok1 else '✗'}")
    print(f"  Тест 2: {'✓' if ok2 else '✗'}")
    if ok1 and ok2:
        print("\nLLM готова к работе.")
        sys.exit(0)
    else:
        print("\nЕсть проблемы. Проверь .env и подключение.")
        sys.exit(1)


if __name__ == "__main__":
    main()
