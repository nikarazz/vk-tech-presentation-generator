"""
Кластеризация паттернов слайдов.

Объединяет информацию из:
  - layouts (доступные макеты)
  - slides (какие макеты использованы, сколько раз)

На выходе — patterns с usage_count и метаданными.
"""
from collections import Counter


def cluster_patterns(layouts: list[dict], slides: list[dict]) -> dict:
    """
    Строит patterns из layouts и статистики использования.

    Возвращает:
      {
        "title": {
          "id": "title",
          "name": "Title Slide",
          "layout_ref": "slideLayout1.xml",
          "placeholders": [...],
          "usage_count": 1,
          "is_used": True,
        },
        ...
      }
    """
    # Считаем использование layouts (пока по эвристике)
    layout_usage = _estimate_layout_usage(layouts, slides)

    patterns = {}
    for layout in layouts:
        pattern_id = _layout_to_pattern_id(layout)
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


def _estimate_layout_usage(layouts: list[dict], slides: list[dict]) -> dict:
    """
    Оценивает, сколько раз каждый layout использован.

    Пока — эвристика по структуре плейсхолдеров.
    В идеале — по rels-файлам, но это отдельная задача.
    """
    usage = {}

    # Каждый layout получает базовый usage_count = 1, если он "основной"
    for layout in layouts:
        layout_type = layout.get("type", "obj")
        if layout_type in ("title", "obj", "secHead"):
            usage[layout["layout_ref"]] = 1
        else:
            usage[layout["layout_ref"]] = 0

    # Если слайдов больше, чем layouts — распределяем
    # (грубая эвристика, заменим позже)
    if slides:
        obj_layouts = [l for l in layouts if l.get("type") == "obj"]
        if obj_layouts:
            per_layout = max(1, len(slides) // len(obj_layouts))
            for layout in obj_layouts:
                usage[layout["layout_ref"]] = per_layout

    return usage


def _layout_to_pattern_id(layout: dict) -> str:
    """Генерирует pattern_id."""
    layout_type = layout.get("type", "obj")
    name = layout.get("name", "").lower().replace(" ", "_")

    if layout_type == "title" or "title" in name:
        return "title"
    if layout_type == "secHead" or "section" in name:
        return "section"
    if layout_type == "blank":
        return "blank"
    if "content" in name:
        return "content_bullets"
    if "two" in name and "column" in name:
        return "content_two_column"
    if "chart" in name:
        return "data_chart"
    if "table" in name:
        return "data_table"
    if "image" in name or "picture" in name:
        return "image_full"
    if "closing" in name or "thank" in name:
        return "closing"

    # Уникальный ID для остальных
    ref = layout["layout_ref"].replace(".xml", "")
    return f"layout_{ref}"


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
