from parser.parse_template import parse_template

def test_parse_template():
    ds = parse_template("data/templates/template1.pptx")
    assert "theme_colors" in ds["palette"]
    assert "fonts" in ds["typography"]
    assert ds["meta"]["confidence"] > 0
    print("Palette:", ds["palette"]["theme_colors"])
    print("Fonts:", ds["typography"]["fonts"])
