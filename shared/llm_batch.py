"""Параллельные запросы к LLM."""

import concurrent.futures
from shared.llm_client import chat_json


def batch_chat_json(messages_list, max_workers=3, **kwargs):
    """Отправляет несколько запросов параллельно."""
    results = [None] * len(messages_list)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(chat_json, msgs, **kwargs): i
            for i, msgs in enumerate(messages_list)
        }
        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            try:
                results[i] = future.result()
            except Exception as e:
                results[i] = {"error": str(e)}
    return results
