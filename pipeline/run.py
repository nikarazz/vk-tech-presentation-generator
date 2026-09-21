from parser.parse_template import parse_template
from generation.plan_content import plan_content
from generation.export.export_pptx import export_pptx
from generation.export.export_html import export_html
from generation.export.export_pdf import export_pdf
from generation.variants import generate_variants


def run_pipeline(template_path: str, brief: str, output_dir: str = "output"):
    ds = parse_template(template_path)
    print(f"[A] Parsed template, confidence={ds['meta']['confidence']}")
    print(f"[A] Patterns: {list(ds['patterns'].keys())}")
    
    plan = plan_content(brief, {}, ds)
    print(f"[B] Planned {len(plan['slides'])} slides")
    
    variants = generate_variants(plan, ds)
    print(f"[B] Generated 3 variants: {list(variants.keys())}")
    
    for name, pres in variants.items():
        pptx_path = f"{output_dir}/presentation_{name}.pptx"
        html_path = f"{output_dir}/presentation_{name}.html"
        pdf_path = f"{output_dir}/presentation_{name}.pdf"
        
        # PPTX
        export_pptx(pres, ds, template_path, pptx_path)
        
        # HTML
        try:
            export_html(pptx_path, html_path)
        except Exception as e:
            print(f"[B] HTML export failed for {name}: {e}")
        
        # PDF
        try:
            export_pdf(pptx_path, pdf_path)
        except Exception as e:
            print(f"[B] PDF export failed for {name}: {e}")


if __name__ == "__main__":
    run_pipeline(
        template_path="data/templates/template1.pptx",
        brief="Фича: тёмная тема. Плюс: снижает нагрузку. Метрика: 40%.",
        output_dir="output",
    )