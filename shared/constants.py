EMU_PER_INCH = 914400
EMU_PER_PT = 12700
EMU_PER_CM = 360000

SLIDE_16_9_WIDTH_EMU = 12192000
SLIDE_16_9_HEIGHT_EMU = 6858000

"""
Контракты между слоями пайплайна.

A (Parser) реализует: parse_template.
B (Generation) реализует: plan_content, layout_slides, export_pptx.
C (Audit) реализует: audit_presentation, repair_presentation.
"""

def parse_template(pptx_path: str) -> dict:
    """A: .pptx → DesignSystem (dict)."""
    raise NotImplementedError

def plan_content(brief: str, content_pack: dict, ds: dict) -> dict:
    """B: бриф + DesignSystem → SlidePlan (dict)."""
    raise NotImplementedError

def layout_slides(plan: dict, ds: dict) -> dict:
    """B: SlidePlan + DesignSystem → Presentation (dict)."""
    raise NotImplementedError

def audit_presentation(pres: dict, ds: dict) -> dict:
    """C: Presentation + DesignSystem → AuditReport (dict)."""
    raise NotImplementedError

def repair_presentation(pres: dict, report: dict, ds: dict) -> dict:
    """B: Presentation + AuditReport → исправленная Presentation."""
    raise NotImplementedError

def export_pptx(pres: dict, ds: dict, template_path: str, output_path: str) -> None:
    """B: Presentation → .pptx."""
    raise NotImplementedError