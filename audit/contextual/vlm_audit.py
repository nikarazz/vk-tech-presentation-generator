"""Контекстный аудит слайдов с помощью VLM."""
from __future__ import annotations

from shared.schemas.audit import Issue
from .prompts import VLM_AUDIT_PROMPT


def audit_slide_with_vlm(image_path: str, client=None) -> list[Issue]:
    """
    Отправить изображение слайда в VLM и получить список проблем.

    Заготовка: полноценная реализация требует API-клиента
    и модели ≤ 35M параметров.
    """
    if client is None:
        return []
    # TODO: реализовать вызов VLM
    return []
