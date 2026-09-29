"""Рендер слайда в изображение для VLM-аудита."""
from __future__ import annotations

from pathlib import Path


def render_slide_to_png(presentation_path: str, slide_index: int, output_dir: str = "tmp") -> str | None:
    """
    Отрендерить слайд в PNG.

    Полноценная реализация требует LibreOffice:
        soffice --headless --convert-to png <file.pptx>

    Заготовка.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"slide_{slide_index}.png"
    return str(output_path) if output_path.exists() else None


def render_all_slides(presentation_path: str, output_dir: str = "tmp") -> list[str]:
    """Отрендерить все слайды. Заготовка."""
    return []
