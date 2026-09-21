"""
Парсер slides/slideN.xml — конкретных слайдов презентации.

Использует резолвер наследования для получения финальных стилей.
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
from parser.resolver import (
    build_inheritance_chain,
    resolve_color_from_chain,
    resolve_font_size_from_chain,
    resolve_font_family_from_chain,
)

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def parse_slides(pptx_path: str, theme: dict) -> list[dict]:
    """Парсит все слайды из .pptx."""
    slides = []

    with ZipFile(pptx_path) as z:
        slide_files = sorted(
            [n for n in z.namelist() if 'slides/slide' in n and n.endswith('.xml')],
            key=_slide_sort_key,
        )

    for idx, slide_file in enumerate(slide_files, start=1):
        with ZipFile(pptx_path) as z:
            slide_root = _read_xml(z, slide_file)

        layout_ref = _find_layout_ref(pptx_path, idx)
        chain = build_inheritance_chain(pptx_path, idx)

        elements = _parse_elements(slide_root, chain, theme)

        slides.append({
            "slide_id": idx,
            "layout_ref": layout_ref,
            "elements": elements,
        })

    return slides


def _read_xml(z: ZipFile, path: str) -> etree._Element:
    with z.open(path) as f:
        return etree.parse(f).getroot()


def _slide_sort_key(path: str) -> int:
    name = path.split('/')[-1].replace('slide', '').replace('.xml', '')
    return int(name) if name.isdigit() else 0


def _find_layout_ref(pptx_path: str, slide_id: int) -> str:
    """Находит layout_ref для слайда через _rels."""
    with ZipFile(pptx_path) as z:
        rels_path = f"ppt/slides/_rels/slide{slide_id}.xml.rels"
        if rels_path not in z.namelist():
            return "unknown"

        with z.open(rels_path) as f:
            tree = etree.parse(f)

        for rel in tree.findall('.//rel:Relationship', NS):
            rel_type = rel.get('Type', '')
            if rel_type.endswith('/slideLayout'):
                target = rel.get('Target', '')
                return target.split('/')[-1]

    return "unknown"


def _parse_elements(root: etree._Element, chain: list, theme: dict) -> list[dict]:
    """Извлекает элементы из слайда."""
    sp_tree = root.find('.//p:cSld/p:spTree', NS)
    if sp_tree is None:
        return []

    elements = []

    for sp in sp_tree.findall('p:sp', NS):
        el = _parse_text_shape(sp, chain, theme)
        if el:
            elements.append(el)

    for pic in sp_tree.findall('p:pic', NS):
        el = _parse_picture(pic)
        if el:
            elements.append(el)

    for gf in sp_tree.findall('p:graphicFrame', NS):
        el = _parse_graphic_frame(gf)
        if el:
            elements.append(el)

    return elements


def _parse_text_shape(sp: etree._Element, chain: list, theme: dict) -> dict | None:
    nv = sp.find('.//p:cNvPr', NS)
    if nv is None:
        return None
    element_id = f"sp_{nv.get('id')}"

    ph = sp.find('.//p:ph', NS)
    role = 'body'
    if ph is not None:
        role = _map_placeholder_to_role(ph.get('type', 'body'))

    bbox = _extract_bbox(sp)
    text = _extract_text(sp)
    style = _extract_style(sp, chain, theme)

    return {
        "element_id": element_id,
        "type": "text",
        "role": role,
        "bbox": bbox,
        "text": text,
        "style": style,
    }


def _extract_bbox(sp: etree._Element) -> dict:
    xfrm = sp.find('.//a:xfrm', NS)
    if xfrm is None:
        return {"x_emu": 0, "y_emu": 0, "w_emu": 0, "h_emu": 0}

    off = xfrm.find('a:off', NS)
    ext = xfrm.find('a:ext', NS)
    if off is None or ext is None:
        return {"x_emu": 0, "y_emu": 0, "w_emu": 0, "h_emu": 0}

    return {
        "x_emu": int(off.get('x')),
        "y_emu": int(off.get('y')),
        "w_emu": int(ext.get('cx')),
        "h_emu": int(ext.get('cy')),
    }


def _extract_text(sp: etree._Element) -> str:
    texts = []
    for t in sp.findall('.//a:t', NS):
        if t.text:
            texts.append(t.text)
    return '\n'.join(texts)


def _extract_style(sp: etree._Element, chain: list, theme: dict) -> dict:
    """Извлекает стиль с использованием цепочки наследования."""
    color, alpha = resolve_color(sp, theme)
    size = resolve_font_size(sp)
    font = resolve_font_family(sp, theme)

    if color is None:
        color, alpha = resolve_color_from_chain(chain, theme)
    if size is None:
        size = resolve_font_size_from_chain(chain)
    if font is None:
        font = resolve_font_family_from_chain(chain, theme)

    return {
        "font": font,
        "size_pt": size,
        "color": color,
        "alpha": alpha,
        "bold": resolve_bold(sp),
        "italic": resolve_italic(sp),
    }


def _parse_picture(pic: etree._Element) -> dict | None:
    nv = pic.find('.//p:cNvPr', NS)
    if nv is None:
        return None

    return {
        "element_id": f"pic_{nv.get('id')}",
        "type": "image",
        "role": "image",
        "bbox": _extract_bbox(pic),
        "text": "",
        "style": {},
    }


def _parse_graphic_frame(gf: etree._Element) -> dict | None:
    nv = gf.find('.//p:cNvPr', NS)
    if nv is None:
        return None

    table = gf.find('.//a:tbl', NS)
    chart = gf.find('.//c:chart', {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'})

    el_type = "table" if table is not None else "chart" if chart is not None else "unknown"

    return {
        "element_id": f"gf_{nv.get('id')}",
        "type": el_type,
        "role": el_type,
        "bbox": _extract_bbox(gf),
        "text": "",
        "style": {},
    }


def _map_placeholder_to_role(ph_type: str) -> str:
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
