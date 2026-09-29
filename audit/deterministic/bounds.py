"""Проверка выхода объектов за границы слайда и safe area."""
from __future__ import annotations

from shared.schemas.audit import Issue, IssueSeverity, IssueType


def check_bounds(presentation, design_system) -> list[Issue]:
    """Проверить, что объекты не выходят за safe area."""
    issues: list[Issue] = []

    slide_w = design_system.slide_width
    slide_h = design_system.slide_height
    safe = getattr(design_system, "safe_area", None)
    safe_left = getattr(safe, "left", 0) if safe else 0
    safe_top = getattr(safe, "top", 0) if safe else 0
    safe_right = getattr(safe, "right", 0) if safe else 0
    safe_bottom = getattr(safe, "bottom", 0) if safe else 0

    for slide_idx, slide in enumerate(presentation.slides):
        for shape in slide.shapes:
            x = getattr(shape, "left", 0) or 0
            y = getattr(shape, "top", 0) or 0
            w = getattr(shape, "width", 0) or 0
            h = getattr(shape, "height", 0) or 0

            if x < safe_left or y < safe_top:
                issues.append(Issue(
                    slide=slide_idx,
                    shape_id=getattr(shape, "shape_id", None),
                    type=IssueType.BOUNDS,
                    severity=IssueSeverity.HIGH,
                    message=f"Объект выходит за верхний/левый край (x={x}, y={y})",
                    bbox=(x, y, w, h),
                ))
            if x + w > slide_w - safe_right or y + h > slide_h - safe_bottom:
                issues.append(Issue(
                    slide=slide_idx,
                    shape_id=getattr(shape, "shape_id", None),
                    type=IssueType.BOUNDS,
                    severity=IssueSeverity.HIGH,
                    message="Объект выходит за правый/нижний край слайда",
                    bbox=(x, y, w, h),
                ))
    return issues
