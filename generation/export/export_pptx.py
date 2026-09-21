from pptx import Presentation as PptxPresentation
from pptx.util import Emu, Pt


def export_pptx(pres: dict, ds: dict, template_path: str, output_path: str) -> None:
    prs = PptxPresentation(template_path)
    
    # Удалить все существующие слайды из пакета
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    for sld in slides:
        rId = sld.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        prs.part.drop_rel(rId)
        xml_slides.remove(sld)
    
    # Собрать словарь: путь layout → индекс
    layout_by_ref = {}
    for idx, layout in enumerate(prs.slide_layouts):
        ref = str(layout.part.partname).split("/")[-1]
        layout_by_ref[ref] = idx
    
    print(f"[B] Available layouts: {list(layout_by_ref.keys())}")
    
    # Добавить новые слайды
    for slide_data in pres["slides"]:
        layout_ref = slide_data.get("layout_ref", "")
        
        if layout_ref in layout_by_ref:
            layout_idx = layout_by_ref[layout_ref]
            slide = prs.slides.add_slide(prs.slide_layouts[layout_idx])
            print(f"[B] Slide {slide_data['slide_id']}: using layout {layout_ref} (idx={layout_idx})")
        else:
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            print(f"[B] Slide {slide_data['slide_id']}: layout {layout_ref} not found, using blank")
        
        # УДАЛИТЬ все плейсхолдеры из слайда (чтобы не было "Заголовок слайда")
        for shape in list(slide.shapes):
            if shape.is_placeholder:
                sp = shape._element
                sp.getparent().remove(sp)
        
        # Добавить свои text box'ы
        for el in slide_data["elements"]:
            if el["type"] != "text":
                continue
            bbox = el["bbox"]
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
    
    prs.save(output_path)
    print(f"[B] Saved to {output_path}")