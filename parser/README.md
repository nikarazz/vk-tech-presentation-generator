Парсинг .pptx → DesignSystem.

## Что делает

1. **Theme** (`theme_parser.py`) — цвета и шрифты из `theme1.xml`.
2. **Master** (`master_parser.py`) — фон, логотип, стили текста из `slideMaster1.xml`.
3. **Layouts** (`layout_parser.py`) — паттерны слайдов из `slideLayouts/*.xml`.
4. **Slides** (`slide_parser.py`) — конкретные слайды из `slides/*.xml`.
5. **Inheritance** (`inheritance.py`) — резолв цвета, кегля, шрифта внутри элемента.
6. **Resolver** (`resolver.py`) — резолв наследования между уровнями (slide → layout → master → theme).
7. **Grid** (`grid_extractor.py`) — сетка из координат элементов.
8. **Patterns** (`pattern_clusterer.py`) — кластеризация паттернов + usage_count + constraints.

## Главная функция

```python
from parser.parse_template import parse_template

ds = parse_template("data/templates/template1.pptx")