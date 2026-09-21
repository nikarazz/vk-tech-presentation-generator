from parser.parse_template import parse_template
from generation.plan_content import plan_content
from generation.layout_engine import layout_slides
from generation.export.export_pptx import export_pptx


def run_pipeline(template_path: str, brief: str, output_path: str):
    # A: парсинг
    ds = parse_template(template_path)
    print(f"[A] Parsed template, confidence={ds['meta']['confidence']}")
    print(f"[A] Patterns: {list(ds['patterns'].keys())}")
    print(f"[A] Colors: {list(ds['palette']['colors'].keys())}")
    
    # B: план
    plan = plan_content(brief, {}, ds)
    print(f"[B] Planned {len(plan['slides'])} slides")
    
    # B: раскладка
    pres = layout_slides(plan, ds)
    print(f"[B] Laid out {len(pres['slides'])} slides")
    
    # B: экспорт
    export_pptx(pres, ds, template_path, output_path)


if __name__ == "__main__":
    run_pipeline(
        template_path="data/templates/template1.pptx",
        brief="Фича: тёмная тема. Плюс: снижает нагрузку. Метрика: 40%.",
        output_path="output/presentation.pptx",
    )