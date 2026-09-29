"""Схемы аудита."""
from dataclasses import dataclass, field
from enum import Enum


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueType(str, Enum):
    BOUNDS = "bounds"
    OVERLAP = "overlap"
    TYPOGRAPHY = "typography"
    COLORS = "colors"
    DENSITY = "density"
    INTEGRITY = "integrity"
    CONTENT = "content"


@dataclass
class Issue:
    slide_id: int
    rule_id: str
    severity: IssueSeverity
    issue_type: IssueType
    message: str
    element_id: str | None = None
    details: dict = field(default_factory=dict)


@dataclass
class AuditReport:
    total_problems: int = 0
    by_severity: dict = field(default_factory=dict)
    problems: list[Issue] = field(default_factory=list)
