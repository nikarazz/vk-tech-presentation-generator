# Модели данных проекта

## 1. Обзор

Все модели данных проекта описаны через Pydantic v2. Они находятся в каталоге `shared/schemas/`.

Модели используются для унификации обмена данными между модулями:

- DesignSystem — параметры дизайн-системы
- Presentation — структура презентации
- SlidePlan — план отдельного слайда
- AuditReport — результат аудита
- Issue — одна найденная проблема

## 2. DesignSystem

DesignSystem — промежуточное представление визуальной системы исходного PowerPoint-шаблона.

Поля:

- slide_width — ширина слайда
- slide_height — высота слайда
- safe_area — безопасная зона (отступы)
- colors — цветовая палитра
- typography — шрифты и размеры
- grid — сетка
- patterns — паттерны компоновки

### ColorPalette

Семантические токены цветовой палитры:

- primary — основной цвет
- secondary — вторичный цвет
- accent — акцент
- text_primary — основной текст
- text_secondary — вторичный текст
- text_inverse — инверсный текст
- background — фон
- surface — поверхность

### Typography

Роли типографики:

- slide_title — заголовок слайда
- slide_subtitle — подзаголовок
- section_title — заголовок раздела
- bullet — основной пункт
- bullet_sub — подпункт
- chart_label — подпись графика
- table_header — заголовок таблицы
- table_cell — ячейка таблицы
- footer — нижний колонтитул

## 3. Presentation

Presentation — структура создаваемой презентации.

Поля:

- slides — список слайдов
- metadata — метаданные
- design_system — дизайн-система

### Slide

Поля:

- shapes — объекты на слайде
- layout — имя layout
- index — индекс слайда

### Shape

Поля:

- shape_id — ID фигуры
- left — координата X
- top — координата Y
- width — ширина
- height — высота
- type — тип (text, chart, table, image)
- text — текст (если применимо)

## 4. SlidePlan

SlidePlan — план отдельного слайда, промежуточная структура между планированием и раскладкой.

Поля:

- index — номер слайда
- title — заголовок
- subtitle — подзаголовок
- content — блоки контента
- layout_hint — рекомендуемый layout

### ContentBlock

Поля:

- type — тип (bullet, chart, table, image)
- data — данные блока
- priority — приоритет

## 5. AuditReport

AuditReport — результат аудита презентации.

Поля:

- issues — список найденных проблем
- checked_slides — сколько слайдов проверено
- duration_sec — время аудита в секундах

Методы:

- has_issues — есть ли проблемы (bool)
- by_slide() — группировка проблем по слайдам (dict[int, list[Issue]])

## 6. Issue

Issue — одна найденная проблема.

Поля:

- slide — номер слайда (0-based)
- shape_id — ID фигуры
- type — тип проблемы
- severity — серьёзность
- message — описание
- bbox — координаты (left, top, width, height)

### IssueType

Возможные значения:

- bounds — выход за границы
- overlap — наложение
- typography — проблемы шрифта
- colors — проблемы контраста
- density — перегруз
- integrity — целостность
- contextual — смысловая проблема (VLM)

### IssueSeverity

Возможные значения:

- low — низкая
- medium — средняя
- high — высокая

### Пример JSON

```json
{
  "slide": 3,
  "shape_id": 12,
  "type": "bounds",
  "severity": "high",
  "message": "Объект выходит за правый край слайда",
  "bbox": [800, 200, 300, 100]
}
```

## 7. Использование

### Создание презентации

```python
from shared.schemas import DesignSystem, Presentation

design_system = DesignSystem(...)
presentation = Presentation(slides=[...], design_system=design_system)
```

### Запуск аудита

```python
from audit.audit import run_audit

report = run_audit(presentation, design_system)
if report.has_issues:
    for slide_idx, issues in report.by_slide().items():
        print(f"Слайд {slide_idx}: {len(issues)} проблем")
```

### Исправление

```python
from audit.repair import repair

presentation = repair(presentation, report, design_system)
```

## 8. Соглашения

- Все модели — на Pydantic v2
- Поля именуются в snake_case
- Enum'ы — на английском
- Описания — на русском
- Модели не содержат логики, кроме вспомогательных методов
