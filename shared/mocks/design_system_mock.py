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
        "fonts": {
            "primary": {"family": "Arial", "fallback": "Arial"},
            "secondary": {"family": "Arial", "fallback": "Arial"},
        },
        "scale": {
            "h1": {"size_pt": 32, "weight": 700},
            "body": {"size_pt": 16, "weight": 400},
        },
        "roles": {"slide_title": "h1", "bullet": "body"},
    },
    "grid": {
        "columns": 12,
        "margin": {"top_emu": 457200, "right_emu": 457200, "bottom_emu": 457200, "left_emu": 457200},
        "safe_area": {"top_emu": 685800, "right_emu": 685800, "bottom_emu": 685800, "left_emu": 685800},
    },
    "patterns": {
        "title": {
            "layout_ref": "slideLayout1.xml",
            "placeholders": [{"type": "title", "idx": 0, "role": "slide_title"}],
        },
        "content_bullets": {
            "layout_ref": "slideLayout3.xml",
            "placeholders": [
                {"type": "title", "idx": 0, "role": "slide_title"},
                {"type": "body", "idx": 1, "role": "bullet"},
            ],
            "body_constraints": {"max_bullets": 6, "max_words_per_bullet": 15},
        },
        "closing": {
            "layout_ref": "slideLayout8.xml",
            "placeholders": [{"type": "title", "idx": 0, "role": "slide_title"}],
        },
    },
    "rules": {
        "max_font_families": 2,
        "min_contrast_ratio": 4.5,
        "max_bullets_per_slide": 6,
    },
}