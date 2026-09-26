"""Генерирует 3 презентации на 3 шаблонах в 3 вариантах вёрстки (9 .pptx)."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import time
from pathlib import Path

from parser.parse_template import parse_template
from generation.plan_content import plan_content
from generation.layout_engine import layout_slides
from generation.export.export_pptx import export_pptx
from generation.export.export_pdf import export_pdf
from generation.export.export_html import export_html


TEMPLATES = [
    ("vk_education", "data/templates/vk_education.pptx"),
    ("vk_tech", "data/templates/vk_tech.pptx"),
    ("vk_workspace", "data/templates/vk_workspace.pptx"),
]

MODES = ["dense", "airy", "data"]

BRIEF = (
    "Сервис для автоматической генерации презентаций по шаблону. "
    "Проблема: дизайнеры тратят часы на ручную вёрстку. "
    "Решение: парсинг шаблона + LLM + автовёрстка. "
    "Результат: 5 минут вместо часов, стиль сохраняется, 3 варианта вёрстки."
)


def generate_one(name, template_path, mode, ds, plan, output_dir):
    """Генерирует один вариант одной презентации."""
    start = time.time()

    pres = layout_slides(plan, ds, mode=mode)

    base = f"{output_dir}/{name}_{mode}"
    pptx_path = f"{base}.pptx"

    export_pptx(pres, ds, template_path, pptx_path)

    # PDF
    try:
        export_pdf(pptx_path, f"{base}.pdf")
    except Exception as e:
        print(f"[warn] PDF failed for {name}_{mode}: {e}")

    # HTML
    try:
        export_html(pptx_path, f"{base}.html")
    except Exception as e:
        print(f"[warn] HTML failed for {name}_{mode}: {e}")

    elapsed = round(time.time() - start, 2)

    return {
        "name": name,
        "mode": mode,
        "output": pptx_path,
        "slides": len(pres["slides"]),
        "elapsed": elapsed,
    }


async def generate_one_async(*args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_one, *args)


async def main():
    output_dir = "output"
    Path(output_dir).mkdir(exist_ok=True)

    overall_start = time.time()

    print("=== Step 1: Parse templates & plan content ===")
    template_data = {}

    for name, template_path in TEMPLATES:
        print(f"  Parsing {name}...")
        ds = parse_template(template_path)
        print(f"    confidence={ds['meta']['confidence']}, layouts={ds['meta']['layout_count']}")

        print(f"  Planning content for {name}...")
        plan = plan_content(BRIEF, {}, ds)
        print(f"    slides={len(plan.get('slides', []))}")

        template_data[name] = {
            "template_path": template_path,
            "ds": ds,
            "plan": plan,
        }

    print()
    print("=== Step 2: Generate 9 variants ===")

    tasks = []
    for name, data in template_data.items():
        for mode in MODES:
            tasks.append(
                generate_one_async(
                    name,
                    data["template_path"],
                    mode,
                    data["ds"],
                    data["plan"],
                    output_dir,
                )
            )

    results = await asyncio.gather(*tasks)
    overall_elapsed = round(time.time() - overall_start, 2)

    print()
    print("=== Results ===")
    for r in results:
        print(f"  {r['name']}_{r['mode']}: {r['slides']} slides, {r['elapsed']}s → {r['output']}")

    print()
    print(f"=== Total: {overall_elapsed}s ===")
    print(f"=== Target: ≤ 300s ===")
    print(f"=== Status: {'OK' if overall_elapsed <= 300 else 'FAIL'} ===")

    pptx_count = len(list(Path(output_dir).glob("*.pptx")))
    print(f"=== Generated .pptx: {pptx_count} (expected 9) ===")


if __name__ == "__main__":
    asyncio.run(main())
