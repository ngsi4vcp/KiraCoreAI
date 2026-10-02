# STATUS — platform/android

**Статус документа:** фактический текущий снимок, не журнал истории.

## Текущая база

- ветка: `platform/android`;
- текущий кодовый migration HEAD: `879ca55b42e1972365731e5d5612770a63f8b61c`;
- текущий документационный HEAD: `39487c4a3ba38e827d3d596f06a056f6b1877af8`;
- Core-срез синхронизирован с `main` на merge-контрольной точке `20372923bb06a3a0f7e6e31419f81233ebd3dde1`;
- принят A2.1;
- A2.2 implementation slice реализован;
- физический rollback instrumentation test добавлен и включён в Android CI;
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

## CI

- sync CI #560 — SUCCESS на исходном кодовом migration HEAD `879ca55b42e1972365731e5d5612770a63f8b61c`;
- после него добавлен физический Room rollback instrumentation test и CI-шаг; результат нового CI ещё не подтверждён.

## Release

- `0.1.0-alpha.1` — исторический desktop pre-release;
- Android public release отсутствует;
- текущий Android test-release публикуется как CI artifact.

## Invariants

G22/GENOME не меняются.
State/Memory/History/Conversation остаются раздельными.
Kotlin не становится отдельным domain layer.
