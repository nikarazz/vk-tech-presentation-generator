"""
Главная функция парсера.

Собирает всё:
  - theme (цвета, шрифты)
  - master (фон, логотип, стили)
  - layouts (паттерны слайдов)
  - правила (из статистики)

Возвращает DesignSystem.
"""
from parser.theme_parser import parse_theme
from parser.master_parser import parse_master
from parser.layout_parser import parse_layouts
from shared.mocks.design_system_mock import MOCK_DESIGN_SYSTEM


def parse_template(pptx_path: str) -> dict:
    """
    Парсит .pptx и возвращает DesignSystem.

    На текущем этапе:
      - theme: реальный (из theme1.xml)
      - master: реальный (из slideMaster1.xml)
      - patterns: реальные (из slideLayouts/)
      - palette.colors: пока мок (заменим позже)
      - typography.scale: пока мок (заменим позже)
      - grid: пока мок
      - rules: пока мок
    """
    theme = parse_theme(pptx_path)
    master = parse_master(pptx_path, theme)
    layouts = parse_layouts(pptx_path)

    patterns = _layouts_to_patterns(layouts)

    ds = {
        "version": "1.0",
        "meta": {
            "source_file": pptx_path,
            "slide_size": {"width_emu": 12192000, "height_emu": 6858000},
            "aspect_ratio": "16:9",
            "confidence": _compute_confidence(theme, master, layouts),
        },
        "palette": {
            "theme_colors": theme["clrScheme"],
            "colors": _theme_to_color_tokens(theme),
        },
        "typography": {
            "fonts": theme["fontScheme"],
            "scale": _master_to_scale(master),
            "roles": MOCK_DESIGN_SYSTEM["typography"]["roles"],
        },
        "grid": MOCK_DESIGN_SYSTEM["grid"],
        "patterns": patterns,
        "rules": _compute_rules(layouts),
        "assets": {
            "logo": master.get("logo"),
        },
    }

    return ds


def _layouts_to_patterns(layouts: list[dict]) -> dict:
    """Преобразует layouts в словарь patterns."""
    patterns = {}
    for layout in layouts:
        pattern_id = _layout_to_pattern_id(layout)
        patterns[pattern_id] = {
            "id": pattern_id,
            "name": layout["name"],
            "layout_ref": layout["layout_ref"],
            "type": layout["type"],
            "placeholders": layout["placeholders"],
            "usage_count": 0,
        }
    return patterns


def _layout_to_pattern_id(layout: dict) -> str:
    """Генерирует pattern_id из типа и имени layout."""
    layout_type = layout.get("type", "obj")
    name = layout.get("name", "").lower().replace(" ", "_")

    if layout_type == "title" or "title" in name:
        return "title"
    if layout_type == "secHead" or "section" in name:
        return "section"
    if layout_type == "blank":
        return "blank"
    if "content" in name or layout_type == "obj":
        return "content_bullets"
    if "chart" in name:
        return "data_chart"
    if "table" in name:
        return "data_table"

    return f"layout_{layout['layout_ref'].replace('.xml', '')}"


def _theme_to_color_tokens(theme: dict) -> dict:
    """Преобразует theme clrScheme в color tokens."""
    clr = theme.get("clrScheme", {})
    return {
        "primary": {"hex": clr.get("accent1", "#000000"), "role": "brand", "scheme_ref": "accent1"},
        "secondary": {"hex": clr.get("accent2", "#000000"), "role": "brand", "scheme_ref": "accent2"},
        "text_primary": {"hex": clr.get("dk1", "#000000"), "role": "text", "scheme_ref": "dk1"},
        "text_inverse": {"hex": clr.get("lt1", "#FFFFFF"), "role": "text", "scheme_ref": "lt1"},
        "background": {"hex": clr.get("lt1", "#FFFFFF"), "role": "bg", "scheme_ref": "lt1"},
    }


def _master_to_scale(master: dict) -> dict:
    """Преобразует стили master в типографическую шкалу."""
    title_levels = master.get("title_style", {}).get("levels", {})
    body_levels = master.get("body_style", {}).get("levels", {})

    title_l1 = title_levels.get(1, {})
    body_l1 = body_levels.get(1, {})
    body_l2 = body_levels.get(2, body_l1)

    return {
        "h1": {"size_pt": title_l1.get("size_pt") or 32, "weight": 700},
        "body": {"size_pt": body_l1.get("size_pt") or 16, "weight": 400},
        "body_sm": {"size_pt": body_l2.get("size_pt") or 14, "weight": 400},
    }


def _compute_confidence(theme: dict, master: dict, layouts: list[dict]) -> float:
    """Оценивает уверенность парсинга."""
    score = 0.0
    if theme.get("clrScheme"):
        score += 0.3
    if theme.get("fontScheme"):
        score += 0.2
    if master.get("background"):
        score += 0.2
    if layouts:
        score += 0.3
    return round(score, 2)


def _compute_rules(layouts: list[dict]) -> dict:
    """Вычисляет правила из статистики layouts."""
    return {
        "max_font_families": 2,
        "min_contrast_ratio": 4.5,
        "max_bullets_per_slide": 6,
        "max_words_per_bullet": 15,
    }
