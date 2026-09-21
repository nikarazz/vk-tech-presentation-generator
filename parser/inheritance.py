"""
Резолвер наследования свойств из OOXML.

На вход — XML-элемент. На выход — финальное значение:
  - цвет (hex + alpha)
  - кегль (pt)
  - шрифт (family)
"""
from lxml import etree
from shared.utils.color import apply_lum

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
}


def resolve_color(elem: etree._Element, theme: dict) -> tuple[str | None, float]:
    """
    Резолвит цвет из XML-элемента.

    Возвращает (hex, alpha), где alpha ∈ [0, 1].
    Если цвет не найден — (None, 1.0).
    """
    if elem is None:
        return None, 1.0

    # 1. Прямой srgbClr
    srgb = elem.find('.//a:srgbClr', NS)
    if srgb is not None:
        hex_val = f"#{srgb.get('val')}"
        alpha = _extract_alpha(srgb)
        return hex_val, alpha

    # 2. schemeClr — из theme
    scheme = elem.find('.//a:schemeClr', NS)
    if scheme is not None:
        scheme_name = scheme.get('val')
        base_hex = theme.get('clrScheme', {}).get(scheme_name)
        if base_hex is None:
            return None, 1.0

        # Модификации lumMod/lumOff
        lum_mod_el = scheme.find('a:lumMod', NS)
        lum_off_el = scheme.find('a:lumOff', NS)

        lum_mod = int(lum_mod_el.get('val')) / 100000 if lum_mod_el is not None else 1.0
        lum_off = int(lum_off_el.get('val')) / 100000 if lum_off_el is not None else 0.0

        if lum_mod != 1.0 or lum_off != 0.0:
            base_hex = apply_lum(base_hex, lum_mod, lum_off)

        alpha = _extract_alpha(scheme)
        return base_hex, alpha

    return None, 1.0


def _extract_alpha(elem: etree._Element) -> float:
    """Извлекает alpha из элемента. По умолчанию 1.0."""
    alpha_el = elem.find('a:alpha', NS)
    if alpha_el is not None:
        return int(alpha_el.get('val')) / 100000
    return 1.0


def resolve_font_size(elem: etree._Element) -> float | None:
    """
    Резолвит кегль из XML-элемента.

    Ищет атрибут 'sz' на разных уровнях:
      1. rPr (run properties) — локальный
      2. defRPr (default run properties) — из paragraph
      3. Наследуется от placeholder/layout/master — пока не реализовано

    Возвращает размер в pt или None.
    """
    if elem is None:
        return None

    # Ищем rPr или defRPr
    rpr = elem.find('.//a:rPr', NS)
    if rpr is None:
        rpr = elem.find('.//a:defRPr', NS)

    if rpr is not None and rpr.get('sz'):
        # sz в 1/100 pt
        return int(rpr.get('sz')) / 100

    return None


def resolve_font_family(elem: etree._Element, theme: dict) -> str | None:
    """
    Резолвит шрифт из XML-элемента.

    Обрабатывает:
      - 'latin typeface' — прямой шрифт
      - '+mj-lt' — major font из theme
      - '+mn-lt' — minor font из theme

    Возвращает название шрифта или None.
    """
    if elem is None:
        return None

    latin = elem.find('.//a:latin', NS)
    if latin is None:
        return None

    typeface = latin.get('typeface')
    if typeface is None:
        return None

    # Ссылка на theme
    if typeface == '+mj-lt':
        return theme.get('fontScheme', {}).get('major')
    if typeface == '+mn-lt':
        return theme.get('fontScheme', {}).get('minor')

    return typeface


def resolve_paragraph_alignment(elem: etree._Element) -> str | None:
    """Резолвит выравнивание абзаца: l, ctr, r, just."""
    if elem is None:
        return None
    ppr = elem.find('.//a:pPr', NS)
    if ppr is not None:
        return ppr.get('algn')
    return None


def resolve_bold(elem: etree._Element) -> bool:
    """Резолвит жирность: b='1' или b='true'."""
    if elem is None:
        return False
    rpr = elem.find('.//a:rPr', NS)
    if rpr is None:
        rpr = elem.find('.//a:defRPr', NS)
    if rpr is not None:
        return rpr.get('b') in ('1', 'true')
    return False


def resolve_italic(elem: etree._Element) -> bool:
    """Резолвит курсив: i='1' или i='true'."""
    if elem is None:
        return False
    rpr = elem.find('.//a:rPr', NS)
    if rpr is None:
        rpr = elem.find('.//a:defRPr', NS)
    if rpr is not None:
        return rpr.get('i') in ('1', 'true')
    return False
