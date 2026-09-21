from parser.parse_template import parse_template
from generation.plan_content import plan_content
from generation.layout_engine import layout_slides
from generation.export.export_pptx import export_pptx
from generation.variants import generate_variants


def run_pipeline(template_path: str, brief: str, output_dir: str = "output"):
    # A: парсинг
    ds = parse_template(template_path)
    print(f"[A] Parsed template, confidence={ds['meta']['confidence']}")
    print(f"[A] Patterns: {list(ds['patterns'].keys())}")
    
    # B: план (один для всех вариантов)
    plan = plan_content(brief, {}, ds)
    print(f"[B] Planned {len(plan['slides'])} slides")
    
    # B: три варианта вёрстки
    variants = generate_variants(plan, ds)
    print(f"[B] Generated 3 variants: {list(variants.keys())}")
    
    # B: экспорт каждого варианта
    for name, pres in variants.items():
        output_path = f"{output_dir}/presentation_{name}.pptx"
        export_pptx(pres, ds, template_path, output_path)
        print(f"[B] Exported {name} → {output_path}")


if __name__ == "__main__":
    run_pipeline(
        template_path="data/templates/template1.pptx",
        brief="Фича: тёмная тема. Плюс: снижает нагрузку. Метрика: 40%.",
        output_dir="output",
    )