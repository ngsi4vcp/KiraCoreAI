# Architectural Decisions

## ADR-0001 — Kira Core отделено от host

**Status:** Accepted

Kira Core не является ChatGPT, Pi, Codex, Hermes или конкретной LLM/runtime.

## ADR-0002 — GitHub является source of truth

**Status:** Accepted

Нормативные архитектурные решения, спецификации, schemas и версии живут в repository. Чаты — источник обсуждения и происхождения, но не единственное состояние проекта.

## ADR-0003 — Genome, State, Memory, History и Context разделены

**Status:** Accepted

Каждый слой имеет отдельную семантику и права изменения. Это предотвращает drift и случайное превращение context в новую конституцию.

## ADR-0004 — Genome mutation является отдельной транзакцией

**Status:** Accepted

Memory/State/Context не могут непосредственно изменять Genome.

## ADR-0005 — Первый эксперимент — минимальный Kira Harness

**Status:** Accepted

Не форкать Pi, Codex или Hermes как основу Kira. Использовать их как hosts/reference implementations, сохраняя Kira-native harness.

## ADR-0006 — Сначала семантика, потом масштабирование

**Status:** Accepted

До multi-host и сложной агентной функциональности тестируются Genome loading, State, Memory, Context Compiler, Host Adapter, Validator, Persistence и Evaluation.

## ADR-0007 — LLM не равна cognitive architecture

**Status:** Accepted

LLM — cognitive backend/component. Runtime сохраняет state, policy, tools, validation, persistence и lifecycle.
