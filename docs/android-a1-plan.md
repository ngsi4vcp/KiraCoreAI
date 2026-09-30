# A1 — Core Parity

Дата: 30 сентября 2026 года.

## 1. Цель

Превратить A0 Android foundation в реально исполняющийся Android host текущего KiraCore с сохранением семантики desktop Alpha.

A1 не переписывает Python Core. Он расширяет Android Host/Bridge/Runtime boundary так, чтобы один и тот же доменный runtime мог пройти на Android путь:

```
startup
→ GENOME
→ runtime
→ session
→ authorization semantics
→ user turn
→ ContextCompiler
→ PromptRenderer
→ deterministic ModelAdapter
→ ModelResponse
→ OutputValidator
→ PulseStamp
→ state/conversation persistence
→ restart/recovery
→ resume
```

Реальные OpenRouter/Gemini network calls относятся к последующему provider-этапу A8. A1 доказывает provider-independent runtime semantics через deterministic test adapter.

## 2. Предпосылки

A1 начинается только после:
- A0.D1 acceptance;
- отсутствия критического device blocker;
- актуального `docs/android-development-checklist.md`;
- согласованного baseline GENOME 22.

G22.txt и `GENOME/genome.txt` не изменяются.

## 3. Инварианты A1

1. GENOME остаётся единственным каноническим источником.
2. Kotlin Host не реализует второй Python-domain Core.
3. State, Memory, History, Conversation остаются отдельными семантическими stores.
4. ContextCompiler остаётся производным оперативным контуром.
5. ModelAdapter скрывает provider implementation.
6. Model output не активирует approved memory.
7. PulseStamp создаётся runtime, а не model.
8. UI не получает прямого доступа к GenomeStore/SecureStore/Sync internals.
9. Ошибка model-call не стирает ранее сохранённое состояние.
10. Неопределённый внешний call получает состояние UNKNOWN и не повторяется молча.
11. Android lifecycle не является источником истины доменного состояния.
12. G22/GENOME/security identity contracts не меняются скрытым образом.

## 4. Этап A1.0 — Контрактная фиксация

Перед кодом:
- сверить актуальный API Python Runtime;
- зафиксировать точные JSON/typed payload schemas bridge;
- определить mapping RuntimeSnapshot ↔ core_state;
- определить event/progress model;
- определить error taxonomy;
- зафиксировать current persistence boundary;
- составить список Python APIs, которые Android должен использовать, а не дублировать.

Результат:
- Android bridge contract;
- список unchanged core APIs;
- тестовые fixtures;
- matrix of ожидаемых переходов.

## 5. Этап A1.1 — Типизированный runtime bridge

Расширить `KiraRuntimeBridge` и Python bridge до минимально необходимого parity API:

- start/initialize;
- stop/shutdown;
- health;
- getGenomeInfo;
- getRuntimeState;
- createSession;
- listSessions;
- resumeSession;
- sendTestTurn / deterministic turn;
- getMemory;
- getMemoryCandidates;
- checkHealth;
- sleep preparation boundary.

На этом этапе real provider credentials не подключаются.

Обязательное свойство: UI вызывает типизированные operations, а не Python module internals.

## 6. Этап A1.2 — Владение runtime и lifecycle

Уточнить:
- Activity/Compose не владеет runtime;
- Service/Runtime owns Python lifecycle;
- повторный start idempotent;
- stop корректен;
- failure state observable;
- listener/event subscription не теряет events;
- service restart не создаёт параллельный Python runtime.

Проверки:
- recreate Activity;
- background/foreground;
- duplicate start;
- stop/start;
- failure injection.

## 7. Этап A1.3 — Паритет сессий

Реализовать semantic parity:
- create session;
- active session;
- session metadata;
- last session;
- resume;
- provider/model metadata;
- identity_id только как метаданные на этом этапе;
- authorization state boundary.

Сохранить desktop-совместимую семантику `~1` первого сообщения.

Важно: A1 не делает парольную authority plane. Это A3b/A3.

## 8. Этап A1.4 — Разговор / состояние / ПУЛЬС

Доказать полный deterministic turn:

1. создать session;
2. передать test task;
3. сохранить user-side operation;
4. выполнить deterministic ModelAdapter;
5. получить ModelResponse;
6. выполнить runtime validation;
7. сформировать PulseStamp;
8. обновить core state;
9. сохранить assistant result;
10. вернуть типизированный результат в UI.

