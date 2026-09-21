from dataclasses import dataclass, field

@dataclass
class Element:
    element_id: str
    type: str
    role: str
    bbox: dict
    text: str = ""
    style: dict = field(default_factory=dict)

@dataclass
class Slide:
    slide_id: int
    pattern_id: str
    layout_ref: str
    elements: list[Element] = field(default_factory=list)

@dataclass
class Presentation:
    template_path: str
    slides: list[Slide] = field(default_factory=list)