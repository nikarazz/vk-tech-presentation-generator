"""
Резолвер наследования между уровнями.

Цепочка: slide → layout → master → theme.

Для каждого слайда строим цепочку XML-элементов:
  [slide_root, layout_root, master_root]

И передаём её в resolve_* функции.
"""
from lxml import etree
from zipfile import ZipFile

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def build_inheritance_chain(pptx_path: str, slide_id: int) -> list[etree._Element]:
    """
    Строит цепочку наследования для слайда.

    Возвращает [slide_root, layout_root, master_root].
    Порядок важен: от частного к общему.
    """
    with ZipFile(pptx_path) as z:
        # 1. Slide
        slide_path = f"ppt/slides/slide{slide_id}.xml"
        if slide_path not in z.namelist():
            return []
        slide_root = _read_xml(z, slide_path)

        # 2. Layout (через _rels)
        layout_path = _resolve_relationship(z, slide_path, "slideLayout")
        if not layout_path:
            return [slide_root]
        layout_root = _read_xml(z, layout_path)

        # 3. Master (через _rels layout'а)
        master_path = _resolve_relationship(z, layout_path, "slideMaster")
        if not master_path:
            return [slide_root, layout_root]
        master_root = _read_xml(z, master_path)

        return [slide_root, layout_root, master_root]


def _read_xml(z: ZipFile, path: str) -> etree._Element:
    """Читает XML из ZIP."""
    with z.open(path) as f:
        return etree.parse(f).getroot()


def _resolve_relationship(z: ZipFile, source_path: str, rel_type_suffix: str) -> str | None:
    """
    Находит Target отношения по типу.

    source_path: 'ppt/slides/slide1.xml'
    rel_type_suffix: 'slideLayout' или 'slideMaster'
    Возвращает: 'ppt/slideLayouts/slideLayout1.xml' или None.
    """
    # Формируем путь к .rels
    parts = source_path.split('/')
    rels_path = f"{'/'.join(parts[:-1])}/_rels/{parts[-1]}.rels"

    if rels_path not in z.namelist():
        return None

    with z.open(rels_path) as f:
        tree = etree.parse(f)

    for rel in tree.findall('.//rel:Relationship', NS):
        rel_type = rel.get('Type', '')
        if rel_type.endswith(f'/{rel_type_suffix}'):
            target = rel.get('Target')
            # Target относительный: '../slideLayouts/slideLayout1.xml'
            # Нормализуем
            base = '/'.join(parts[:-1])
            resolved = _normalize_path(base, target)
            if resolved in z.namelist():
                return resolved

    return None


def _normalize_path(base: str, target: str) -> str:
    """Нормализует относительный путь."""
    if target.startswith('/'):
        return target.lstrip('/')

    # base = 'ppt/slides', target = '../slideLayouts/slideLayout1.xml'
    base_parts = base.split('/')
    target_parts = target.split('/')

    for part in target_parts:
        if part == '..':
            base_parts.pop()
        elif part == '.':
            continue
        else:
            base_parts.append(part)

    return '/'.join(base_parts)


def resolve_color_from_chain(chain: list[etree._Element], theme: dict) -> tuple[str | None, float]:
    """
    Резолвит цвет по цепочке наследования.

    Идёт от slide → layout → master. Первое найденное значение — финальное.
    Если нигде нет — берёт из theme по роли.
    """
    from parser.inheritance import resolve_color

    for elem in chain:
        color, alpha = resolve_color(elem, theme)
        if color is not None:
            return color, alpha

    return None, 1.0


def resolve_font_size_from_chain(chain: list[etree._Element]) -> float | None:
    """Резолвит кегль по цепочке."""
    from parser.inheritance import resolve_font_size

    for elem in chain:
        size = resolve_font_size(elem)
        if size is not None:
            return size

    return None


def resolve_font_family_from_chain(chain: list[etree._Element], theme: dict) -> str | None:
    """Резолвит шрифт по цепочке."""
    from parser.inheritance import resolve_font_family

    for elem in chain:
        font = resolve_font_family(elem, theme)
        if font is not None:
            return font

    return None