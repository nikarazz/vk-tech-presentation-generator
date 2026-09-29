"""Проверка перегруза слайда элементами."""
from __future__ import annotations

from shared.schemas.audit import Issue, IssueSeverity, IssueType

MAX_SHAPES = 15
MAX_BULLETS = 7


def check_density(presentation, design_system) -> list[Issue]:
    """Проверить плотность элементов на слайде."""
    issues: list[Issue] = []
    for slide_idx, slide in enumerate(presentation.slides):
        shapes = list(slide.shapes)
        if len(shapes) > MAX_SHAPES:
            issues.append(Issue(
                slide=slide_idx,
                type=IssueType.DENSITY,
                severity=IssueSeverity.MEDIUM,
                message=f"Слайд перегружен: {len(shapes)} объектов",
            ))
        for shape in shapes:
            if not getattr(shape, "has_text_frame", False):
                continue
            bullets = sum(1 for p in shape.text_frame.paragraphs if p.text.strip())
            if bullets > MAX_BULLETS:
                issues.append(Issue(
                    slide=slide_idx,
                    shape_id=getattr(shape, "shape_id", None),
                    type=IssueType.DENSITY,
                    severity=IssueSeverity.MEDIUM,
                    message=f"Слишком много пунктов: {bullets}",
                    bbox=(shape.left, shape.top, shape.width, shape.height),
                ))
    return issues
