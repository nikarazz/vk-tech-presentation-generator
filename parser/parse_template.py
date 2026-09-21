from parser.theme_parser import parse_theme
from shared.mocks.design_system_mock import MOCK_DESIGN_SYSTEM

def parse_template(pptx_path: str) -> dict:
    theme = parse_theme(pptx_path)
    
    ds = dict(MOCK_DESIGN_SYSTEM)
    ds["meta"] = {
        "source_file": pptx_path,
        "slide_size": {"width_emu": 12192000, "height_emu": 6858000},
        "aspect_ratio": "16:9",
        "confidence": 0.5,
    }
    ds["palette"] = {
        "theme_colors": theme["clrScheme"],
        "colors": MOCK_DESIGN_SYSTEM["palette"]["colors"],
    }
    ds["typography"] = {
        "fonts": theme["fontScheme"],
        "scale": MOCK_DESIGN_SYSTEM["typography"]["scale"],
        "roles": MOCK_DESIGN_SYSTEM["typography"]["roles"],
    }
    return ds
