"""Layout Engine: SlidePlan + DesignSystem → Presentation."""

SKIP_PLACEHOLDER_KEYWORDS = [
    'логотип', 'logo',
    'номер и название', 'номер задачи',
    'иконка задачи', 'иконка',
    'подпись', 'caption',
    'вставить фото', 'вставить qr',
    'qr-код', 'qr код',
    'имя фамилия', 'имя спикера',
    'должность',
    'название компании',
    'vktech', 'vk tech',
    'vk workspace', 'vk education',
    'дополнительная информация',
    'дополнительное описание',
]

ROLE_ORDER = {
    "section_title": 0,
    "slide_title": 0,
    "slide_subtitle": 1,
    "bullet": 2,
    "caption": 3,
    "image": 4,
    "chart": 5,
    "table": 6,
}


def layout_slides(plan: dict, ds: dict, mode: str = "dense") -> dict:
    """Раскладывает слайды по плейсхолдерам."""
    if mode == "dense":
        font_multiplier = 0.85
        padding_multiplier = 0.8
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
    slide_height = ds["meta"]["slide_size"]["height_emu"]
    default_w = slide_width - default_x - safe_area.get("right_emu", 457200)
    default_h = int(1143000 * padding_multiplier)

    # Определяем тёмный шаблон по имени файла
    source = ds["meta"].get("source_file", "").lower()
    is_dark_bg = "vk_tech" in source or "vk_workspace" in source

    # Цвет текста
    if is_dark_bg:
        text_color = "#FFFFFF"
    else:
        text_color = ds["palette"]["colors"].get(
            "text_primary", {"hex": "#1A1A1A"}
        )["hex"]

    for i, spec in enumerate(plan["slides"], start=1):
        pattern_id = spec["pattern_id"]
        pattern = ds["patterns"].get(pattern_id, {})

        elements = []
        y_offset = default_y
        seen_roles = set()

        pattern_has_body = any(
            ph["role"] == "bullet"
            for ph in pattern.get("placeholders", [])
        )

        chart_ph = next(
            (ph for ph in pattern.get("placeholders", [])
             if ph["role"] == "chart"),
            None,
        )
        table_ph = next(
            (ph for ph in pattern.get("placeholders", [])
             if ph["role"] == "table"),
            None,
        )

        for ph in pattern.get("placeholders", []):
            role = ph["role"]
            name = (ph.get("name") or "").lower()

            if any(kw in name for kw in SKIP_PLACEHOLDER_KEYWORDS):
                continue
            if role in ("date", "footer", "slide_number"):
                continue
            if role in ("chart", "table"):
                continue
            if role in seen_roles:
                continue
            seen_roles.add(role)

            if role in ("slide_title", "section_title"):
                text = spec.get("title", "")
            elif role == "slide_subtitle":
                text = spec.get("subtitle", "")
            elif role == "bullet":
                if "bullets" in spec:
                    bullets = spec.get("bullets", [])[:max_bullets]
                    text = "\n".join(bullets)
                elif "content" in spec:
                    lines = [
                        line.strip()
                        for line in spec["content"].split("\n")
                        if line.strip()
                    ]
                    text = "\n".join(lines[:max_bullets])
                else:
                    text = ""
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
                    "w_emu": default_w,
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
                "placeholder_idx": ph.get("idx") if ph.get("is_placeholder", True) else None,
                "bbox": bbox,
                "text": text,
                "style": {
                    "font": font,
                    "size_pt": int(scale["size_pt"] * font_multiplier),
                    "color": text_color,
                    "weight": scale.get("weight", 400),
                },
            })

        # Fallback
        has_bullet = any(el["role"] == "bullet" for el in elements)
        if not has_bullet and not pattern_has_body and spec.get("bullets"):
            text = "\n".join(spec["bullets"][:max_bullets])
            elements.append({
                "element_id": f"bullet_fallback_{i}",
                "type": "text",
                "role": "bullet",
                "placeholder_idx": None,
                "bbox": {
                    "x_emu": default_x,
                    "y_emu": default_y + 1143000,
                    "w_emu": default_w,
                    "h_emu": 3429000,
                },
                "text": text,
                "style": {
                    "font": ds["typography"]["fonts"].get("primary", {}).get("family", "Arial"),
                    "size_pt": 18,
                    "color": text_color,
                    "weight": 400,
                },
            })

        # Убираем текстовые элементы у chart/table
        if spec.get("chart") or spec.get("table"):
            elements = [el for el in elements if el["type"] != "text"]

        elements.sort(key=lambda e: ROLE_ORDER.get(e["role"], 99))

        # CHART
        if spec.get("chart"):
            chart_bbox = {
                "x_emu": int(slide_width * 0.02),
                "y_emu": int(slide_height * 0.25),
                "w_emu": int(slide_width * 0.45),
                "h_emu": int(slide_height * 0.60),
            }
            elements.append({
                "element_id": f"chart_{i}",
                "type": "chart",
                "role": "chart",
                "bbox": chart_bbox,
                "spec": spec["chart"],
            })

        # TABLE
        if spec.get("table"):
            table_bbox = {
                "x_emu": int(slide_width * 0.05),
                "y_emu": int(slide_height * 0.25),
                "w_emu": int(slide_width * 0.90),
                "h_emu": int(slide_height * 0.55),
            }
            elements.append({
                "element_id": f"table_{i}",
                "type": "table",
                "role": "table",
                "bbox": table_bbox,
                "spec": spec["table"],
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
