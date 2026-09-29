"""
Кластеризация паттернов слайдов.

Каждый layout → уникальный pattern_id.
usage_count считается реально — по layout_ref слайдов.
"""
from collections import Counter


def cluster_patterns(layouts: list[dict], slides: list[dict]) -> dict:
    """
    Строит patterns из layouts и статистики использования.

    Каждый layout получает уникальный pattern_id.
    Если семантическое имя уже занято — добавляется суффикс из layout_ref.
    """
    # Считаем использование layout'ов
    layout_usage = Counter()
    for slide in slides:
        layout_ref = slide.get("layout_ref", "unknown")
        if layout_ref != "unknown":
            layout_usage[layout_ref] += 1

    patterns = {}
    used_ids = set()

    for layout in layouts:
        base_id = _layout_to_base_id(layout)
        pattern_id = _make_unique_id(base_id, layout, used_ids)
        used_ids.add(pattern_id)

        usage = layout_usage.get(layout["layout_ref"], 0)

        patterns[pattern_id] = {
            "id": pattern_id,
            "name": layout["name"],
            "layout_ref": layout["layout_ref"],
            "type": layout["type"],
            "placeholders": layout["placeholders"],
            "usage_count": usage,
            "is_used": usage > 0,
        }

    return patterns


def _layout_to_base_id(layout: dict) -> str:
    """Возвращает семантическое имя паттерна по имени layout'а."""
    layout_type = layout.get("type", "obj")
    name = layout.get("name", "").lower()

    # Русские ключевые слова
    if "титул" in name:
        return "title"
    if "команда" in name:
        return "team"
    if "содержание" in name:
        return "content_bullets"
    if "описание" in name or "объект" in name:
        return "content_bullets"
    if "пункт" in name:
        return "content_bullets"
    if "статистик" in name or "график" in name or "диаграмм" in name:
        return "data_chart"
    if "таблиц" in name:
        return "data_table"
    if "стади" in name or "этап" in name:
        return "stages"
    if "проблем" in name and "решен" in name:
        return "problem_solution"
    if "демо" in name:
        return "demo"
    if "фото" in name or "рисунок" in name or "изображен" in name:
        return "image_full"
    if "сравнен" in name:
        return "comparison"
    if "пустой" in name:
        return "blank"

    # Английские ключевые слова
    if "title" in name:
        return "title"
    if "team" in name:
        return "team"
    if "content" in name:
        return "content_bullets"
    if "chart" in name or "stat" in name:
        return "data_chart"
    if "table" in name:
        return "data_table"
    if "demo" in name:
        return "demo"
    if "image" in name or "picture" in name:
        return "image_full"
    if "blank" in name:
        return "blank"

    # Fallback по типу
    if layout_type == "title":
        return "title"
    if layout_type == "secHead":
        return "section"
    if layout_type == "blank":
        return "blank"

    # Fallback по структуре плейсхолдеров
    roles = [ph.get("role") for ph in layout.get("placeholders", [])]
    if "slide_title" in roles and "bullet" in roles:
        return "content_bullets"
    if "slide_title" in roles:
        return "title_only"

    return "layout"


def _make_unique_id(base_id: str, layout: dict, used_ids: set) -> str:
    """
    Делает pattern_id уникальным.

    Если base_id не занят — возвращает его.
    Если занят — добавляет суффикс из layout_ref.
    """
    if base_id not in used_ids:
        return base_id

    ref = layout["layout_ref"].replace("slideLayout", "").replace(".xml", "")
    candidate = f"{base_id}_{ref}"

    # Если и это занято — добавляем ещё
    counter = 2
    while candidate in used_ids:
        candidate = f"{base_id}_{ref}_{counter}"
        counter += 1

    return candidate


def get_used_patterns(patterns: dict) -> dict:
    """Возвращает только использованные паттерны."""
    return {k: v for k, v in patterns.items() if v.get("is_used")}


def get_patterns_by_role(patterns: dict, role: str) -> list[dict]:
    """Возвращает паттерны, у которых есть плейсхолдер с данной ролью."""
    result = []
    for pattern in patterns.values():
        roles = [ph.get("role") for ph in pattern.get("placeholders", [])]
        if role in roles:
            result.append(pattern)
    return result


def compute_pattern_constraints(patterns: dict, slides: list[dict]) -> dict:
    """Вычисляет ограничения для каждого паттерна по реальным слайдам."""
    slides_by_layout = {}
    for slide in slides:
        layout_ref = slide.get("layout_ref", "unknown")
        slides_by_layout.setdefault(layout_ref, []).append(slide)

    for pattern in patterns.values():
        layout_ref = pattern["layout_ref"]
        pattern_slides = slides_by_layout.get(layout_ref, [])

        max_bullets = 0
        max_words = 0
        for slide in pattern_slides:
            bullet_count = 0
            for el in slide.get("elements", []):
                if el.get("role") == "bullet":
                    lines = [l for l in el.get("text", "").split('\n') if l.strip()]
                    bullet_count += len(lines)
                    for line in lines:
                        max_words = max(max_words, len(line.split()))
            max_bullets = max(max_bullets, bullet_count)

        if max_bullets > 0:
            pattern["body_constraints"] = {
                "max_bullets": max_bullets,
                "max_words_per_bullet": max_words,
            }

    return patterns
