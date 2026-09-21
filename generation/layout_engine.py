def layout_slides(plan: dict, ds: dict) -> dict:
    slides = []
    
    grid = ds.get("grid", {})
    safe_area = grid.get("safe_area", {})
    default_x = safe_area.get("left_emu", 457200)
    default_y = safe_area.get("top_emu", 685800)
    slide_width = ds["meta"]["slide_size"]["width_emu"]
    default_w = slide_width - default_x - safe_area.get("right_emu", 457200)
    default_h = 1143000
    
    for i, spec in enumerate(plan["slides"], start=1):
        pattern_id = spec["pattern_id"]
        pattern = ds["patterns"].get(pattern_id, {})
        
        elements = []
        y_offset = default_y
        
        for ph in pattern.get("placeholders", []):
            role = ph["role"]
            
            # Пропускаем служебные плейсхолдеры
            if role in ("date", "footer", "slide_number"):
                continue
            
            # Текст по роли
            if role in ("slide_title", "section_title"):
                text = spec.get("title", "")
            elif role == "slide_subtitle":
                text = spec.get("subtitle", "")
            elif role == "bullet":
                text = "\n".join(spec.get("bullets", []))
            else:
                text = ""
            
            if not text:
                continue
            
            # Координаты из position, если есть
            pos = ph.get("position")
            if pos:
                bbox = {
                    "x_emu": pos["x_emu"],
                    "y_emu": pos["y_emu"],
                    "w_emu": pos["w_emu"],
                    "h_emu": pos["h_emu"],
                }
            else:
                bbox = {
                    "x_emu": default_x,
                    "y_emu": y_offset,
                    "w_emu": default_w,
                    "h_emu": default_h,
                }
                y_offset += default_h + 228600
            
            # Стиль
            role_key = ds["typography"]["roles"].get(role, "body")
            scale = ds["typography"]["scale"].get(role_key, {"size_pt": 16, "weight": 400})
            color = ds["palette"]["colors"].get("text_primary", {"hex": "#1A1A1A"})["hex"]
            font = ds["typography"]["fonts"].get("primary", {}).get("family", "Arial")
            
            elements.append({
                "element_id": f"{role}_{i}",
                "type": "text",
                "role": role,
                "bbox": bbox,
                "text": text,
                "style": {
                    "font": font,
                    "size_pt": scale["size_pt"],
                    "color": color,
                    "weight": scale.get("weight", 400),
                },
            })
        
        slides.append({
            "slide_id": i,
            "pattern_id": pattern_id,
            "layout_ref": pattern.get("layout_ref", ""),
            "elements": elements,
        })
    
    return {
        "template_path": ds["meta"].get("source_file", ""),
        "slides": slides,
    }