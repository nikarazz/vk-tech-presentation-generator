import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""Проверка, что буллеты попадают в presentation."""
from parser.parse_template import parse_template
from generation.plan_content import plan_content
from generation.layout_engine import layout_slides

ds = parse_template('data/templates/template1.pptx')
plan = plan_content('Фича: тёмная тема. Метрика: 40%.', {'p': 1}, ds)
pres = layout_slides(plan, ds)

slide2 = pres['slides'][1]
print(f'Slide 2 elements: {len(slide2["elements"])}')
for el in slide2['elements']:
    text = el['text'][:80] if el.get('text') else ''
    print(f"  role={el['role']}, text={text!r}")
