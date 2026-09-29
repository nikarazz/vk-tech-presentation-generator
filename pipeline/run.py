"""Pipeline генерации презентации по шаблону.

Использование:
    python -m pipeline.run                                    # vk_tech по умолчанию
    python -m pipeline.run data/templates/vk_education.pptx
    python -m pipeline.run data/templates/vk_tech.pptx "Бриф..."
"""
import sys
import traceback

from parser.parse_template import parse_template
from generation.plan_content import plan_content
from generation.export.export_pptx import export_pptx
from generation.export.export_html import export_html
from generation.export.export_pdf import export_pdf
from generation.variants import generate_variants


def run_pipeline(template_path: str, brief: str, output_dir: str = "output") -> dict:
    """Запускает полный pipeline: парсинг → план → варианты → экспорт.

    Возвращает словарь с результатами (для отладки/аудита).
    """
    print(f"\n{'='*60}")
    print(f"[PIPELINE] template = {template_path}")
    print(f"[PIPELINE] brief    = {brief[:80]}{'...' if len(brief) > 80 else ''}")
    print(f"{'='*60}")

    #  Парсинг шаблона 
    ds = parse_template(template_path)
    print(f"[A] Parsed template, confidence={ds['meta']['confidence']}")
    print(f"[A] Patterns ({len(ds['patterns'])}): {list(ds['patterns'].keys())}")

    #  Content Planner 
    plan = plan_content(brief, {}, ds)
    print(f"[B] Planned {len(plan['slides'])} slides")
    for i, spec in enumerate(plan["slides"], 1):
        print(f"    slide {i}: pattern={spec.get('pattern_id')}, title={spec.get('title', '')[:40]!r}")

    # Варианты (dense / airy / data) 
    variants = generate_variants(plan, ds)
    print(f"[B] Generated {len(variants)} variants: {list(variants.keys())}")

    #  Экспорт
    results = {}
    for name, pres in variants.items():
        pptx_path = f"{output_dir}/presentation_{name}.pptx"
        html_path = f"{output_dir}/presentation_{name}.html"
        pdf_path  = f"{output_dir}/presentation_{name}.pdf"

        result = {"pptx": None, "html": None, "pdf": None}

        # PPTX
        try:
            export_pptx(pres, ds, template_path, pptx_path)
            result["pptx"] = pptx_path
        except Exception as e:
            print(f"[B]  PPTX export failed for {name}: {e}")
            traceback.print_exc()
            continue

        # HTML
        try:
            export_html(pptx_path, html_path)
            result["html"] = html_path
        except Exception as e:
            print(f"[B]   HTML export failed for {name}: {e}")

        # PDF
        try:
            export_pdf(pptx_path, pdf_path)
            result["pdf"] = pdf_path
        except Exception as e:
            print(f"[B]   PDF export failed for {name}: {e}")

        results[name] = result

    print(f"\n[PIPELINE] Done. Results:")
    for name, r in results.items():
        print(f"  {name}: pptx={r['pptx']}, html={r['html']}, pdf={r['pdf']}")

    return {"ds": ds, "plan": plan, "variants": variants, "results": results}



# CLI


DEFAULT_TEMPLATE = "data/templates/vk_tech.pptx"
DEFAULT_BRIEF = "Фича: тёмная тема. Плюс: снижает нагрузку. Метрика: 40%."

DEMO_TEMPLATES = [
    ("vk_tech", DEFAULT_BRIEF),
    ("vk_workspace", "Кейс: внедрение VK WorkSpace. Результат: 30% экономии времени."),
    ("vk_education", "Программа IT-дайвинг. 6 специальностей. Регистрация до 25 февраля."),
]


def main():
    args = sys.argv[1:]

    # Режим "прогнать все три шаблона"
    if args and args[0] == "--all":
        for name, brief in DEMO_TEMPLATES:
            try:
                run_pipeline(f"data/templates/{name}.pptx", brief)
            except Exception as e:
                print(f"\n❌ FAIL on {name}: {e}")
                traceback.print_exc()
        return

    # Обычный режим: 1 шаблон
    template = args[0] if len(args) > 0 else DEFAULT_TEMPLATE
    brief    = args[1] if len(args) > 1 else DEFAULT_BRIEF

    try:
        run_pipeline(template, brief)
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()