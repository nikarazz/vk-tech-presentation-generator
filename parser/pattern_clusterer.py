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
    """Возвращает базовое семантическое имя для layout."""
    layout_type = layout.get("type", "obj")
    name = layout.get("name", "").lower().replace(" ", "_")

    if "blank" in name:
        return "blank"
    if "section" in name or layout_type == "secHead":
        return "section"
    if "two_content" in name or "two content" in name:
        return "content_two_column"
    if "comparison" in name:
        return "comparison"
    if "content_with_caption" in name or "content with caption" in name:
        return "content_with_caption"
    if "picture_with_caption" in name or "picture with caption" in name:
        return "picture_with_caption"
    if "title_only" in name or "title only" in name:
        return "title_only"
    if "vertical_title" in name or "vertical title" in name:
        return "vertical_title"
    if "title_slide" in name or "title slide" in name:
        return "title"
    if "title_and_content" in name or "title and content" in name:
        return "content_bullets"
    if "chart" in name:
        return "data_chart"
    if "table" in name:
        return "data_table"
    if "image" in name or "picture" in name:
        return "image_full"
    if "closing" in name or "thank" in name:
        return "closing"

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
