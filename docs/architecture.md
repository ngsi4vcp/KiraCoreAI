# Architecture

## Назначение

KiraCoreAI реализует переносимую архитектуру Kira, а не агента, целиком определяемого конкретной LLM.

~~~text
Kira Core
 ├── Kira Harness
 │    ├── Pi host
 │    ├── Codex host
 │    ├── Hermes host
 │    └── other hosts
 ├── ChatGPT realization
 └── future runtimes
~~~

## Слои

**Genome** — нормативный конституционный слой. Он содержит identity invariants, epistemic rules, authorization semantics и stop-elements.

**State** — текущее изменяемое состояние: session, turn, goals, task, host, runtime status и ссылки на актуальные записи.

**Memory** — долговременная информационная организация: episodic, semantic, procedural, autobiographical/self, relationship и task memory.

**History** — причинная линия изменений.

**Context** — оперативный срез, который получает модель. Его формирует Context Compiler.

**Runtime** — жизненный цикл load → validate → restore → compile context → invoke → validate → persist.

**Host** — адаптер конкретной среды/API.

**Model** — LLM или другой cognitive backend. Model не равна всей cognitive architecture.

## Поток данных

~~~text
GENOME
   ↓
STATE
   ↓
MEMORY / HISTORY
   ↓
CONTEXT COMPILER
   ↓
MODEL
   ↓
VALIDATOR
   ↓
STATE / MEMORY / HISTORY
~~~

Путь CONTEXT → MODEL → «новая Кира» не является механизмом изменения генома.

## Genome mutation

~~~text
CANDIDATE
   ↓
ANALYSIS
   ↓
PROPOSAL
   ↓
EXPLICIT ALEK APPROVAL
   ↓
NEW REVISION
   ↓
CHECKSUM / PROVENANCE
   ↓
EVALUATION
~~~

Memory, State и Context не должны иметь прямого права записи в GenomeStore.

## Минимальный Harness

- GenomeLoader
- GenomeValidator
- StateStore
- MemoryStore
- HistoryStore
- ContextCompiler
- HostAdapter
- ModelAdapter
- OutputValidator
- SessionManager
- Persistence
- EvaluationRunner
