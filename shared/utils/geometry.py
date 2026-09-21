def bbox_overlap(a: dict, b: dict) -> bool:
    ax1, ay1 = a["x_emu"], a["y_emu"]
    ax2, ay2 = ax1 + a["w_emu"], ay1 + a["h_emu"]
    bx1, by1 = b["x_emu"], b["y_emu"]
    bx2, by2 = bx1 + b["w_emu"], by1 + b["h_emu"]
    return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)

def bbox_inside(inner: dict, outer: dict) -> bool:
    return (
        inner["x_emu"] >= outer["x_emu"]
        and inner["y_emu"] >= outer["y_emu"]
        and inner["x_emu"] + inner["w_emu"] <= outer["x_emu"] + outer["w_emu"]
        and inner["y_emu"] + inner["h_emu"] <= outer["y_emu"] + outer["h_emu"]
    )

def bbox_area(bbox: dict) -> float:
    return bbox["w_emu"] * bbox["h_emu"]