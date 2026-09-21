from parser.parse_template import parse_template
from parser.theme_parser import parse_theme
from parser.master_parser import parse_master
from parser.layout_parser import parse_layouts
from parser.slide_parser import parse_slides
from parser.grid_extractor import extract_grid
from parser.pattern_clusterer import cluster_patterns, get_used_patterns


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
    assert master["title_style"]["levels"]


def test_parse_layouts():
    layouts = parse_layouts("data/templates/template1.pptx")
    assert len(layouts) > 0
    assert "layout_ref" in layouts[0]
    assert "placeholders" in layouts[0]


def test_parse_slides():
    theme = parse_theme("data/templates/template1.pptx")
    slides = parse_slides("data/templates/template1.pptx", theme)
    assert len(slides) > 0
    assert "elements" in slides[0]
    assert "slide_id" in slides[0]


def test_extract_grid():
    theme = parse_theme("data/templates/template1.pptx")
    layouts = parse_layouts("data/templates/template1.pptx")
    slides = parse_slides("data/templates/template1.pptx", theme)
    grid = extract_grid(slides, layouts)
    assert "columns" in grid
    assert "margin" in grid
    assert grid["columns"] > 0


def test_cluster_patterns():
    theme = parse_theme("data/templates/template1.pptx")
    layouts = parse_layouts("data/templates/template1.pptx")
    slides = parse_slides("data/templates/template1.pptx", theme)
    patterns = cluster_patterns(layouts, slides)
    assert len(patterns) > 0
    assert "usage_count" in list(patterns.values())[0]


def test_parse_template():
    ds = parse_template("data/templates/template1.pptx")
    assert "theme_colors" in ds["palette"]
    assert "fonts" in ds["typography"]
    assert ds["meta"]["confidence"] > 0.5
    assert len(ds["patterns"]) > 0
    assert ds["meta"]["slide_count"] >= 0
    print("Confidence:", ds["meta"]["confidence"])
    print("Patterns:", list(ds["patterns"].keys()))
