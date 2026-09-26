"""Layout Engine: SlidePlan + DesignSystem → Presentation."""


def layout_slides(plan: dict, ds: dict, mode: str = "dense") -> dict:
    """Раскладывает слайды по плейсхолдерам."""
    if mode == "dense":
        font_multiplier = 1.0
        padding_multiplier = 1.0
        max_bullets = 6
    elif mode == "airy":
        font_multiplier = 1.3
        padding_multiplier = 1.6
        max_bullets = 3
    elif mode == "data":
        font_multiplier = 1.0
        padding_multiplier = 1.0
        max_bullets = 8
    else:
        font_multiplier = 1.0
        padding_multiplier = 1.0
        max_bullets = 6

    slides = []
    grid = ds.get("grid", {})
    safe_area = grid.get("safe_area", {})
    default_x = safe_area.get("left_emu", 457200)
    default_y = safe_area.get("top_emu", 685800)
    slide_width = ds["meta"]["slide_size"]["width_emu"]
    default_w = slide_width - default_x - safe_area.get("right_emu", 457200)
    default_h = int(1143000 * padding_multiplier)

    for i, spec in enumerate(plan["slides"], start=1):
        pattern_id = spec["pattern_id"]
        pattern = ds["patterns"].get(pattern_id, {})

        elements = []
        y_offset = default_y

        for ph in pattern.get("placeholders", []):
            role = ph["role"]

            if role in ("date", "footer", "slide_number"):
                continue

            # Пропускаем декор (placeholder'ы с мусорным текстом)
            if role == "decoration":
                continue

            # Не дублируем bullet — в шаблоне их бывает несколько
            if role == "bullet" and any(e["role"] == "bullet" for e in elements):
                continue

            if role in ("slide_title", "section_title"):
                text = spec.get("title", "")
            elif role == "slide_subtitle":
                text = spec.get("subtitle", "")
            elif role == "bullet":
                bullets = spec.get("bullets", [])[:max_bullets]
                text = "\n".join(bullets)
            elif role == "caption":
                text = spec.get("caption", "")
            else:
                text = ""

            if not text:
                continue

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
                    "w_emu": int(default_w * 0.55),
                    "h_emu": default_h,
                }
                y_offset += default_h + int(228600 * padding_multiplier)

            role_key = ds["typography"]["roles"].get(role, "body")
            scale = ds["typography"]["scale"].get(
                role_key, {"size_pt": 16, "weight": 400}
            )
            font = (
                ds["typography"]["fonts"]
                .get("primary", {})
                .get("family", "Arial")
            )

            elements.append({
                "element_id": f"{role}_{i}",
                "type": "text",
                "role": role,
                "placeholder_idx": ph.get("idx"),
                "bbox": bbox,
                "text": text,
                "style": {
                    "font": font,
                    "size_pt": int(scale["size_pt"] * font_multiplier),
                    "weight": scale.get("weight", 400),
                },
            })

        # ── Fallback: буллеты есть, но bullet-элемента нет ──
        bullets_text = "\n".join(spec.get("bullets", [])[:max_bullets])
        has_bullet_el = any(e.get("role") == "bullet" for e in elements)
        if bullets_text and not has_bullet_el:
            role_key = ds["typography"]["roles"].get("bullet", "body")
            scale = ds["typography"]["scale"].get(
                role_key, {"size_pt": 16, "weight": 400}
            )
            font = (
                ds["typography"]["fonts"]
                .get("primary", {})
                .get("family", "Arial")
            )
            elements.append({
                "element_id": f"bullet_{i}_fallback",
                "type": "text",
                "role": "bullet",
                "placeholder_idx": None,
                "bbox": {
                    "x_emu": default_x,
                    "y_emu": default_y + 1200000,   # ниже заголовка
                    "w_emu": int(default_w * 0.75),
                    "h_emu": 2500000,
                },
                "text": bullets_text,
                "style": {
                    "font": font,
                    "size_pt": int(scale["size_pt"] * font_multiplier),
                    "weight": scale.get("weight", 400),
                },
            })

        # График
        if spec.get("chart"):
            elements.append({
                "element_id": f"chart_{i}",
                "type": "chart",
                "role": "chart",
                "bbox": {
                    "x_emu": default_x,
                    "y_emu": y_offset,
                    "w_emu": default_w,
                    "h_emu": 3429000,
                },
                "spec": spec["chart"],
            })
            y_offset += 3429000 + 228600

        # Таблица
        if spec.get("table"):
            elements.append({
                "element_id": f"table_{i}",
                "type": "table",
                "role": "table",
                "bbox": {
                    "x_emu": default_x,
                    "y_emu": y_offset,
                    "w_emu": default_w,
                    "h_emu": 2286000,
                },
                "spec": spec["table"],
            })
            y_offset += 2286000 + 228600

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