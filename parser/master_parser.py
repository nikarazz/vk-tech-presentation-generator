"""
Парсер slideMaster1.xml.

Извлекает:
  - фон (bg)
  - логотип (если есть)
  - стили текста по умолчанию (titleStyle, bodyStyle)
  - позиции плейсхолдеров footer/date/slide number
"""
from lxml import etree
from zipfile import ZipFile
from parser.inheritance import resolve_color, resolve_font_size, resolve_font_family

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
}

EMU_PER_PT = 12700


def parse_master(pptx_path: str, theme: dict) -> dict:
    """
    Парсит slideMaster1.xml.

    Возвращает:
      {
        "background": {"type": "solid", "color": "#FFFFFF"} | None,
        "logo": {"path": "...", "position": {...}} | None,
        "title_style": {...},
        "body_style": {...},
        "footer_position": {...} | None,
        "slide_number_position": {...} | None,
      }
    """
    with ZipFile(pptx_path) as z:
        master_files = [n for n in z.namelist() if 'slideMaster' in n and n.endswith('.xml')]
        if not master_files:
            return _empty_master()
        with z.open(master_files[0]) as f:
            tree = etree.parse(f)

    root = tree.getroot()

    return {
        "background": _parse_background(root, theme),
        "logo": _parse_logo(root),
        "title_style": _parse_text_style(root, 'titleStyle', theme),
        "body_style": _parse_text_style(root, 'bodyStyle', theme),
        "footer_position": _parse_placeholder_position(root, 'ftr'),
        "slide_number_position": _parse_placeholder_position(root, 'sldNum'),
    }


def _empty_master() -> dict:
    return {
        "background": None,
        "logo": None,
        "title_style": {},
        "body_style": {},
        "footer_position": None,
        "slide_number_position": None,
    }


def _parse_background(root: etree._Element, theme: dict) -> dict | None:
    """Извлекает фон слайда из master."""
    bg = root.find('.//p:cSld/p:bg', NS)
    if bg is None:
        return None

    solid = bg.find('.//a:solidFill', NS)
    if solid is not None:
        color, alpha = resolve_color(solid, theme)
        if color:
            return {"type": "solid", "color": color, "alpha": alpha}

    return None


def _parse_logo(root: etree._Element) -> dict | None:
    """
    Ищет логотип на master.

    Логотип — это либо картинка (p:pic), либо текстовый шейп с именем "Logo".
    Возвращает позицию и путь к картинке (если есть).
    """
    # Ищем шейпы на master
    sp_tree = root.find('.//p:cSld/p:spTree', NS)
    if sp_tree is None:
        return None

    for sp in sp_tree.findall('p:sp', NS):
        nv = sp.find('.//p:cNvPr', NS)
        if nv is not None and 'logo' in nv.get('name', '').lower():
            xfrm = sp.find('.//a:xfrm', NS)
            if xfrm is not None:
                off = xfrm.find('a:off', NS)
                ext = xfrm.find('a:ext', NS)
                if off is not None and ext is not None:
                    return {
                        "type": "text",
                        "position": {
                            "x_emu": int(off.get('x')),
                            "y_emu": int(off.get('y')),
                            "w_emu": int(ext.get('cx')),
                            "h_emu": int(ext.get('cy')),
                        },
                    }

    for pic in sp_tree.findall('p:pic', NS):
        nv = pic.find('.//p:cNvPr', NS)
        if nv is not None and 'logo' in nv.get('name', '').lower():
            xfrm = pic.find('.//a:xfrm', NS)
            if xfrm is not None:
                off = xfrm.find('a:off', NS)
                ext = xfrm.find('a:ext', NS)
                if off is not None and ext is not None:
                    return {
                        "type": "image",
                        "position": {
                            "x_emu": int(off.get('x')),
                            "y_emu": int(off.get('y')),
                            "w_emu": int(ext.get('cx')),
                            "h_emu": int(ext.get('cy')),
                        },
                    }

    return None


def _parse_text_style(root: etree._Element, style_name: str, theme: dict) -> dict:
    """
    Извлекает стиль текста (titleStyle / bodyStyle) из master.

    Возвращает:
      {
        "levels": {
          1: {"size_pt": 32, "font": "...", "color": "...", "bold": True},
          2: {...},
          ...
        }
      }
    """
    style = root.find(f'.//p:txStyles/p:{style_name}', NS)
    if style is None:
        return {"levels": {}}

    levels = {}
    for lvl in range(1, 10):
        lvl_pr = style.find(f'a:lvl{lvl}pPr', NS)
        if lvl_pr is None:
            continue

        def_rpr = lvl_pr.find('a:defRPr', NS)
        if def_rpr is None:
            continue

        size = resolve_font_size(lvl_pr)
        font = resolve_font_family(lvl_pr, theme)
        color, _ = resolve_color(def_rpr, theme)
        bold = def_rpr.get('b') in ('1', 'true')

        levels[lvl] = {
            "size_pt": size,
            "font": font,
            "color": color,
            "bold": bold,
        }

    return {"levels": levels}


def _parse_placeholder_position(root: etree._Element, ph_type: str) -> dict | None:
    """
    Ищет позицию плейсхолдера по типу (ftr, sldNum, dt).

    Возвращает {x_emu, y_emu, w_emu, h_emu} или None.
    """
    sp_tree = root.find('.//p:cSld/p:spTree', NS)
    if sp_tree is None:
        return None

    for sp in sp_tree.findall('p:sp', NS):
        ph = sp.find('.//p:ph', NS)
        if ph is not None and ph.get('type') == ph_type:
            xfrm = sp.find('.//a:xfrm', NS)
            if xfrm is not None:
                off = xfrm.find('a:off', NS)
                ext = xfrm.find('a:ext', NS)
                if off is not None and ext is not None:
                    return {
                        "x_emu": int(off.get('x')),
                        "y_emu": int(off.get('y')),
                        "w_emu": int(ext.get('cx')),
                        "h_emu": int(ext.get('cy')),
                    }

    return None
