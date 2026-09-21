"""
Парсер slides/slideN.xml — конкретных слайдов презентации.

Извлекает:
  - layout_ref — на каком layout собран слайд
  - элементы: тексты, картинки, таблицы, графики
  - для каждого элемента: bbox, стиль, содержимое

Используется для:
  - режима Improve (доработка существующей презы)
  - сбора статистики (какие паттерны чаще используются)
  - извлечения примеров контента
"""
from lxml import etree
from zipfile import ZipFile
from parser.inheritance import (
    resolve_color,
    resolve_font_size,
    resolve_font_family,
    resolve_bold,
    resolve_italic,
)

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}


def parse_slides(pptx_path: str, theme: dict) -> list[dict]:
    """
    Парсит все слайды из .pptx.

    Возвращает список:
      [
        {
          "slide_id": 1,
          "layout_ref": "slideLayout1.xml",
          "elements": [
            {
              "element_id": "sp_2",
              "type": "text",
              "role": "slide_title",
              "bbox": {...},
              "text": "...",
              "style": {...},
            },
            ...
          ],
        },
        ...
      ]
    """
    slides = []

    with ZipFile(pptx_path) as z:
        slide_files = sorted(
            [n for n in z.namelist() if 'slides/slide' in n and n.endswith('.xml')],
            key=_slide_sort_key,
        )

        for idx, slide_file in enumerate(slide_files, start=1):
            with z.open(slide_file) as f:
                tree = etree.parse(f)
            slide = _parse_slide(tree, idx, theme)
            slides.append(slide)

    return slides


def _slide_sort_key(path: str) -> int:
    """Сортирует slideN.xml по номеру."""
    name = path.split('/')[-1].replace('slide', '').replace('.xml', '')
    return int(name) if name.isdigit() else 0


def _parse_slide(tree: etree._ElementTree, slide_id: int, theme: dict) -> dict:
    """Парсит один слайд."""
    root = tree.getroot()

    # Ссылка на layout
    layout_ref = _find_layout_ref(root)

    # Элементы
    elements = _parse_elements(root, theme)

    return {
        "slide_id": slide_id,
        "layout_ref": layout_ref,
        "elements": elements,
    }


def _find_layout_ref(root: etree._Element) -> str:
    """
    Находит ссылку на layout из слайда.

    В slideN.xml это p:sld/p:cSld/... и r:id в p:sldLayout.
    Но проще: смотрим связь через rels-файл.
    Для упрощения — возвращаем 'unknown'.
    """
    # TODO: использовать ppt/slides/_rels/slideN.xml.rels для точного layout_ref
    return "unknown"


def _parse_elements(root: etree._Element, theme: dict) -> list[dict]:
    """Извлекает элементы из слайда."""
    sp_tree = root.find('.//p:cSld/p:spTree', NS)
    if sp_tree is None:
        return []

    elements = []

    # Текстовые шейпы
    for sp in sp_tree.findall('p:sp', NS):
        el = _parse_text_shape(sp, theme)
        if el:
            elements.append(el)

    # Картинки
    for pic in sp_tree.findall('p:pic', NS):
        el = _parse_picture(pic)
        if el:
            elements.append(el)

    # Таблицы
    for graphic_frame in sp_tree.findall('p:graphicFrame', NS):
        el = _parse_graphic_frame(graphic_frame)
        if el:
            elements.append(el)

    return elements


