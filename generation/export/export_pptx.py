"""Экспорт Presentation → .pptx через копирование шаблонных слайдов."""
from copy import deepcopy

from pptx import Presentation as PptxPresentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

from generation.chart_builder import build_chart
from generation.table_builder import build_table


SERVICE_TEXTS = {
    "текст слайда", "заголовок", "заголовок слайда",
    "text slide", "click to edit", "click to add text",
    "введите текст", "текст", "подзаголовок",
}


def _apply_style_to_frame(text_frame, style: dict):
    """Применяет шрифт, размер, цвет (белый по умолчанию), жирность."""
    font_name = style.get("font", "Arial")
    font_size = style.get("size_pt", 16)
    color_hex = style.get("color", "#FFFFFF").lstrip("#")   # ← БЕЛЫЙ по умолчанию
    weight = style.get("weight", 400)

    try:
        rgb = RGBColor.from_string(color_hex)
    except Exception:
        rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for para in text_frame.paragraphs:
        for run in para.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)
            run.font.bold = weight >= 700
            run.font.color.rgb = rgb


def _classify_shape(shape) -> str:
    name = shape.name.lower()
    top = shape.top or 0
    height = shape.height or 0
    width = shape.width or 0

    if "title" in name or "заголов" in name:
        return "title"
    if "body" in name or "text" in name or "content" in name or "текст" in name:
        return "body"
    if top < 1500000 and height < 2000000:
        return "title"
    if width > 3000000 and height > 1000000:
        return "body"
    return "other"


def _collect_text_shapes(slide) -> list:
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

    for sp in list(new_spTree):
        tag = sp.tag.split('}')[-1]
        if tag in ('sp', 'pic', 'graphicFrame', 'grpSp', 'cxnSp'):
            new_spTree.remove(sp)

    for sp in list(template_spTree):
        tag = sp.tag.split('}')[-1]
        if tag in ('sp', 'pic', 'graphicFrame', 'grpSp', 'cxnSp'):
            new_spTree.append(deepcopy(sp))


def _remove_service_shapes(slide):
    """Удаляет placeholder'ы, не заполненные нашим контентом.

    Убирает:
      - placeholder'ы с сервисным текстом ("Текст слайда", "Заголовок");
      - пустые placeholder'ы (PowerPoint рисует в них prompt text).
    """
    for shape in list(slide.shapes):
        try:
            if not shape.is_placeholder:
                continue
            txt = ""
            if shape.has_text_frame:
                txt = shape.text_frame.text.strip()
            if txt.lower() in SERVICE_TEXTS or not txt:
                shape._element.getparent().remove(shape._element)
        except Exception:
            continue


def export_pptx(pres: dict, ds: dict, template_path: str, output_path: str) -> None:
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

    # 3. Удаляем существующие слайды
    xml_slides = prs.slides._sldIdLst
    for sld in list(xml_slides):
        rId = sld.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        prs.part.drop_rel(rId)
        xml_slides.remove(sld)

    # 4. Создаём новые слайды
    for slide_data in pres["slides"]:
        layout_ref = slide_data.get("layout_ref", "")
        layout_name = layout_names.get(layout_ref, "")

        template_slide = template_by_layout.get(layout_name)
        if template_slide is None:
            template_slide = list(template_by_layout.values())[0]

        new_slide = prs.slides.add_slide(template_slide.slide_layout)
        _copy_shapes(template_slide, new_slide)

        text_shapes = _collect_text_shapes(new_slide)

        title_shape = None
        body_shape = None
        for shape in text_shapes:
            role = _classify_shape(shape)
            if role == "title" and title_shape is None:
                title_shape = shape
            elif role == "body" and body_shape is None:
                body_shape = shape

        for shape in text_shapes:
            try:
                shape.text_frame.text = ""
            except Exception:
                pass

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

        # ← Убираем «Текст слайда» и пустые placeholder'ы
        _remove_service_shapes(new_slide)

    prs.save(output_path)
    print(f"[B] Saved to {output_path}")