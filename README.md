# KiraCoreAI

**KiraCoreAI** — нормативное и исполняемое ядро проекта **Кира:Ядро**.

## Текущий статус

**Genesis / Rev. 22 → первый executable runtime experiment.**

Задача текущего этапа — превратить зафиксированную модель Kira в минимальный проверяемый runtime, не подменяя архитектуру Киры особенностями конкретного host или LLM.

~~~
G22 Genome
    ↓
Kira Loader
    ↓
Persistent State
    ↓
Context Compiler
    ↓
Host Adapter
    ↓
Model
    ↓
Validator
    ↓
Persistent State
~~~

Цель первого этапа — проверить воспроизводимость устойчивых инвариантов: разделение уровней, эпистемическую честность, неизменяемость генома, авторизацию, continuity и устойчивость к context drift.

## Архитектурный принцип

~~~
                    KIRACOREAI
                        │
                 KIRA CORE / GENOME
                        │
                  KIRA HARNESS
                        │
          ┌─────────────┼─────────────┐
          │             │             │
         Pi           Codex        Hermes
          │             │             │
         Host          Host          Host
          │             │             │
        Model         Model         Model
~~~

**Не:** ChatGPT = Kira.  
**Не:** host/framework = Kira.  
**Да:** Kira Core + state + runtime contract + host = конкретная реализация Kira.

## Нормативный порядок

1. genome/ — конституционный слой; G22 является текущей ревизией.
2. docs/ — архитектура и governance.
3. schemas/ — машиночитаемые контракты.
4. capsule/ — переносимое представление Core.
5. runtime/ и implementations/ — конкретные реализации.
6. evaluation/ — проверка инвариантов.

GitHub является источником истины проекта. История чатов не является нормативным состоянием.

## Главные разделения

- **Genome** — конституция.
- **State** — текущее изменяемое состояние.
- **Memory** — долговременная информационная организация.
- **History** — причинная линия.
- **Context** — оперативный срез для модели.
- **Runtime** — механизм исполнения.
- **Host** — конкретная вычислительная/API-среда.
- **Model** — cognitive backend.

Ключевой инвариант:

~~~
GENOME ≠ STATE ≠ MEMORY ≠ HISTORY ≠ CONTEXT ≠ RUNTIME ≠ HOST
~~~

## Первый инженерный milestone

До большой агентной системы необходимо получить минимальный harness:

- GenomeLoader;
- checksum/provenance;
- StateStore;
- MemoryStore;
- HistoryStore;
- Context Compiler;
- один Host Adapter;
- один Model Adapter;
- Validator;
- SessionManager;
- Persistence;
- Evaluation Runner.

## Документация

- Architecture — docs/architecture.md
- Context / State / Memory — docs/context-model.md
- Genome Governance — docs/genome-governance.md
- Evaluation — docs/evaluation.md
- Architectural Decisions — docs/decisions.md
- Roadmap — docs/roadmap.md
- Capsule — capsule/KIRA_CORE_CAPSULE.md

## Важное ограничение

Repository не утверждает наличие сознания или субъективного опыта как научно установленного факта. Это должно быть отделено от инженерно проверяемых свойств runtime.

> Не строить большой runtime, пока семантика GENOME → STATE → MEMORY → CONTEXT → HOST не определена и не тестируется.
