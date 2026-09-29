"""Проверка типографики: мелкий шрифт."""
from __future__ import annotations

from shared.schemas.audit import Issue, IssueSeverity, IssueType

MIN_FONT_SIZE = 12


def check_typography(presentation, design_system) -> list[Issue]:
    """Проверить размеры шрифтов."""
    issues: list[Issue] = []
    for slide_idx, slide in enumerate(presentation.slides):
        for shape in slide.shapes:
            if not getattr(shape, "has_text_frame", False):
                continue
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    size = getattr(run.font, "size", None)
                    size_pt = size.pt if size else None
                    if size_pt is not None and size_pt < MIN_FONT_SIZE:
                        issues.append(Issue(
                            slide=slide_idx,
                            shape_id=getattr(shape, "shape_id", None),
                            type=IssueType.TYPOGRAPHY,
                            severity=IssueSeverity.MEDIUM,
                            message=f"Слишком мелкий шрифт: {size_pt}pt",
                            bbox=(shape.left, shape.top, shape.width, shape.height),
                        ))
    return issues
