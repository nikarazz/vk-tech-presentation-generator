"""Генерирует 3 презентации на 3 разных шаблонах параллельно."""
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


TEMPLATES = [
    "data/templates/vk_education.pptx",
    "data/templates/vk_tech.pptx",
    "data/templates/vk_workspace.pptx",
]

BRIEF = (
    "Наше решение: сервис для генерации презентаций по шаблону. "
    "Экономит время дизайнеров, сохраняет корпоративный стиль, "
    "генерирует 10-15 слайдов за 5 минут."
)


def generate_one(template_path: str, output_path: str, idx: int) -> dict:
    start = time.time()
    ds = parse_template(template_path)
    plan = plan_content(BRIEF, {}, ds)
    pres = layout_slides(plan, ds)
    export_pptx(pres, ds, template_path, output_path)

    return {
        "idx": idx,
        "template": template_path,
        "output": output_path,
        "slides": len(pres["slides"]),
        "elapsed": round(time.time() - start, 2),
        "confidence": ds["meta"]["confidence"],
    }


async def generate_one_async(template_path, output_path, idx):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, generate_one, template_path, output_path, idx
    )


async def main():
    Path("output").mkdir(exist_ok=True)
    start = time.time()

    tasks = [
        generate_one_async(t, f"output/presentation_{i}.pptx", i)
        for i, t in enumerate(TEMPLATES, 1)
    ]
    results = await asyncio.gather(*tasks)

    total = time.time() - start

    print("=== Results ===")
    for r in results:
        print(f"  #{r['idx']}: {r['template']}")
        print(f"      → {r['output']}")
        print(f"      → {r['slides']} slides, {r['elapsed']}s, conf={r['confidence']}")
    print()
    print(f"=== Total: {total:.2f}s ===")
    print(f"=== Status: {'OK' if total <= 300 else 'FAIL'} ===")


if __name__ == "__main__":
    asyncio.run(main())
