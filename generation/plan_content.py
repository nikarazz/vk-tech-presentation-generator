import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""Content Planner: бриф + контент-пакет + дизайн-система → SlidePlan."""

import json
from pathlib import Path

from shared.llm_client import chat_json


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


def build_user_prompt(brief: str, content_pack: dict, design_system: dict) -> str:
    patterns = []
    for pid, p in design_system.get("patterns", {}).items():
        info = f"- {pid}: {p.get('name', pid)}"
        constraints = p.get("body_constraints")
        if constraints:
            info += f" (max_bullets={constraints.get('max_bullets')})"
        patterns.append(info)
    return f"""Бриф: {brief}

Контент-пакет:
{json.dumps(content_pack, ensure_ascii=False, indent=2)}

Доступные паттерны:
{chr(10).join(patterns)}

Составь структуру презентации из 8-12 слайдов. Верни JSON."""


def plan_content(brief: str, content_pack: dict, design_system: dict) -> dict:
    system_prompt = load_prompt("content_planner_v1.md")
    user_prompt = build_user_prompt(brief, content_pack, design_system)
    response = chat_json(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1500,
    )
    plan = json.loads(response)
    if "slides" not in plan:
        raise ValueError(f"LLM вернула неверный формат: {plan}")
    return plan


if __name__ == "__main__":
    from shared.mocks.design_system_mock import MOCK_DESIGN_SYSTEM

    mock_content_pack = {
        "product": "Тёмная тема в мобильном приложении",
        "benefits": ["Снижает нагрузку на глаза", "Экономит батарею"],
        "metrics": {"adoption_first_month": "40%"},
    }

    brief = "Фича: тёмная тема. Метрика: 40%."

    print("Запуск Content Planner...")
    plan = plan_content(brief, mock_content_pack, MOCK_DESIGN_SYSTEM)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
