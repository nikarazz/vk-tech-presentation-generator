from pydantic import BaseModel
from typing import Optional

class SlideSpec(BaseModel):
    pattern_id: str
    title: str
    bullets: Optional[list[str]] = None
    subtitle: Optional[str] = None
    chart: Optional[dict] = None
    table: Optional[dict] = None

class SlidePlan(BaseModel):
    slides: list[SlideSpec]