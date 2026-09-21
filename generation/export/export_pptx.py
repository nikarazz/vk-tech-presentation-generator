from pptx import Presentation as PptxPresentation
from pptx.util import Emu, Pt

from generation.chart_builder import build_chart
from generation.table_builder import build_table


def export_pptx(pres: dict, ds: dict, template_path: str, output_path: str) -> None:
    prs = PptxPresentation(template_path)
    
    # Удалить все существующие слайды из пакета
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
        
        # Удалить плейсхолдеры, чтобы не было «Заголовок слайда»
        for shape in list(slide.shapes):
            if shape.is_placeholder:
                sp = shape._element
                sp.getparent().remove(sp)
        
        # Добавить элементы
        for el in slide_data["elements"]:
            bbox = el["bbox"]
            
            if el["type"] == "text":
                txBox = slide.shapes.add_textbox(
                    Emu(bbox["x_emu"]), Emu(bbox["y_emu"]),
                    Emu(bbox["w_emu"]), Emu(bbox["h_emu"]),
                )
                tf = txBox.text_frame
                tf.word_wrap = True
                tf.text = el["text"]
                for para in tf.paragraphs:
                    for run in para.runs:
                        run.font.size = Pt(el["style"]["size_pt"])
                        run.font.bold = el["style"].get("weight", 400) >= 700
            
            elif el["type"] == "chart":
                build_chart(slide, el["spec"], ds, bbox)
            
            elif el["type"] == "table":
                build_table(slide, el["spec"], ds, bbox)
    
    prs.save(output_path)
    print(f"[B] Saved to {output_path}")