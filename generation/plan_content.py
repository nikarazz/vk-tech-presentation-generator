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
    """Заглушка: использует реальные паттерны из шаблона."""
    patterns = list(ds.get("patterns", {}).keys())

    if not patterns:
        patterns = ["title", "content_bullets", "title_only"]

    title_pattern = _find_pattern(patterns, "title", fallback="title")
    content_pattern = _find_pattern(
        patterns, "content_bullets", "content", "пункт",
        fallback="content_bullets",
    )
    closing_pattern = _find_pattern(
        patterns, "title_only", "team", "closing",
        fallback=title_pattern,
    )

    return {
        "slides": [
            {
                "pattern_id": title_pattern,
                "title": "Тёмная тема",
                "subtitle": "Фича Q1 2026",
            },
            {
                "pattern_id": content_pattern,
                "title": "Проблема",
                "bullets": [
                    "Нагрузка на глаза при ярком экране",
                    "Яркий экран мешает ночью",
                    "Жалобы пользователей растут",
                ],
            },
            {
                "pattern_id": content_pattern,
                "title": "Решение",
                "bullets": [
                    "Тёмная тема в приложении",
                    "40% пользователей включили за месяц",
                    "Автопереключение по времени",
                ],
            },
            {
                "pattern_id": closing_pattern,
                "title": "Спасибо",
            },
        ]
    }


# ---------------------------------------------------------------------------
# LLM — реальный вызов с fallback-моделью
# ---------------------------------------------------------------------------

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

def plan_content(
    brief: str,
    content_pack: dict,
    ds: dict,
    use_llm: bool = True,
) -> dict:
    """Content Planner с fallback на заглушку."""
    if use_llm:
        try:
            return plan_content_llm(brief, content_pack, ds, verbose=True)
        except Exception as e:
            print(f"[plan_content] LLM failed: {e}. Fallback to stub.")
    return plan_content_stub(brief, content_pack, ds)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from shared.mocks.design_system_mock import MOCK_DESIGN_SYSTEM

    brief = "Фича: тёмная тема. Метрика: 40%."
    plan = plan_content(brief, {}, MOCK_DESIGN_SYSTEM)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
