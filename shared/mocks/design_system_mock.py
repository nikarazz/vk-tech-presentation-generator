"""Мок дизайн-системы для параллельной разработки."""

MOCK_DESIGN_SYSTEM = {
    "version": "1.0",
    "meta": {
        "source_file": "mock.pptx",
        "slide_size": {"width_emu": 12192000, "height_emu": 6858000},
        "aspect_ratio": "16:9",
        "language": "ru",
        "confidence": 1.0,
    },
    "palette": {
        "colors": {
            "primary": {"hex": "#0077FF", "role": "brand"},
            "text_primary": {"hex": "#1A1A1A", "role": "text"},
            "background": {"hex": "#FFFFFF", "role": "bg"},
        }
    },
    "typography": {
        "scale": {
            "h1": {"size_pt": 32, "weight": 700},
            "body": {"size_pt": 16, "weight": 400},
        },
        "roles": {"slide_title": "h1", "bullet": "body"},
    },
    "patterns": {
        "title": {"name": "Титульный слайд"},
        "content_bullets": {
            "name": "Контент с буллетами",
            "body_constraints": {"max_bullets": 6, "max_words_per_bullet": 15},
        },
        "data_chart": {"name": "Слайд с диаграммой"},
        "closing": {"name": "Финальный слайд"},
    },
    "rules": {
        "max_font_families": 2,
        "min_contrast_ratio": 4.5,
        "max_bullets_per_slide": 6,
    },
}
