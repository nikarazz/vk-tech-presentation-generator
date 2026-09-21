from parser.parse_template import parse_template
from generation.plan_content import plan_content
from generation.export.export_pptx import export_pptx
from generation.export.export_html import export_html
from generation.variants import generate_variants


def run_pipeline(template_path: str, brief: str, output_dir: str = "output"):
    ds = parse_template(template_path)
    print(f"[A] Parsed template, confidence={ds['meta']['confidence']}")
    
    plan = plan_content(brief, {}, ds)
    print(f"[B] Planned {len(plan['slides'])} slides")
    
    variants = generate_variants(plan, ds)
    print(f"[B] Generated 3 variants: {list(variants.keys())}")
    
    for name, pres in variants.items():
        pptx_path = f"{output_dir}/presentation_{name}.pptx"
        html_path = f"{output_dir}/presentation_{name}.html"
        
        export_pptx(pres, ds, template_path, pptx_path)
        export_html(pptx_path, html_path)


if __name__ == "__main__":
    run_pipeline(
        template_path="data/templates/template1.pptx",
        brief="Фича: тёмная тема. Плюс: снижает нагрузку. Метрика: 40%.",
        output_dir="output",
    )