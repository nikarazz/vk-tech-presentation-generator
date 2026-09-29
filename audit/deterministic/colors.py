"""Проверка контраста текста и фона."""
from __future__ import annotations

from shared.schemas.audit import Issue, IssueSeverity, IssueType

MIN_CONTRAST = 4.5


def _luminance(rgb: tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    l1, l2 = _luminance(fg), _luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def check_colors(presentation, design_system) -> list[Issue]:
    """Проверить контраст текста и фона."""
    issues: list[Issue] = []
    bg = (255, 255, 255)
    colors = getattr(design_system, "colors", None)
    if colors and getattr(colors, "background", None):
        bg = colors.background

    for slide_idx, slide in enumerate(presentation.slides):
        for shape in slide.shapes:
            if not getattr(shape, "has_text_frame", False):
                continue
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    color = getattr(run.font, "color", None)
                    rgb = getattr(color, "rgb", None) if color else None
                    if rgb is None:
                        continue
                    if isinstance(rgb, str):
                        rgb = tuple(int(rgb[i:i+2], 16) for i in (0, 2, 4))
                    ratio = contrast_ratio(tuple(rgb), tuple(bg))
                    if ratio < MIN_CONTRAST:
                        issues.append(Issue(
                            slide=slide_idx,
                            shape_id=getattr(shape, "shape_id", None),
                            type=IssueType.COLORS,
                            severity=IssueSeverity.MEDIUM,
                            message=f"Плохой контраст: {ratio:.2f}",
                            bbox=(shape.left, shape.top, shape.width, shape.height),
                        ))
    return issues
