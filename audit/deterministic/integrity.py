"""Проверка целостности презентации."""
from __future__ import annotations

from shared.schemas.audit import Issue, IssueSeverity, IssueType


def check_integrity(presentation, design_system) -> list[Issue]:
    """Проверить пустые слайды и целостность структуры."""
    issues: list[Issue] = []
    if not getattr(presentation, "slides", None):
        issues.append(Issue(
            slide=0,
            type=IssueType.INTEGRITY,
            severity=IssueSeverity.HIGH,
            message="Презентация не содержит слайдов",
        ))
        return issues

    for slide_idx, slide in enumerate(presentation.slides):
        shapes = list(slide.shapes)
        if not shapes:
            issues.append(Issue(
                slide=slide_idx,
                type=IssueType.INTEGRITY,
                severity=IssueSeverity.HIGH,
                message="Пустой слайд",
            ))
            continue
        has_content = False
        for shape in shapes:
            if getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip():
                has_content = True
                break
        if not has_content:
            issues.append(Issue(
                slide=slide_idx,
                type=IssueType.INTEGRITY,
                severity=IssueSeverity.MEDIUM,
                message="Слайд без текстового содержимого",
            ))
    return issues