Проверки:
- turn increments once;
- Pulse value deterministic;
- Pulse соответствует core_state;
- response metadata сохранены;
- error path не стирает предыдущий state.

## 9. Этап A1.5 — Граница доменной персистентности

A1 обязан доказать семантику persistence, но не должен одновременно переписывать физический backend.

На этом этапе:
- Python current domain stores остаются каноническим runtime backend;
- Android не создаёт параллельную SQLite source of truth;
- Bridge exposes persistence semantics;
- checkpoints/operation states фиксируются в существующем runtime контуре там, где они уже поддержаны.

Room/SQLite физический backend реализуется в A2 после того, как parity semantics подтверждены.

Это разделение необходимо, чтобы ошибки Core parity и ошибки Room integration не смешивались.

## 10. Этап A1.6 — Готовность к восстановлению

Создать минимальный operation/recovery model:
- operation_id;
- phase;
- checkpoint;
- provider/model metadata;
- recovery_state;
- UNKNOWN boundary.

Минимальная state machine:

CREATED
→ PREPARING
→ CONTEXT_READY
→ MODEL_CALL_STARTED
→ MODEL_CALL_FINISHED / UNKNOWN
→ VALIDATING
→ PERSISTING
→ COMPLETED / FAILED

Неизвестный model-call не ретраится молча.

A1 завершает semantic recovery boundary. Полный production recovery реализуется в A5.

## 11. Этап A1.7 — Диагностика и поток событий

Расширить diagnostics:
- app;
- core;
- Python;
- GENOME;
- runtime phase;
- active session;
- turn;
- Pulse;
- provider/model;
- storage backend identity;
- last operation;
- last error;
- recovery state.

Ни один diagnostic payload не содержит:
- secret;
- credentials;
- identity_secret;
- protected GENOME body.

## 12. Этап A1.8 — Тестирование

### Unit

- bridge schemas;
- snapshot mapping;
- state transitions;
- session state;
- Pulse;
- error mapping;
- UNKNOWN semantics.

### JVM/интеграционные проверки, где применимо

- deterministic test turn;
- restart of bridge object;
- idempotent startup/shutdown;
- secure-store regression.

### Device

После каждого significant A1 milestone:
- launch;
- session;
- deterministic turn;
- Pulse;
- process restart;
- recovery.

A0.D1 harness должен продолжать работать.

## 13. Этап A1.9 — Финальный quality pass

Перед закрытием A1:
- самоаудит по AGENTS;
- проверка G22/GENOME invariants;
- compare Python and Android semantics;
- security smoke;
- UTF-8 smoke;
- docs sync;
- test run;
- explicit list of known limitations.

A1 не считается закрытым при просто успешной сборке.

## 14. Definition of Done

A1 принят, когда:
- один deterministic end-to-end turn проходит на Android;
- session create/resume работают;
- runtime state совпадает с Python core state;
- Pulse совпадает и рождается runtime;
- Conversation/State semantic boundaries сохранены;
- operation/recovery state machine зафиксирована;
- UNKNOWN boundary протестирован;
- Activity recreate/background не ломают ownership;
- diagnostics достаточны для дальнейшего A2;
- Android tests и device smoke проходят;
- documentation reflects facts;
- no G22/GENOME changes;
- quality pass завершён.

## 15. Что сознательно не входит в A1

- Room/SQLite production backend;
- реальные OpenRouter/Gemini credentials;
- real network model calls;
- production foreground-service hardening;
- sealed authority packaging;
- QR identity transfer;
- GitHub sync;
- full Chat UI;
- Pulse chip/avatar polish;
- release signing.

Эти функции сохраняются в общей цели Android Alpha, но вводятся после доказательства Core Parity.

## 16. Stop conditions

A1 останавливается и исправляет foundation, если:
- Kotlin начинает дублировать Python domain semantics;
- появляются два источника истины persistence;
- UI получает privileged storage access;
- Pulse начинает генерировать model;
- session semantics расходятся с desktop;
- unknown model-call silently retries;
- новый security invariant нужен, но не оформлен;
- изменяется G22/GENOME без отдельного утверждения.
