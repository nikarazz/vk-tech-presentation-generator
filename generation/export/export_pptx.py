from pptx import Presentation as PptxPresentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

from generation.chart_builder import build_chart
from generation.table_builder import build_table


def _apply_style_to_frame(text_frame, style: dict):
    """Применяет стиль (шрифт, размер, цвет, жирность) ко всем run'ам."""
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


def _add_bullet_markers(text_frame):
    """Добавляет маркер '•' только если его нет."""
    for para in text_frame.paragraphs:
        pPr = para._p.get_or_add_pPr()

        if pPr.find(qn('a:buChar')) is not None:
            continue
        if pPr.find(qn('a:buAutoNum')) is not None:
            continue

        buNone = pPr.find(qn('a:buNone'))
        if buNone is not None:
            pPr.remove(buNone)

        buChar = pPr.makeelement(qn('a:buChar'), {'char': '•'})
        pPr.append(buChar)


def _resolve_layout_ref(slide_data: dict, prs, layout_by_ref: dict) -> str:
    """Определяет layout_ref с fallback по pattern_id."""
    layout_ref = slide_data.get("layout_ref", "")
    if layout_ref and layout_ref in layout_by_ref:
        return layout_ref

    pattern_id = slide_data.get("pattern_id", "").lower()

    # Ищем layout, в имени которого есть pattern_id
    for ref, idx in layout_by_ref.items():
        layout = prs.slide_layouts[idx]
        if pattern_id and pattern_id in layout.name.lower():
            return ref

    # Fallback: ищем по ключевым словам
    keyword_map = {
        "title": ["титул", "title"],
        "content": ["содержание", "content", "пункт"],
        "team": ["команда", "team"],
        "chart": ["статистик", "chart"],
        "demo": ["демо", "demo"],
        "closing": ["спасибо", "финал", "thank"],
    }
    for key, keywords in keyword_map.items():
        if key in pattern_id:
            for ref, idx in layout_by_ref.items():
                layout = prs.slide_layouts[idx]
                for kw in keywords:
                    if kw in layout.name.lower():
                        return ref

    # Совсем fallback: первый layout (title)
    return list(layout_by_ref.keys())[0] if layout_by_ref else ""


def export_pptx(pres: dict, ds: dict, template_path: str, output_path: str) -> None:
    prs = PptxPresentation(template_path)

    # Удалить все существующие слайды
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    for sld in slides:
        rId = sld.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        prs.part.drop_rel(rId)
        xml_slides.remove(sld)

    # Словарь: имя layout → индекс
    layout_by_ref = {}
    for idx, layout in enumerate(prs.slide_layouts):
        ref = str(layout.part.partname).split("/")[-1]
        layout_by_ref[ref] = idx

    for slide_data in pres["slides"]:
        # Разрешаем layout_ref с fallback
        layout_ref = _resolve_layout_ref(slide_data, prs, layout_by_ref)
        layout_idx = layout_by_ref.get(layout_ref, 0)
        slide = prs.slides.add_slide(prs.slide_layouts[layout_idx])

        available_phs = {}
        for ph in slide.placeholders:
            available_phs[ph.placeholder_format.idx] = ph

        filled_idx = set()
        for el in slide_data["elements"]:
            if el["type"] == "text":
                ph_idx = el.get("placeholder_idx")
                is_bullet = el.get("role") == "bullet"

                if ph_idx is not None and ph_idx in available_phs:
                    ph = available_phs[ph_idx]
                    ph.text = el["text"]
                    _apply_style_to_frame(ph.text_frame, el.get("style", {}))
                    if is_bullet:
                        _add_bullet_markers(ph.text_frame)
                    filled_idx.add(ph_idx)
                else:
                    bbox = el["bbox"]
                    txBox = slide.shapes.add_textbox(
                        Emu(bbox["x_emu"]), Emu(bbox["y_emu"]),
                        Emu(bbox["w_emu"]), Emu(bbox["h_emu"]),
                    )
                    tf = txBox.text_frame
                    tf.word_wrap = True
                    tf.text = el["text"]
                    _apply_style_to_frame(tf, el.get("style", {}))
                    if is_bullet:
                        _add_bullet_markers(tf)

            elif el["type"] == "chart":
                build_chart(slide, el["spec"], ds, el["bbox"])

            elif el["type"] == "table":
                build_table(slide, el["spec"], ds, el["bbox"])

        # Очищаем незаполненные плейсхолдеры
        for ph in slide.placeholders:
            if ph.placeholder_format.idx not in filled_idx:
                try:
                    ph.text = ""
                except Exception:
                    pass

    prs.save(output_path)
    print(f"[B] Saved to {output_path}")
