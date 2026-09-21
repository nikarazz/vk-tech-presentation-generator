from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ColorToken:
    hex: str
    role: str
    scheme_ref: Optional[str] = None
    usage_count: int = 0

@dataclass
class FontToken:
    family: str
    fallback: str = "Arial"
    roles: list[str] = field(default_factory=list)

@dataclass
class DesignSystem:
    version: str = "1.0"
    meta: dict = field(default_factory=dict)
    palette: dict = field(default_factory=dict)
    typography: dict = field(default_factory=dict)
    grid: dict = field(default_factory=dict)
    patterns: dict = field(default_factory=dict)
    rules: dict = field(default_factory=dict)
    assets: dict = field(default_factory=dict)