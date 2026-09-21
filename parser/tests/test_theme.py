from parser.parse_template import parse_template
from parser.theme_parser import parse_theme
from parser.master_parser import parse_master
from parser.layout_parser import parse_layouts


def test_parse_theme():
    theme = parse_theme("data/templates/template1.pptx")
    assert "clrScheme" in theme
    assert "fontScheme" in theme
    assert len(theme["clrScheme"]) > 0


def test_parse_master():
    theme = parse_theme("data/templates/template1.pptx")
    master = parse_master("data/templates/template1.pptx", theme)
    assert "title_style" in master
    assert "body_style" in master


def test_parse_layouts():
    layouts = parse_layouts("data/templates/template1.pptx")
    assert len(layouts) > 0
    assert "layout_ref" in layouts[0]
    assert "placeholders" in layouts[0]


def test_parse_template():
    ds = parse_template("data/templates/template1.pptx")
    assert "theme_colors" in ds["palette"]
    assert "fonts" in ds["typography"]
    assert ds["meta"]["confidence"] > 0
    assert len(ds["patterns"]) > 0
    print("Palette:", ds["palette"]["theme_colors"])
    print("Fonts:", ds["typography"]["fonts"])
    print("Patterns:", list(ds["patterns"].keys()))
    print("Confidence:", ds["meta"]["confidence"])
