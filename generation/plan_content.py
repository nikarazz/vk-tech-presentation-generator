"""Content Planner: бриф + контент-пакет + дизайн-система → SlidePlan.

Два режима:
  1. plan_content_llm — реальный LLM-вызов (если API работает).
  2. plan_content_stub — заглушка (если LLM недоступна).

plan_content — обёртка с fallback.
"""

import json
import os
from pathlib import Path

from shared.llm_client import chat_json

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ---------------------------------------------------------------------------
# Промпты
# ---------------------------------------------------------------------------

def load_prompt(filename: str) -> str:
    """Загружает промпт из файла."""
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


def build_user_prompt(brief: str, content_pack: dict, ds: dict) -> str:
    """Собирает user-промпт с реальными паттернами из шаблона."""
    patterns = []
    for pid, p in ds.get("patterns", {}).items():
        name = p.get("name", pid)
        info = f"- {pid} ({name})"
        constraints = p.get("body_constraints")
        if constraints:
            max_bullets = constraints.get("max_bullets", 6)
            max_words = constraints.get("max_words_per_bullet", 15)
            info += f" [max_bullets={max_bullets}, max_words={max_words}]"
        patterns.append(info)

    return f"""Бриф:
{brief}

Контент:
{json.dumps(content_pack, ensure_ascii=False)}

Доступные паттерны из шаблона:
{chr(10).join(patterns)}

Составь 8-12 слайдов, используя ТОЛЬКО эти паттерны.

Правила:
1. Первый слайд — pattern_id "title".
2. Для буллетов — pattern_id "content_bullets" или "content_bullets_N".
3. Для графиков — "data_chart".
4. Для финала — "title_only" или "team".
5. Буллеты — массив строк, каждое ≤ 15 слов.

Верни JSON:
{{"slides": [{{"pattern_id": "...", "title": "...", "bullets": ["..."]}}]}}"""


# ---------------------------------------------------------------------------
# Stub — работает без LLM
# ---------------------------------------------------------------------------

def _find_pattern(patterns: list, *keywords, fallback: str = None) -> str:
    """Ищет паттерн по нескольким ключевым словам."""
    for keyword in keywords:
        for pid in patterns:
            if keyword in pid.lower():
                return pid
    if fallback and fallback in patterns:
        return fallback
    return patterns[0] if patterns else fallback


def plan_content_stub(brief: str, content_pack: dict, ds: dict) -> dict:
    """Заглушка: 10 слайдов с реальными паттернами шаблона."""
    patterns = ds.get("patterns", {})
    if not patterns:
        patterns = {"title": {}, "content_bullets": {}}

    pattern_ids = list(patterns.keys())

    # Ищем title-паттерн
    title_p = "title" if "title" in patterns else pattern_ids[0]

    # Ищем body-паттерн
    body_patterns = [
        pid for pid, p in patterns.items()
        if any(ph.get("role") == "bullet" for ph in p.get("placeholders", []))
    ]
    content_p = body_patterns[0] if body_patterns else title_p

    # Контентные слайды с буллетами
    content_slides = [
        ("Проблема", ["Ручная вёрстка занимает часы", "Дизайнеры перегружены", "Шаблоны не адаптируются"]),
        ("Решение", ["Парсинг произвольного шаблона", "LLM генерирует структуру", "Автовёрстка по плейсхолдерам"]),
        ("Как это работает", ["Загрузка шаблона .pptx", "Бриф → план слайдов", "Раскладка по правилам шаблона"]),
        ("Преимущества", ["5 минут вместо часов", "3 варианта вёрстки", "Экспорт в .pptx / .pdf / .html"]),
        ("Технологии", ["Parser: python-pptx + lxml", "LLM: Qwen / GPT", "Layout Engine: детерминированный"]),
        ("Метрики", ["Время генерации ≤ 5 мин", "Соответствие стилю 100%", "Устойчивость к шаблонам"]),
        ("Развитие", ["Генерация изображений", "SmartArt", "Веб-интерфейс"]),
        ("Команда", ["Parser Engineer", "Generation Engineer", "Audit Engineer"]),
        ("Итоги", ["Работающий прототип", "Устойчивость к шаблонам", "Готовность к пилоту"]),
    ]

    slides = [{"pattern_id": title_p, "title": "Тёмная тема", "subtitle": "Фича Q1 2026"}]

    for title, bullets in content_slides:
        slides.append({
            "pattern_id": content_p,
            "title": title,
            "bullets": bullets,
        })

    slides.append({"pattern_id": title_p, "title": "Спасибо"})

    return {"slides": slides}



def plan_content_llm(
    brief: str,
    content_pack: dict,
    ds: dict,
    verbose: bool = False,
) -> dict:
    """LLM-вызов с fallback на вторую модель."""
    system_prompt = load_prompt("content_planner_v1.md")
    user_prompt = build_user_prompt(brief, content_pack, ds)

    models = [
        os.getenv("LLM_MODEL"),
        os.getenv("LLM_MODEL_FALLBACK"),
    ]
    models = [m for m in models if m]

    last_error = None
    for model in models:
        try:
            response = chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=model,
                temperature=0.3,
                max_tokens=1000,
                verbose=verbose,
            )
            plan = json.loads(response) if isinstance(response, str) else response
            if "slides" in plan:
                return plan
        except Exception as e:
            last_error = e
            if verbose:
                print(f"[plan_content] {model} failed: {e}")

    raise last_error or RuntimeError("All models failed")


# ---------------------------------------------------------------------------
# Главная функция с fallback
# ---------------------------------------------------------------------------

def plan_content(brief, content_pack, ds, use_llm=True):
    """С fallback и retry."""
    if use_llm:
        import time
        for attempt in range(3):
            try:
                return plan_content_llm(brief, content_pack, ds, verbose=True)
            except Exception as e:
                print(f"[plan_content] Attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    time.sleep(2)
        print("[plan_content] All attempts failed. Fallback to stub.")
    return plan_content_stub(brief, content_pack, ds)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from shared.mocks.design_system_mock import MOCK_DESIGN_SYSTEM

    brief = "Фича: тёмная тема. Метрика: 40%."
    plan = plan_content(brief, {}, MOCK_DESIGN_SYSTEM)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
