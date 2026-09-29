"""Модели данных для аудита презентаций."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class IssueSeverity(str, Enum):
    """Степень серьёзности проблемы."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IssueType(str, Enum):
    """Тип проблемы."""
    BOUNDS = "bounds"
    OVERLAP = "overlap"
    TYPOGRAPHY = "typography"
    COLORS = "colors"
    DENSITY = "density"
    INTEGRITY = "integrity"
    CONTEXTUAL = "contextual"


class Issue(BaseModel):
    """Одна найденная проблема."""
    slide: int = Field(..., description="Номер слайда (0-based)")
    shape_id: Optional[int] = Field(None, description="ID фигуры")
    type: IssueType = Field(..., description="Тип проблемы")
    severity: IssueSeverity = Field(..., description="Серьёзность")
    message: str = Field(..., description="Описание проблемы")
    bbox: Optional[tuple[float, float, float, float]] = Field(
        None, description="Координаты (left, top, width, height)"
    )


class AuditReport(BaseModel):
    """Результат аудита."""
    issues: list[Issue] = Field(default_factory=list)
    checked_slides: int = Field(0, description="Сколько слайдов проверено")
    duration_sec: float = Field(0.0, description="Время аудита в секундах")

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def by_slide(self) -> dict[int, list[Issue]]:
        """Сгруппировать проблемы по слайдам."""
        result: dict[int, list[Issue]] = {}
        for issue in self.issues:
            result.setdefault(issue.slide, []).append(issue)
        return result
