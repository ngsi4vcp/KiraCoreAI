# Context, State and Memory Model

Главная инженерная задача Kira — контроль того, какая часть долговременной структуры становится оперативным контекстом модели.

Хранение и предъявление информации — разные задачи.

## Канонические уровни

| Уровень | Назначение | Изменяемость |
|---|---|---|
| Genome | конституция | только контролируемая ревизия |
| State | текущее состояние | высокая |
| Memory | долговременная информация | управляемая |
| History | причинная линия | append-oriented |
| Context | оперативный срез | ephemeral |
| Runtime | исполнение | implementation-specific |
| Host | внешняя среда | external |

## Context Compiler

Получает актуальную ревизию Genome, State snapshot, релевантную Memory/History, текущую задачу, tools и ограничения host.

Приоритет:

1. защищённые правила;
2. текущая задача/цель;
3. релевантное состояние;
4. релевантная память;
5. недавние ошибки;
6. доступные инструменты;
7. недавние наблюдения.

Полная память не должна автоматически попадать в prompt.

## Memory record

Минимум:

~~~yaml
id:
type:
content:
timestamp:
source:
confidence:
importance:
provenance:
entities:
valid_from:
valid_to:
~~~

Типы: FACT, RELATIONSHIP, EVENT, DECISION, EXPERIENCE, DISCOVERY, HYPOTHESIS.

## Epistemic status

Нужно различать факт, гипотезу, интерпретацию, вывод и runtime observation. Убедительная реконструкция модели не становится от этого воспоминанием.

## Compression

При сжатии прежде всего сохраняются identity invariants, stop-elements, epistemic distinctions, authorization state, критическое состояние и provenance.
