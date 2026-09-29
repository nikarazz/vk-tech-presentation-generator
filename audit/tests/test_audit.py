"""Тесты аудита."""
from types import SimpleNamespace

from audit.audit import run_audit
from audit.deterministic import check_bounds, check_integrity


def make_shape(left, top, width, height, shape_id=1, text=""):
    """Создать фигуру-заглушку для теста."""
    tf = SimpleNamespace(paragraphs=[], text=text)
    return SimpleNamespace(
        left=left, top=top, width=width, height=height,
        shape_id=shape_id, has_text_frame=bool(text),
        text_frame=tf,
    )


def make_presentation(shapes_per_slide):
    """Создать презентацию-заглушку."""
    slides = [SimpleNamespace(shapes=shapes) for shapes in shapes_per_slide]
    return SimpleNamespace(slides=slides)


def make_design_system(w=1280, h=720):
    """Создать дизайн-систему-заглушку."""
    return SimpleNamespace(
        slide_width=w, slide_height=h,
        safe_area=SimpleNamespace(left=0, top=0, right=0, bottom=0),
        colors=SimpleNamespace(background=(255, 255, 255)),
    )


def test_bounds_ok():
    """Объект внутри слайда — проблем нет."""
    pres = make_presentation([[make_shape(100, 100, 200, 100)]])
    ds = make_design_system()
    assert check_bounds(pres, ds) == []


def test_bounds_outside():
    """Объект за краем — должна быть проблема."""
    pres = make_presentation([[make_shape(1200, 100, 200, 100)]])
    ds = make_design_system()
    issues = check_bounds(pres, ds)
    assert len(issues) == 1


def test_integrity_empty_slide():
    """Пустой слайд — должна быть проблема."""
    pres = make_presentation([[]])
    ds = make_design_system()
    issues = check_integrity(pres, ds)
    assert len(issues) == 1


def test_run_audit_returns_report():
    """run_audit должен вернуть AuditReport."""
    pres = make_presentation([[make_shape(100, 100, 200, 100)]])
    ds = make_design_system()
    report = run_audit(pres, ds)
    assert report.checked_slides == 1
