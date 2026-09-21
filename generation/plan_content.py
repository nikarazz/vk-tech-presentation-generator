import json
import os


def plan_content(brief: str, content_pack: dict, ds: dict) -> dict:
    """
    Заглушка Content Planner.
    Возвращает мок-план из 4 слайдов.
    """
    patterns = list(ds.get("patterns", {}).keys())
    
    title_pattern = "title" if "title" in patterns else patterns[0] if patterns else "title"
    content_pattern = "content_bullets" if "content_bullets" in patterns else patterns[0] if patterns else "content_bullets"
    closing_pattern = "title_only" if "title_only" in patterns else patterns[-1] if patterns else "title_only"
    
    return {
        "slides": [
            {"pattern_id": title_pattern, "title": "Тёмная тема", "subtitle": "Фича Q1 2026"},
            {"pattern_id": content_pattern, "title": "Проблема", "bullets": [
                "Нагрузка на глаза",
                "Яркий экран ночью",
                "Жалобы пользователей",
            ]},
            {"pattern_id": content_pattern, "title": "Решение", "bullets": [
                "Тёмная тема",
                "Автопереключение",
                "Настройка в профиле",
            ]},
            {"pattern_id": closing_pattern, "title": "Спасибо"},
        ]
    }


def plan_content_llm(brief: str, content_pack: dict, ds: dict) -> dict:
    """Реальный LLM-вызов. Подключить, когда API готов."""
    from openai import OpenAI
    
    client = OpenAI(
        base_url=os.getenv("LLM_API_URL"),
        api_key=os.getenv("LLM_API_KEY"),
    )
    patterns = list(ds.get("patterns", {}).keys())
    prompt = open("prompts/content_planner_v1.md").read().format(
        brief=brief, patterns=patterns,
    )
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "qwen3-27b"),
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)