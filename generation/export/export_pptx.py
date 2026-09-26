"""Экспорт Presentation → .pptx через копирование шаблонных слайдов.

Подход:
1. Открываем шаблон (.pptx с контентом).
2. Собираем шаблонные слайды по имени layout.
3. Для каждого слайда из pres — находим шаблонный.
4. Копируем XML шейпов из шаблонного слайда.
5. Удаляем сервисные/пустые placeholder'ы.
6. Заполняем контент. Цвет — по шаблону. Многострочный текст — через параграфы.
"""
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


def _pick_text_color(ds: dict) -> tuple:
    """Цвет текста по шаблону: тёмные → белый, светлые → тёмный.

    Нормализуем имя: пробелы/дефисы → подчёркивания.
    Это позволяет распознавать 'VK Tech шаблон.pptx', 'vk_tech.pptx' и т.п.
    """
    source = (ds.get("meta", {}).get("source_file") or "").lower()
    src = source.replace(" ", "_").replace("-", "_")

    # Тёмные шаблоны → белый
    if "tech" in src or "workspace" in src:
        return (0xFF, 0xFF, 0xFF)
    # Светлые шаблоны → тёмный
    if "education" in src:
        return (0x1A, 0x1A, 0x1A)

    # Fallback — белый (VK-стиль)
    return (0xFF, 0xFF, 0xFF)


def _set_text_multiline(text_frame, text: str):
    """Разбивает текст на параграфы по \\n.

    Решает проблему, когда text_frame.text = "a\\nb" PowerPoint
    рендерит как одну строку (текст «слипается»).
    """
    try:
        text_frame.clear()
    except Exception:
        pass

    lines = [ln for ln in text.split("\n") if ln.strip()]
    if not lines:
        return

    for j, line in enumerate(lines):
        if j == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()
        p.text = line


def _apply_style_to_frame(text_frame, style: dict, default_rgb=(0xFF, 0xFF, 0xFF)):
    """Применяет шрифт, размер, цвет, жирность."""
    font_name = style.get("font", "Arial")
    font_size = style.get("size_pt", 16)
    color_hex = style.get("color")
    weight = style.get("weight", 400)

    if color_hex:
        try:
            rgb = RGBColor.from_string(color_hex.lstrip("#"))
        except Exception:
            rgb = RGBColor(*default_rgb)
    else:
        rgb = RGBColor(*default_rgb)

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
    """Удаляет placeholder'ы, не заполненные нашим контентом."""
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
    """Экспортирует Presentation в .pptx."""
    prs = PptxPresentation(template_path)
    default_rgb = _pick_text_color(ds)

    template_by_layout = {}
    for slide in prs.slides:
        layout_name = slide.slide_layout.name
        if layout_name not in template_by_layout:
            template_by_layout[layout_name] = slide

    layout_names = {}
    for layout in prs.slide_layouts:
        ref = str(layout.part.partname).split("/")[-1]
        layout_names[ref] = layout.name

    xml_slides = prs.slides._sldIdLst
    for sld in list(xml_slides):
        rId = sld.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        prs.part.drop_rel(rId)
        xml_slides.remove(sld)

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
                    _set_text_multiline(title_shape.text_frame, text)
                    _apply_style_to_frame(title_shape.text_frame, style, default_rgb)

                elif role in ("bullet", "slide_subtitle", "body"):
                    if body_shape is not None:
                        _set_text_multiline(body_shape.text_frame, text)
                        _apply_style_to_frame(body_shape.text_frame, style, default_rgb)
                    else:
                        bbox = el.get("bbox")
                        if bbox:
                            txBox = new_slide.shapes.add_textbox(
                                Emu(int(bbox["x_emu"])), Emu(int(bbox["y_emu"])),
                                Emu(int(bbox["w_emu"])), Emu(int(bbox["h_emu"])),
                            )
                            tf = txBox.text_frame
                            tf.word_wrap = True
                            _set_text_multiline(tf, text)
                            _apply_style_to_frame(tf, style, default_rgb)

                else:
                    bbox = el.get("bbox")
                    if not bbox:
                        continue
                    txBox = new_slide.shapes.add_textbox(
                        Emu(int(bbox["x_emu"])), Emu(int(bbox["y_emu"])),
                        Emu(int(bbox["w_emu"])), Emu(int(bbox["h_emu"])),
                    )
                    tf = txBox.text_frame
                    tf.word_wrap = True
                    _set_text_multiline(tf, text)
                    _apply_style_to_frame(tf, style, default_rgb)

            elif el["type"] == "chart":
                build_chart(new_slide, el["spec"], ds, el["bbox"])

            elif el["type"] == "table":
                build_table(new_slide, el["spec"], ds, el["bbox"])

        _remove_service_shapes(new_slide)

    prs.save(output_path)
    print(f"[B] Saved to {output_path}")