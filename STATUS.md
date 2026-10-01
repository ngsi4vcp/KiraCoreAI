# STATUS — platform/android

**Статус документа:** фактический текущий снимок, не журнал истории.

## Текущая база

- ветка: `platform/android`;
- исходный code slice: `android/a2.2-atomic-turn-wip`;
- принят A2.1;
- A2.2 implementation slice реализован;
- A2.2 acceptance открыта.

## A2.1 — принято

- device run: `20261001-125458`;
- vivo V2366HA / Android API 36;
- `A2_1_PERSISTENCE_OK`;
- Room backend до/после restart;
- session/state/operation/conversation read-back;
- canonical JSON/JSONL guard;
- encryption at rest;
- CI #501 на принятом code head.

## A2.2 — текущая граница

Реализовано:
- durable pre-call checkpoint;
- `PersistenceBackend.commit_atomic_turn`;
- единый Room transaction для финализации;
- assistant/history/session/core-state/operation finalization;
- failure boundary contract test;
- `UNKNOWN` не становится `COMPLETED`.

Не принято:
- физическая rollback-проверка Room/SQLite;
- отдельная A2.2 device acceptance.

## Invariants

G22/GENOME не меняются.
State/Memory/History/Conversation остаются раздельными.
Kotlin не становится отдельным domain layer.

## Release

- `0.1.0-alpha.1` — исторический desktop release;
- Android public release отсутствует;
- актуальный Android test-release — CI artifact текущей ветки.
