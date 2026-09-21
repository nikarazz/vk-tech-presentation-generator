import json
import os


def plan_content(brief: str, content_pack: dict, ds: dict) -> dict:
    patterns = list(ds.get("patterns", {}).keys())
    title_pattern = "title" if "title" in patterns else patterns[0]
    content_pattern = "content_bullets" if "content_bullets" in patterns else patterns[0]
    closing_pattern = "title_only" if "title_only" in patterns else patterns[-1]
    
    return {
        "slides": [
            {"pattern_id": title_pattern, "title": "Тёмная тема", "subtitle": "Фича Q1 2026"},
            {"pattern_id": content_pattern, "title": "Проблема", "bullets": [
                "Нагрузка на глаза при ярком экране",
                "Яркий экран мешает ночью",
                "Жалобы пользователей растут",
                "Пик использования — вечер",
                "Мобильные устройства чаще",
                "Долгое чтение утомляет",
            ]},
            {"pattern_id": content_pattern, "title": "Решение", "bullets": [
                "Тёмная тема в приложении",
                "40% пользователей включили за месяц",
                "Автопереключение по времени",
                "Настройка в профиле",
                "Экономия батареи на 15%",
            ]},
            {
                "pattern_id": content_pattern,
                "title": "Динамика включения",
                "chart": {
                    "type": "bar",
                    "title": "Включение тёмной темы по месяцам",
                    "categories": ["Янв", "Фев", "Мар", "Апр"],
                    "series": [
                        {"name": "Доля пользователей, %", "values": [10, 18, 28, 40]},
                    ],
                    "x_label": "Месяц",
                    "y_label": "%",
                },
            },
            {
                "pattern_id": content_pattern,
                "title": "Метрики",
                "table": {
                    "headers": ["Метрика", "Q1", "Q2", "Q3", "Q4"],
                    "rows": [
                        ["DAU", "10M", "12M", "15M", "18M"],
                        ["Retention", "40%", "42%", "45%", "48%"],
                        ["NPS", "30", "35", "42", "50"],
                    ],
                },
            },
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