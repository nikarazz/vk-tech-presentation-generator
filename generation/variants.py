from copy import deepcopy


def _apply_dense(plan: dict, ds: dict) -> dict:
    new_plan = deepcopy(plan)
    for slide in new_plan["slides"]:
        if "bullets" in slide:
            slide["bullets"] = slide["bullets"][:6]
    return new_plan


def _apply_airy(plan: dict, ds: dict) -> dict:
    new_plan = deepcopy(plan)
    for slide in new_plan["slides"]:
        if "bullets" in slide:
            slide["bullets"] = slide["bullets"][:3]
        if "title" in slide and len(slide["title"]) > 40:
            slide["title"] = slide["title"][:37] + "..."
    return new_plan


def _apply_data(plan: dict, ds: dict) -> dict:
    new_plan = deepcopy(plan)
    for slide in new_plan["slides"]:
        if "bullets" in slide:
            numbers = [b for b in slide["bullets"] if any(c.isdigit() for c in b)]
            other = [b for b in slide["bullets"] if not any(c.isdigit() for c in b)]
            slide["bullets"] = numbers + other
    return new_plan


def generate_variants(plan: dict, ds: dict) -> dict:
    from generation.layout_engine import layout_slides
    
    return {
        "dense": layout_slides(_apply_dense(plan, ds), ds, mode="dense"),
        "airy":  layout_slides(_apply_airy(plan, ds), ds, mode="airy"),
        "data":  layout_slides(_apply_data(plan, ds), ds, mode="data"),
    }