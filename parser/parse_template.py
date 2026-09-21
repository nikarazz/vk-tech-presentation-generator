"""
Главная функция парсера.
"""
import logging
from parser.theme_parser import parse_theme
from parser.master_parser import parse_master
from parser.layout_parser import parse_layouts
from parser.slide_parser import parse_slides
from parser.grid_extractor import extract_grid
from parser.pattern_clusterer import cluster_patterns, compute_pattern_constraints

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_template(pptx_path: str) -> dict:
    errors = []

    try:
        theme = parse_theme(pptx_path)
    except Exception as e:
        logger.error(f"Theme parsing failed: {e}")
        theme = {"clrScheme": {}, "fontScheme": {}}
        errors.append("theme")

    try:
        master = parse_master(pptx_path, theme)
    except Exception as e:
        logger.error(f"Master parsing failed: {e}")
        master = {"background": None, "logo": None, "title_style": {}, "body_style": {}}
        errors.append("master")

    try:
        layouts = parse_layouts(pptx_path)
    except Exception as e:
        logger.error(f"Layouts parsing failed: {e}")
        layouts = []
        errors.append("layouts")

    try:
        slides = parse_slides(pptx_path, theme)
    except Exception as e:
        logger.error(f"Slides parsing failed: {e}")
        slides = []
        errors.append("slides")

    try:
        grid = extract_grid(slides, layouts)
    except Exception as e:
        logger.error(f"Grid extraction failed: {e}")
        grid = _default_grid()
        errors.append("grid")

    try:
        patterns = cluster_patterns(layouts, slides)
        patterns = compute_pattern_constraints(patterns, slides)
    except Exception as e:
        logger.error(f"Pattern clustering failed: {e}")
        patterns = {}
        errors.append("patterns")

    return {
        "version": "1.0",
        "meta": {
            "source_file": pptx_path,
            "slide_size": {"width_emu": 12192000, "height_emu": 6858000},
            "aspect_ratio": "16:9",
            "slide_count": len(slides),
            "layout_count": len(layouts),
            "confidence": _compute_confidence(theme, master, layouts, slides, grid, errors),
            "errors": errors,
        },
        "palette": {
            "theme_colors": theme.get("clrScheme", {}),
            "colors": _theme_to_color_tokens(theme),
        },
        "typography": {
            "fonts": theme.get("fontScheme", {}),
            "scale": _master_to_scale(master),
            "roles": _default_roles(),
        },
        "grid": grid,
        "patterns": patterns,
        "rules": _compute_rules(patterns),
        "assets": {
            "logo": master.get("logo"),
        },
    }


def _theme_to_color_tokens(theme: dict) -> dict:
    clr = theme.get("clrScheme", {})
    if not clr:
        clr = {
            "dk1": "#000000", "lt1": "#FFFFFF",
            "accent1": "#0077FF", "accent2": "#001A33",
            "accent3": "#FF3D00",
        }
    return {
        "primary": {"hex": clr.get("accent1", "#0077FF"), "role": "brand", "scheme_ref": "accent1"},
        "secondary": {"hex": clr.get("accent2", "#001A33"), "role": "brand", "scheme_ref": "accent2"},
        "accent": {"hex": clr.get("accent3", "#FF3D00"), "role": "accent", "scheme_ref": "accent3"},
        "text_primary": {"hex": clr.get("dk1", "#000000"), "role": "text", "scheme_ref": "dk1"},
        "text_secondary": {"hex": clr.get("dk2", "#44546A"), "role": "text", "scheme_ref": "dk2"},
        "text_inverse": {"hex": clr.get("lt1", "#FFFFFF"), "role": "text", "scheme_ref": "lt1"},
        "background": {"hex": clr.get("lt1", "#FFFFFF"), "role": "bg", "scheme_ref": "lt1"},
        "surface": {"hex": clr.get("lt2", "#F5F7FA"), "role": "bg", "scheme_ref": "lt2"},
    }


def _master_to_scale(master: dict) -> dict:
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


def _default_roles() -> dict:
    return {
        "slide_title": "h1",
        "slide_subtitle": "body",
        "section_title": "h1",
        "bullet": "body",
        "bullet_sub": "body_sm",
        "chart_label": "body_sm",
        "table_header": "body_sm",
        "table_cell": "body_sm",
        "footer": "body_sm",
    }


def _compute_confidence(theme, master, layouts, slides, grid, errors) -> float:
    score = 0.0
    if theme.get("clrScheme"):
        score += 0.2
    if theme.get("fontScheme"):
        score += 0.15
    if master.get("title_style", {}).get("levels"):
        score += 0.15
    if master.get("body_style", {}).get("levels"):
        score += 0.1
    if layouts:
        score += 0.15
    if slides:
        score += 0.15
    if grid.get("guides", {}).get("vertical"):
        score += 0.1

    score -= len(errors) * 0.1
    return round(max(0.0, min(score, 1.0)), 2)


def _compute_rules(patterns: dict) -> dict:
    max_bullets = 0
    max_words = 0
    for p in patterns.values():
        bc = p.get("body_constraints", {})
        max_bullets = max(max_bullets, bc.get("max_bullets", 0))
        max_words = max(max_words, bc.get("max_words_per_bullet", 0))

    return {
        "max_font_families": 2,
        "min_contrast_ratio": 4.5,
        "max_bullets_per_slide": max_bullets or 6,
        "max_words_per_bullet": max_words or 15,
        "max_table_rows": 7,
        "max_table_cols": 5,
        "max_chart_series": 5,
    }


def _default_grid() -> dict:
    return {
        "columns": 12,
        "margin": {"top_emu": 457200, "right_emu": 457200, "bottom_emu": 457200, "left_emu": 457200},
        "safe_area": {"top_emu": 685800, "right_emu": 685800, "bottom_emu": 685800, "left_emu": 685800},
        "gutter_emu": 228600,
        "guides": {"vertical": [], "horizontal": []},
    }