def _parse_text_shape(sp: etree._Element, theme: dict) -> dict | None:
    """Парсит текстовый шейп."""
    nv = sp.find('.//p:cNvPr', NS)
    if nv is None:
        return None
    element_id = f"sp_{nv.get('id')}"

    # Тип и роль плейсхолдера
    ph = sp.find('.//p:ph', NS)
    role = 'body'
    if ph is not None:
        role = _map_placeholder_to_role(ph.get('type', 'body'))

    # Позиция
    xfrm = sp.find('.//a:xfrm', NS)
    bbox = {"x_emu": 0, "y_emu": 0, "w_emu": 0, "h_emu": 0}
    if xfrm is not None:
        off = xfrm.find('a:off', NS)
        ext = xfrm.find('a:ext', NS)
        if off is not None and ext is not None:
            bbox = {
                "x_emu": int(off.get('x')),
                "y_emu": int(off.get('y')),
                "w_emu": int(ext.get('cx')),
                "h_emu": int(ext.get('cy')),
            }

    # Текст
    text = _extract_text(sp)

    # Стиль — берём из первого run
    style = _extract_style(sp, theme)

    return {
        "element_id": element_id,
        "type": "text",
        "role": role,
        "bbox": bbox,
        "text": text,
        "style": style,
    }


def _extract_text(sp: etree._Element) -> str:
    """Извлекает весь текст из шейпа."""
    texts = []
    for t in sp.findall('.//a:t', NS):
        if t.text:
            texts.append(t.text)
    return '\n'.join(texts)


def _extract_style(sp: etree._Element, theme: dict) -> dict:
    """Извлекает стиль из первого run в шейпе."""
    color, alpha = resolve_color(sp, theme)
    size = resolve_font_size(sp)
    font = resolve_font_family(sp, theme)
    bold = resolve_bold(sp)
    italic = resolve_italic(sp)

    return {
        "font": font,
        "size_pt": size,
        "color": color,
        "alpha": alpha,
        "bold": bold,
        "italic": italic,
    }


def _parse_picture(pic: etree._Element) -> dict | None:
    """Парсит картинку."""
    nv = pic.find('.//p:cNvPr', NS)
    if nv is None:
        return None
    element_id = f"pic_{nv.get('id')}"

    xfrm = pic.find('.//a:xfrm', NS)
    bbox = {"x_emu": 0, "y_emu": 0, "w_emu": 0, "h_emu": 0}
    if xfrm is not None:
        off = xfrm.find('a:off', NS)
        ext = xfrm.find('a:ext', NS)
        if off is not None and ext is not None:
            bbox = {
                "x_emu": int(off.get('x')),
                "y_emu": int(off.get('y')),
                "w_emu": int(ext.get('cx')),
                "h_emu": int(ext.get('cy')),
            }

    return {
        "element_id": element_id,
        "type": "image",
        "role": "image",
        "bbox": bbox,
        "text": "",
        "style": {},
    }


def _parse_graphic_frame(frame: etree._Element) -> dict | None:
    """Парсит graphicFrame — таблицу или график."""
    nv = frame.find('.//p:cNvPr', NS)
    if nv is None:
        return None
    element_id = f"gf_{nv.get('id')}"

    # Определяем тип: таблица или график
    table = frame.find('.//a:tbl', NS)
    chart = frame.find('.//c:chart', {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'})

    el_type = "table" if table is not None else "chart" if chart is not None else "unknown"

    xfrm = frame.find('.//a:xfrm', NS)
    bbox = {"x_emu": 0, "y_emu": 0, "w_emu": 0, "h_emu": 0}
    if xfrm is not None:
        off = xfrm.find('a:off', NS)
        ext = xfrm.find('a:ext', NS)
        if off is not None and ext is not None:
            bbox = {
                "x_emu": int(off.get('x')),
                "y_emu": int(off.get('y')),
                "w_emu": int(ext.get('cx')),
                "h_emu": int(ext.get('cy')),
            }

    return {
        "element_id": element_id,
        "type": el_type,
        "role": el_type,
        "bbox": bbox,
        "text": "",
        "style": {},
    }


def _map_placeholder_to_role(ph_type: str) -> str:
    """Маппит тип плейсхолдера на роль."""
    mapping = {
        'title': 'slide_title',
        'ctrTitle': 'section_title',
        'subTitle': 'slide_subtitle',
        'body': 'bullet',
        'pic': 'image',
        'chart': 'chart',
        'tbl': 'table',
        'ftr': 'footer',
        'sldNum': 'slide_number',
        'dt': 'date',
    }
    return mapping.get(ph_type, 'body')
