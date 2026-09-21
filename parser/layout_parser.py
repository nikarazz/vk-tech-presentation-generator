"""
Парсер slideLayouts/*.xml.

Извлекает:
  - тип layout (title, obj, blank, ...)
  - имя layout
  - плейсхолдеры с позициями и типами
  - ссылку на master

Каждый layout → паттерн для генерации.
"""
from lxml import etree
from zipfile import ZipFile

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}


def parse_layouts(pptx_path: str) -> list[dict]:
    """
    Парсит все layouts из .pptx.

    Возвращает список словарей:
      [
        {
          "layout_ref": "slideLayout1.xml",
          "name": "Title Slide",
          "type": "title",
          "placeholders": [
            {"type": "title", "idx": 0, "role": "slide_title", "position": {...}},
            {"type": "subTitle", "idx": 1, "role": "slide_subtitle", "position": {...}},
          ],
        },
        ...
      ]
    """
    layouts = []

    with ZipFile(pptx_path) as z:
        layout_files = sorted([
            n for n in z.namelist()
            if 'slideLayouts/slideLayout' in n and n.endswith('.xml')
        ])

        for layout_file in layout_files:
            with z.open(layout_file) as f:
                tree = etree.parse(f)
            layout = _parse_layout(tree, layout_file)
            layouts.append(layout)

    return layouts


def _parse_layout(tree: etree._ElementTree, layout_file: str) -> dict:
    """Парсит один layout."""
    root = tree.getroot()
    layout_name = layout_file.split('/')[-1]

    # Тип layout
    layout_type = root.get('type', 'obj')

    # Имя layout
    c_sld = root.find('.//p:cSld', NS)
    name = c_sld.get('name', '') if c_sld is not None else ''

    # Плейсхолдеры
    placeholders = _parse_placeholders(root)

    return {
        "layout_ref": layout_name,
        "name": name,
        "type": layout_type,
        "placeholders": placeholders,
    }


def _parse_placeholders(root: etree._Element) -> list[dict]:
    """Извлекает плейсхолдеры из layout."""
    sp_tree = root.find('.//p:cSld/p:spTree', NS)
    if sp_tree is None:
        return []

    placeholders = []

    for sp in sp_tree.findall('p:sp', NS):
        ph = sp.find('.//p:ph', NS)
        if ph is None:
            continue

        ph_type = ph.get('type', 'body')
        ph_idx = ph.get('idx', '0')

        role = _map_placeholder_to_role(ph_type, ph_idx)

        xfrm = sp.find('.//a:xfrm', NS)
        position = None
        if xfrm is not None:
            off = xfrm.find('a:off', NS)
            ext = xfrm.find('a:ext', NS)
            if off is not None and ext is not None:
                position = {
                    "x_emu": int(off.get('x')),
                    "y_emu": int(off.get('y')),
                    "w_emu": int(ext.get('cx')),
                    "h_emu": int(ext.get('cy')),
                }

        placeholders.append({
            "type": ph_type,
            "idx": int(ph_idx) if ph_idx.isdigit() else 0,
            "role": role,
            "position": position,
        })

    return placeholders


def _map_placeholder_to_role(ph_type: str, ph_idx: str) -> str:
    """
    Маппит тип плейсхолдера на семантическую роль.

    Роли:
      - slide_title
      - slide_subtitle
      - section_title
      - bullet
      - image
      - chart
      - table
      - caption
      - footer
      - slide_number
      - date
    """
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
