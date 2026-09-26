"""Режим Improve: аудит → repair → повтор, пока не чисто."""

from audit.audit import audit_presentation
from audit.repair import repair_presentation


def improve_presentation(
    presentation: dict,
    design_system: dict,
    max_iterations: int = 3,
    on_progress=None,
) -> dict:
    """
    Итеративно улучшает презентацию.

    Args:
        presentation: исходная презентация (dict).
        design_system: дизайн-система.
        max_iterations: максимум итераций.
        on_progress: callback(iteration, report) для веба.

    Returns:
        {
          "presentation": исправленная презентация,
          "audit_history": [...],
          "repairs": [...],
          "iterations": N,
          "final_summary": {...}
        }
    """
    audit_history = []
    all_repairs = []
    current = presentation

    for i in range(max_iterations):
        report = audit_presentation(current, design_system)
        audit_history.append(report)

        if on_progress:
            on_progress(i + 1, report)

        errors = report["summary"]["errors"]
        if errors == 0:
            break

        current = repair_presentation(current, report, design_system)
        all_repairs.extend(current.get("repairs", []))

    final_report = audit_presentation(current, design_system)

    return {
        "presentation": current,
        "audit_history": audit_history,
        "repairs": all_repairs,
        "iterations": len(audit_history),
        "final_summary": final_report["summary"],
    }


if __name__ == "__main__":
    # Тест на моке
    from shared.mocks.design_system_mock import MOCK_DESIGN_SYSTEM

    mock_presentation = {
        "slides": [
            {
                "slide_id": 1,
                "background_color": "#FFFFFF",
                "elements": [
                    {
                        "element_id": "title",
                        "type": "text",
                        "role": "title",
                        "text": "Тестовый слайд",
                        "bbox": {
                            "x_emu": 1000000,
                            "y_emu": 1000000,
                            "w_emu": 5000000,
                            "h_emu": 500000,
                        },
                        "style": {"font": "Arial", "size_pt": 32, "color": "#000000"},
                    },
                ],
            }
        ]
    }

    result = improve_presentation(mock_presentation, MOCK_DESIGN_SYSTEM)

    print(f"Итераций: {result['iterations']}")
    print(f"Исправлений: {len(result['repairs'])}")
    print(f"Финальный summary: {result['final_summary']}")
