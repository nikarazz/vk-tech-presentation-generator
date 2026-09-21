from pptx import Presentation as PptxPresentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor

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


def export_pptx(pres: dict, ds: dict, template_path: str, output_path: str) -> None:
    prs = PptxPresentation(template_path)
    
    # Удалить все существующие слайды
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    for sld in slides:
        rId = sld.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        prs.part.drop_rel(rId)
        xml_slides.remove(sld)
    
    # Словарь: путь layout → индекс
    layout_by_ref = {}
    for idx, layout in enumerate(prs.slide_layouts):
        ref = str(layout.part.partname).split("/")[-1]
        layout_by_ref[ref] = idx
    
    for slide_data in pres["slides"]:
        layout_ref = slide_data.get("layout_ref", "")
        layout_idx = layout_by_ref.get(layout_ref, 6)
        slide = prs.slides.add_slide(prs.slide_layouts[layout_idx])
        
        # Собираем плейсхолдеры по idx
        available_phs = {}
        for ph in slide.placeholders:
            available_phs[ph.placeholder_format.idx] = ph
        
        # Заполняем элементы
        for el in slide_data["elements"]:
            if el["type"] == "text":
                ph_idx = el.get("placeholder_idx")
                
                if ph_idx is not None and ph_idx in available_phs:
                    ph = available_phs[ph_idx]
                    ph.text = el["text"]
                    _apply_style_to_frame(ph.text_frame, el.get("style", {}))
                else:
                    # Fallback: text box
                    bbox = el["bbox"]
                    txBox = slide.shapes.add_textbox(
                        Emu(bbox["x_emu"]), Emu(bbox["y_emu"]),
                        Emu(bbox["w_emu"]), Emu(bbox["h_emu"]),
                    )
                    tf = txBox.text_frame
                    tf.word_wrap = True
                    tf.text = el["text"]
                    _apply_style_to_frame(tf, el.get("style", {}))
            
            elif el["type"] == "chart":
                build_chart(slide, el["spec"], ds, el["bbox"])
            
            elif el["type"] == "table":
                build_table(slide, el["spec"], ds, el["bbox"])
    
    prs.save(output_path)
    print(f"[B] Saved to {output_path}")