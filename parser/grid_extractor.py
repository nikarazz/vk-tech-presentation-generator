"""
Извлечение сетки из координат слайдов.

Сетка в .pptx неявная. Мы выводим её статистически:
  - собираем все координаты элементов
  - кластеризуем близкие значения
  - получаем направляющие, колонки, margin

Используется:
  - Layout Engine — для выравнивания новых элементов
  - Auditor — для проверки, что элементы не выходят за safe_area
"""
from collections import Counter


SLIDE_WIDTH_EMU = 12192000
SLIDE_HEIGHT_EMU = 6858000


def extract_grid(slides: list[dict], layouts: list[dict]) -> dict:
    """
    Извлекает сетку из слайдов и layouts.

    Возвращает:
      {
        "columns": 12,
        "margin": {"top_emu", "right_emu", "bottom_emu", "left_emu"},
        "safe_area": {"top_emu", "right_emu", "bottom_emu", "left_emu"},
        "gutter_emu": ...,
        "guides": {
          "vertical": [x1, x2, ...],
          "horizontal": [y1, y2, ...],
        },
      }
    """
    lefts = []
    tops = []
    rights = []
    bottoms = []

    # Собираем координаты со всех слайдов
    for slide in slides:
        for el in slide.get("elements", []):
            bbox = el.get("bbox", {})
            if not bbox or bbox.get("w_emu", 0) == 0:
                continue
            lefts.append(bbox["x_emu"])
            tops.append(bbox["y_emu"])
            rights.append(bbox["x_emu"] + bbox["w_emu"])
            bottoms.append(bbox["y_emu"] + bbox["h_emu"])

    # Собираем координаты со всех layouts
    for layout in layouts:
        for ph in layout.get("placeholders", []):
            pos = ph.get("position")
            if not pos:
                continue
            lefts.append(pos["x_emu"])
            tops.append(pos["y_emu"])
            rights.append(pos["x_emu"] + pos["w_emu"])
            bottoms.append(pos["y_emu"] + pos["h_emu"])

    if not lefts:
        return _default_grid()

    # Кластеризуем
    vertical_guides = _cluster(lefts, tolerance=200000)
    horizontal_guides = _cluster(tops, tolerance=200000)

    # Margin — минимальные отступы
    margin_left = min(lefts) if lefts else 0
    margin_top = min(tops) if tops else 0
    margin_right = SLIDE_WIDTH_EMU - max(rights) if rights else 0
    margin_bottom = SLIDE_HEIGHT_EMU - max(bottoms) if bottoms else 0

    # Safe area — на 10% больше margin
    safe_margin_left = int(margin_left * 1.2)
    safe_margin_top = int(margin_top * 1.2)
    safe_margin_right = int(margin_right * 1.2)
    safe_margin_bottom = int(margin_bottom * 1.2)

    # Колонки — по количеству вертикальных направляющих
    columns = max(len(vertical_guides), 4)

    # Gutter — среднее расстояние между направляющими
    gutter = 0
    if len(vertical_guides) > 1:
        diffs = [vertical_guides[i+1] - vertical_guides[i]
                 for i in range(len(vertical_guides) - 1)]
        gutter = int(sum(diffs) / len(diffs)) if diffs else 0

    return {
        "columns": columns,
        "margin": {
            "top_emu": margin_top,
            "right_emu": margin_right,
            "bottom_emu": margin_bottom,
            "left_emu": margin_left,
        },
        "safe_area": {
            "top_emu": safe_margin_top,
            "right_emu": safe_margin_right,
            "bottom_emu": safe_margin_bottom,
            "left_emu": safe_margin_left,
        },
        "gutter_emu": gutter,
        "guides": {
            "vertical": vertical_guides,
            "horizontal": horizontal_guides,
        },
    }


def _cluster(values: list[int], tolerance: int = 200000) -> list[int]:
    """
    Кластеризует близкие значения.

    Например: [100, 105, 102, 500, 505] → [102, 502]
    """
    if not values:
        return []

    sorted_vals = sorted(values)
    clusters = []
    current = [sorted_vals[0]]

    for v in sorted_vals[1:]:
        if v - current[-1] <= tolerance:
            current.append(v)
        else:
            clusters.append(sum(current) // len(current))
            current = [v]

    clusters.append(sum(current) // len(current))
    return clusters


def _default_grid() -> dict:
    """Дефолтная сетка, если не удалось извлечь."""
    return {
        "columns": 12,
        "margin": {"top_emu": 457200, "right_emu": 457200, "bottom_emu": 457200, "left_emu": 457200},
        "safe_area": {"top_emu": 685800, "right_emu": 685800, "bottom_emu": 685800, "left_emu": 685800},
        "gutter_emu": 228600,
        "guides": {"vertical": [], "horizontal": []},
    }
