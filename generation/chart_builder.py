from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.util import Emu


CHART_TYPE_MAP = {
    "bar":   XL_CHART_TYPE.COLUMN_CLUSTERED,
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "line":  XL_CHART_TYPE.LINE_MARKERS,
    "pie":   XL_CHART_TYPE.PIE,
    "area":  XL_CHART_TYPE.AREA,
}


def build_chart(slide, spec: dict, ds: dict, bbox: dict):
    """
    spec = {
        "type": "bar" | "line" | "pie",
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "series": [
            {"name": "2025", "values": [10, 20, 30, 40]},
            {"name": "2026", "values": [15, 25, 35, 45]},
        ],
        "title": "Динамика по кварталам",  # опционально
    }
    """
    chart_type = CHART_TYPE_MAP.get(spec.get("type", "bar"), XL_CHART_TYPE.COLUMN_CLUSTERED)
    
    chart_data = CategoryChartData()
    chart_data.categories = spec["categories"]
    
    for series in spec["series"]:
        chart_data.add_series(series["name"], series["values"])
    
    chart_shape = slide.shapes.add_chart(
        chart_type,
        Emu(bbox["x_emu"]),
        Emu(bbox["y_emu"]),
        Emu(bbox["w_emu"]),
        Emu(bbox["h_emu"]),
        chart_data,
    )
    
    chart = chart_shape.chart
    
    # Заголовок
    if spec.get("title"):
        chart.has_title = True
        chart.chart_title.text_frame.text = spec["title"]
    else:
        chart.has_title = False
    
    # Легенда (для pie — обязательна, для остальных — если больше одной серии)
    if chart_type == XL_CHART_TYPE.PIE or len(spec["series"]) > 1:
        chart.has_legend = True
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
    else:
        chart.has_legend = False
    
    # Подписи осей (для не-pie)
    if chart_type != XL_CHART_TYPE.PIE:
        try:
            chart.category_axis.has_title = True
            chart.category_axis.axis_title.text_frame.text = spec.get("x_label", "")
            chart.value_axis.has_title = True
            chart.value_axis.axis_title.text_frame.text = spec.get("y_label", "")
        except Exception:
            pass
    
    return chart