"""Экспорт Presentation → .pptx через копирование шаблонных слайдов.

Подход:
1. Открываем шаблон (.pptx с контентом).
2. Собираем шаблонные слайды по имени layout.
3. Для каждого слайда из pres — находим шаблонный.
4. Копируем XML шейпов из шаблонного слайда.
5. Очищаем текст, заполняем своим.
6. Добавляем chart/table.
"""
from copy import deepcopy

from pptx import Presentation as PptxPresentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

from generation.chart_builder import build_chart
from generation.table_builder import build_table


def _apply_style_to_frame(text_frame, style: dict):
    """Применяет шрифт, размер, цвет, жирность."""
    font_name = style.get("font", "Arial")
    font_size = style.get("size_pt", 16)
    color_hex = style.get("color", "#1A1A1A").lstrip("#")
    weight = style.get("weight", 400)

    try:
        rgb = RGBColor.from_string(color_hex)
    except Exception:
        rgb = RGBColor(0x1A, 0x1A, 0x1A)

    for para in text_frame.paragraphs:
        for run in para.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)
            run.font.bold = weight >= 700
            run.font.color.rgb = rgb


def _classify_shape(shape) -> str:
    """Определяет роль шейпа: title, body, other."""
    name = shape.name.lower()
    top = shape.top or 0
    height = shape.height or 0
    width = shape.width or 0

    # По имени
    if "title" in name or "заголов" in name:
        return "title"
    if "body" in name or "text" in name or "content" in name or "текст" in name:
        return "body"

    # По позиции: верхняя треть — title
    if top < 1500000 and height < 2000000:
        return "title"

    # По размеру: большой — body
    if width > 3000000 and height > 1000000:
        return "body"

    return "other"


def _collect_text_shapes(slide) -> list:
    """Собирает шейпы с непустым текстом."""
    shapes = []
    for shape in slide.shapes:
        try:
            if shape.has_text_frame and shape.text_frame.text.strip():
                shapes.append(shape)
        except Exception:
            continue
    return shapes


def _copy_shapes(template_slide, new_slide):
    """Копирует XML шейпов из шаблонного слайда в новый."""
    template_spTree = template_slide.shapes._spTree
    new_spTree = new_slide.shapes._spTree

    # Удаляем всё лишнее с нового слайда
    for sp in list(new_spTree):
        tag = sp.tag.split('}')[-1]
        if tag in ('sp', 'pic', 'graphicFrame', 'grpSp', 'cxnSp'):
            new_spTree.remove(sp)

    # Копируем шейпы из шаблона
    for sp in list(template_spTree):
        tag = sp.tag.split('}')[-1]
        if tag in ('sp', 'pic', 'graphicFrame', 'grpSp', 'cxnSp'):
            new_spTree.append(deepcopy(sp))


def export_pptx(pres: dict, ds: dict, template_path: str, output_path: str) -> None:
    """Экспортирует Presentation в .pptx."""
    prs = PptxPresentation(template_path)

    # 1. Шаблонные слайды по имени layout
    template_by_layout = {}
    for slide in prs.slides:
        layout_name = slide.slide_layout.name
        if layout_name not in template_by_layout:
            template_by_layout[layout_name] = slide

    # 2. Карта: slideLayoutN.xml → имя layout
    layout_names = {}
    for layout in prs.slide_layouts:
        ref = str(layout.part.partname).split("/")[-1]
        layout_names[ref] = layout.name

    # 3. Удаляем все существующие слайды
    xml_slides = prs.slides._sldIdLst
    for sld in list(xml_slides):
        rId = sld.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        prs.part.drop_rel(rId)
        xml_slides.remove(sld)

    # 4. Создаём новые слайды
    for slide_data in pres["slides"]:
        layout_ref = slide_data.get("layout_ref", "")
        layout_name = layout_names.get(layout_ref, "")

        # Ищем шаблонный слайд
        template_slide = template_by_layout.get(layout_name)
        if template_slide is None:
            template_slide = list(template_by_layout.values())[0]

        # Создаём новый слайд
        new_slide = prs.slides.add_slide(template_slide.slide_layout)

        # Копируем шейпы из шаблона
        _copy_shapes(template_slide, new_slide)

        # Собираем текстовые шейпы
        text_shapes = _collect_text_shapes(new_slide)

        # Классифицируем
        title_shape = None
        body_shape = None
        for shape in text_shapes:
            role = _classify_shape(shape)
            if role == "title" and title_shape is None:
                title_shape = shape
            elif role == "body" and body_shape is None:
                body_shape = shape

        # Очищаем все тексты
        for shape in text_shapes:
            try:
                shape.text_frame.text = ""
            except Exception:
                pass

        # Заполняем контент
        for el in slide_data["elements"]:
            if el["type"] == "text":
                role = el.get("role")
                text = el.get("text", "")
                style = el.get("style", {})

                if not text:
                    continue

                if role in ("slide_title", "section_title") and title_shape is not None:
                    title_shape.text_frame.text = text
                    _apply_style_to_frame(title_shape.text_frame, style)

                elif role == "bullet" and body_shape is not None:
                    body_shape.text_frame.text = text
                    _apply_style_to_frame(body_shape.text_frame, style)

                else:
                    # Fallback: textbox
                    bbox = el["bbox"]
                    txBox = new_slide.shapes.add_textbox(
                        Emu(bbox["x_emu"]), Emu(bbox["y_emu"]),
                        Emu(bbox["w_emu"]), Emu(bbox["h_emu"]),
                    )
                    tf = txBox.text_frame
                    tf.word_wrap = True
                    tf.text = text
                    _apply_style_to_frame(tf, style)

            elif el["type"] == "chart":
                build_chart(new_slide, el["spec"], ds, el["bbox"])

            elif el["type"] == "table":
                build_table(new_slide, el["spec"], ds, el["bbox"])

    prs.save(output_path)
    print(f"[B] Saved to {output_path}")
