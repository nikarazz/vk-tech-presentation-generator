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

ROLE_SIZES = {
    "section_title": 48,
    "slide_title": 40,
    "slide_subtitle": 24,
    "bullet": 18,
    "caption": 14,
    "chart_label": 12,
    "table_header": 14,
    "table_cell": 12,
}


def _estimate_text_height(text: str, size_pt: float, width_emu: int) -> int:
    EMU_PER_PT = 12700
    char_width_pt = size_pt * 0.35
    char_width_emu = char_width_pt * EMU_PER_PT
    chars_per_line = max(1, int(width_emu / char_width_emu))
    lines = 0
    for paragraph in text.split('\n'):
        lines += max(1, (len(paragraph) + chars_per_line - 1) // chars_per_line)
    line_height_emu = size_pt * 1.4 * EMU_PER_PT
    return int(lines * line_height_emu) + int(200000)


def _detect_dark_background(ds: dict) -> bool:
    source = ds["meta"].get("source_file", "").lower()
    source_clean = source.replace(" ", "_").replace("-", "_")
    if "vk_tech" in source_clean or "vk_workspace" in source_clean:
        return True
    if "tech" in source_clean or "workspace" in source_clean:
        return True
    bg_hex = ds["palette"]["colors"].get("background", {}).get("hex", "#FFFFFF")
    try:
        h = bg_hex.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        if (r + g + b) / 3 < 128:
            return True
    except Exception:
        pass
    return False


def layout_slides(plan: dict, ds: dict, mode: str = "dense") -> dict:
    if mode == "dense":
        font_multiplier = 1.0
        max_bullets = 6
    elif mode == "airy":
        font_multiplier = 1.1
        max_bullets = 4
    elif mode == "data":
        font_multiplier = 1.0
        max_bullets = 8
    else:
        font_multiplier = 1.0
        max_bullets = 6

    slides = []
    slide_width = ds["meta"]["slide_size"]["width_emu"]
    slide_height = ds["meta"]["slide_size"]["height_emu"]

    # Большие отступы — слайд дышит
    default_x = int(slide_width * 0.08)
    default_y = int(slide_height * 0.15)
    default_w = int(slide_width * 0.84)
    default_h = int(slide_height * 0.15)

    is_dark_bg = _detect_dark_background(ds)

    if is_dark_bg:
        text_color = "#FFFFFF"
    else:
        text_color = ds["palette"]["colors"].get(
            "text_primary", {"hex": "#1A1A1A"}
        )["hex"]

    font_family = (
        ds["typography"]["fonts"].get("primary", {}).get("family", "Arial")
    )

    for i, spec in enumerate(plan["slides"], start=1):
        pattern_id = spec["pattern_id"]
        pattern = ds["patterns"].get(pattern_id, {})

        elements = []
        y_offset = default_y
        seen_roles = set()
        bullet_idx = 0

        # Считаем количество bullet в layout
        bullet_count = len([
            ph for ph in pattern.get("placeholders", [])
            if ph["role"] == "bullet"
        ])

        # Режим колонок: если 3+ bullet в layout — горизонтальная раскладка
        use_columns = bullet_count >= 3

        if use_columns:
            cols = bullet_count
            col_gap = int(slide_width * 0.02)
            col_width = int((default_w - col_gap * (cols - 1)) / cols)

        for ph in pattern.get("placeholders", []):
            role = ph["role"]
            name = (ph.get("name") or "").lower()

            if any(kw in name for kw in SKIP_PLACEHOLDER_KEYWORDS):
                continue
            if role in ("date", "footer", "slide_number"):
                continue
            if role in ("chart", "table"):
                continue

            if role != "bullet":
                if role in seen_roles:
                    continue
                seen_roles.add(role)

            if role in ("slide_title", "section_title"):
                text = spec.get("title", "")
            elif role == "slide_subtitle":
                text = spec.get("subtitle", "")
            elif role == "bullet":
                bullets = spec.get("bullets", [])
                if bullet_idx < len(bullets) and bullet_idx < max_bullets:
                    text = bullets[bullet_idx]
                elif "content" in spec:
                    lines = [
                        line.strip()
                        for line in spec["content"].split("\n")
                        if line.strip()
                    ]
                    if bullet_idx < len(lines) and bullet_idx < max_bullets:
                        text = lines[bullet_idx]
                    else:
                        text = ""
                else:
                    text = ""
            elif role == "caption":
                text = spec.get("caption", "")
            else:
                text = ""

            if not text:
                bullet_idx += 1
                continue

            # === BBOX ===
            if use_columns and role == "bullet":
                # Горизонтальная раскладка: bullet в колонку
                col_idx = bullet_idx
                bbox = {
                    "x_emu": default_x + col_idx * (col_width + col_gap),
                    "y_emu": default_y,
                    "w_emu": col_width,
                    "h_emu": int(slide_height * 0.55),
                }
            elif role in ("slide_title", "section_title"):
                # Title — по центру или слева, с отступом
                bbox = {
                    "x_emu": default_x,
                    "y_emu": int(slide_height * 0.08),
                    "w_emu": default_w,
                    "h_emu": int(slide_height * 0.15),
                }
            elif pos := ph.get("position"):
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
                    "w_emu": int(default_w * 0.6),
                    "h_emu": default_h,
                }
                y_offset += default_h + int(slide_height * 0.03)

            if role == "bullet":
                bullet_idx += 1

            # === STYLE ===
            size_pt = ROLE_SIZES.get(role, 16)
            weight = 700 if role in ("slide_title", "section_title") else 400

            text_height = _estimate_text_height(text, size_pt, bbox["w_emu"])
            min_size = 14 if role == "bullet" else 24
            while text_height > bbox["h_emu"] and size_pt > min_size:
                size_pt -= 1
                text_height = _estimate_text_height(text, size_pt, bbox["w_emu"])

            elements.append({
                "element_id": f"{role}_{i}",
                "type": "text",
                "role": role,
                "placeholder_idx": ph.get("idx") if ph.get("is_placeholder", True) else None,
                "bbox": bbox,
                "text": text,
                "style": {
                    "font": font_family,
                    "size_pt": int(size_pt * font_multiplier),
                    "color": text_color,
                    "weight": weight,
                },
            })

        elements.sort(key=lambda e: ROLE_ORDER.get(e["role"], 99))

        # Если chart/table — убираем текст
        if spec.get("chart") or spec.get("table"):
            elements = [el for el in elements if el["type"] != "text"]

        if spec.get("chart"):
            elements.append({
                "element_id": f"chart_{i}",
                "type": "chart",
                "role": "chart",
                "bbox": {
                    "x_emu": int(slide_width * 0.1),
                    "y_emu": int(slide_height * 0.25),
                    "w_emu": int(slide_width * 0.8),
                    "h_emu": int(slide_height * 0.6),
                },
                "spec": spec["chart"],
            })

        if spec.get("table"):
            elements.append({
                "element_id": f"table_{i}",
                "type": "table",
                "role": "table",
                "bbox": {
                    "x_emu": int(slide_width * 0.08),
                    "y_emu": int(slide_height * 0.28),
                    "w_emu": int(slide_width * 0.84),
                    "h_emu": int(slide_height * 0.55),
                },
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
