"""Проверка наложения объектов друг на друга."""
from __future__ import annotations

from shared.schemas.audit import Issue, IssueSeverity, IssueType


def _intersect(a: tuple, b: tuple) -> float:
    ax1, ay1, aw, ah = a
    bx1, by1, bw, bh = b
    ax2, ay2 = ax1 + aw, ay1 + ah
    bx2, by2 = bx1 + bw, by1 + bh
    dx = max(0, min(ax2, bx2) - max(ax1, bx1))
    dy = max(0, min(ay2, by2) - max(ay1, by1))
    return dx * dy


def check_overlap(presentation, design_system) -> list[Issue]:
    """Найти наложения объектов на слайдах."""
    issues: list[Issue] = []
    for slide_idx, slide in enumerate(presentation.slides):
        shapes = list(slide.shapes)
        for i in range(len(shapes)):
            for j in range(i + 1, len(shapes)):
                a, b = shapes[i], shapes[j]
                ra = (a.left or 0, a.top or 0, a.width or 0, a.height or 0)
                rb = (b.left or 0, b.top or 0, b.width or 0, b.height or 0)
                area = _intersect(ra, rb)
                if area <= 0:
                    continue
                min_area = min(ra[2] * ra[3], rb[2] * rb[3])
                if min_area > 0 and area / min_area > 0.3:
                    issues.append(Issue(
                        slide=slide_idx,
                        shape_id=getattr(a, "shape_id", None),
                        type=IssueType.OVERLAP,
                        severity=IssueSeverity.MEDIUM,
                        message=f"Объекты пересекаются (площадь={area:.0f})",
                        bbox=ra,
                    ))
    return issues
