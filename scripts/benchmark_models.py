"""Замер скорости разных моделей."""

import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.llm_client import chat


MODELS = [
    "qwen3.8-max",
    "qwen3.8-flash",
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-5.6-luna",
    "gpt-6-astra",
    "ma-qwen3.8-max",
    "ma-qwen3.8-flash",
    "ma-gpt-5.6-sol",
]

PROMPT = [{"role": "user", "content": "Скажи 'привет' одним словом."}]

print(f"{'Модель':<25} {'Время':>10}  {'Ответ':<20}")
print("-" * 60)

for model in MODELS:
    try:
        t0 = time.time()
        r = chat(PROMPT, model=model, temperature=0.0, max_tokens=20, use_cache=False)
        elapsed = time.time() - t0
        print(f"{model:<25} {elapsed:>8.2f}с  {r[:20]:<20}")
    except Exception as e:
        err = str(e)[:40]
        print(f"{model:<25} {'—':>10}  {err}")
