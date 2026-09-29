"""
Парсер slideLayouts/*.xml.
"""
from lxml import etree
from zipfile import ZipFile

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}


def parse_layouts(pptx_path: str) -> list[dict]:
    """Парсит все layouts из .pptx."""
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
    layout_type = root.get('type', 'obj')

    c_sld = root.find('.//p:cSld', NS)
    name = c_sld.get('name', '') if c_sld is not None else ''

    placeholders = _parse_placeholders(root)

    return {
        "layout_ref": layout_name,
        "name": name,
        "type": layout_type,
        "placeholders": placeholders,
    }


def _parse_placeholders(root: etree._Element) -> list[dict]:
    """Извлекает плейсхолдеры И обычные shapes с текстом.

    Плейсхолдеры берём ВСЕ (даже с пустым текстом — в них будем класть контент).
    Обычные shapes фильтруем от мусора.
    """
    sp_tree = root.find('.//p:cSld/p:spTree', NS)
    if sp_tree is None:
        return []

    placeholders = []

    for sp in sp_tree.findall('p:sp', NS):
        nv = sp.find('.//p:cNvPr', NS)
        ph = sp.find('.//p:ph', NS)
        txBody = sp.find('.//p:txBody', NS)

        name = nv.get('name', '') if nv is not None else ''

        if ph is not None:
            # Placeholder — берём ВСЕГДА
            ph_type = ph.get('type', 'body')
            ph_idx = ph.get('idx', '0')
            role = _map_placeholder_to_role(ph_type, ph_idx)
            is_placeholder = True
            idx = int(ph_idx) if ph_idx.isdigit() else 0
        else:
            # Обычный shape — только если есть текст и он не мусор
            if txBody is None:
                continue

            text = _extract_shape_text(txBody)
            if _is_garbage_text(text):
                continue

            role = _guess_role_by_shape(sp, name)
            is_placeholder = False
            idx = -1
            ph_type = 'shape'

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
            "idx": idx,
            "role": role,
            "name": name,
            "position": position,
            "is_placeholder": is_placeholder,
        })

    return placeholders


def _extract_shape_text(txBody: etree._Element) -> str:
    """Извлекает текст из txBody."""
    texts = []
    for t in txBody.findall('.//a:t', NS):
        if t.text:
            texts.append(t.text)
    return ' '.join(texts)


def _is_garbage_text(text: str) -> bool:
    """Мусор: пустой, короткий, только цифры/слэши, без букв."""
    if not text or len(text) < 3:
        return True

    cleaned = text.replace(' ', '').replace('/', '').replace('\\', '')

    if not cleaned:
        return True

    if cleaned.isdigit():
        return True

    has_letter = any(c.isalpha() for c in cleaned)
    if not has_letter:
        return True

    return False


def _map_placeholder_to_role(ph_type: str, ph_idx: str) -> str:
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


def _guess_role_by_shape(sp: etree._Element, name: str) -> str:
    """Угадывает роль обычного shape по имени и размеру."""
    name_lower = name.lower()

    if 'title' in name_lower or 'заголовок' in name_lower:
        return 'slide_title'
    if 'subtitle' in name_lower or 'подзаголовок' in name_lower:
        return 'slide_subtitle'
    if 'bullet' in name_lower or 'текст' in name_lower or 'body' in name_lower:
        return 'bullet'

    xfrm = sp.find('.//a:xfrm', NS)
    if xfrm is not None:
        ext = xfrm.find('a:ext', NS)
        if ext is not None:
            w = int(ext.get('cx'))
            h = int(ext.get('cy'))
            if w * h > 3_000_000_000:
                return 'bullet'

    return 'bullet'
