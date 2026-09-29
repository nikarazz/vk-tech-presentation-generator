"""Главный модуль аудита презентаций."""
from __future__ import annotations

import time

from audit.deterministic import (
    check_bounds,
    check_colors,
    check_density,
    check_integrity,
    check_overlap,
    check_typography,
)
from shared.schemas.audit import AuditReport


def run_audit(presentation, design_system) -> AuditReport:
    """Запустить все детерминированные проверки."""
    start = time.time()
    issues = []

    issues += check_bounds(presentation, design_system)
    issues += check_overlap(presentation, design_system)
    issues += check_typography(presentation, design_system)
    issues += check_colors(presentation, design_system)
    issues += check_density(presentation, design_system)
    issues += check_integrity(presentation, design_system)

    return AuditReport(
        issues=issues,
        checked_slides=len(presentation.slides) if hasattr(presentation, "slides") else 0,
        duration_sec=time.time() - start,
    )
