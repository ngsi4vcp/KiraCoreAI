# Эволюция архитектуры Core — семантические контрольные снимки

## Назначение

Этот файл — **семантический журнал эволюции общего Kira Core**, а не копия исходного кода.

Пока активен режим разработки только для Android, Android может опережать desktop-реализацию. Каждый шаг, который меняет архитектуру Core, Persistence Contract, семантику runtime или иной общий логический контракт, должен добавлять сюда краткий контрольный снимок.

Цель: когда Windows/Linux-контур будет возобновлён, восстановить не только что изменилось в коде, что уже видно из Git, но и какая архитектурная семантика была принята, какие инварианты обязательны и что именно должен реализовать desktop-контур.

### Правило ведения

Контрольный снимок добавляется **только при изменении общего архитектурного или логического контракта**. Обычные исправления, рефакторинг без изменения семантики, UI-изменения Android и изменения только для CI сюда не попадают.

Каждый контрольный снимок содержит:
1. этап и commit;
2. что изменилось семантически;
3. новые/сохранённые инварианты;
4. влияние на Android;
5. обязательные заметки по переносу для Windows/Linux;
6. что намеренно не менялось.

Git остаётся единственным источником полного кода и истории изменений. Этот файл не заменяет Git history, tests, G22/GENOME или persistence contract.

---

## Контрольный снимок S0 — базовая точка Core Parity

**Этап:** A1 Core Parity  
**Статус:** историческая базовая точка.

### Семантика

- Python Core остаётся доменным authority.
- State, Memory, History и Conversation являются разными семантическими поверхностями.
- PULSE генерируется runtime, а не моделью.
- Unknown model calls не должны молча retry.
- Activity/UI не владеет runtime lifecycle; runtime/service владеет runtime.
- Persistence не должна смешивать независимые семантические поверхности.

### Заметки по переносу для Windows/Linux

Windows/Linux должны сохранять эти Core semantics независимо от Android UI, service и storage implementation.

---

## Контрольный снимок S1 — основа персистентности A2.0

**Этап:** A2.0  
**Android baseline:** Room/SQLite schema v1, Android Keystore + AES-GCM payload protection.

### Семантика

Введён единый PersistenceBackend contract, позволяющий Core работать поверх физического persistence adapter без изменения доменной семантики stores.

Ключевой принцип:

**одна физическая canonical persistence backend**, а не параллельные JSON + Room источники истины.

Store-level invariants:
- State, Memory, History, Conversation и Operations остаются отдельными поверхностями;
- JSON persistence и backend persistence не используются одновременно для одного runtime;
- backend отвечает за физическое хранение, Core — за domain semantics;
- Android Room является физическим adapter/backend, а не новым источником domain truth.

### Android

Android использует Room/SQLite как canonical physical backend. Sensitive payloads защищаются Android Keystore/AES-GCM.

### Desktop migration note

При возвращении Windows/Linux необходимо реализовать тот же PersistenceBackend contract или совместимый adapter, сохранив Core semantics. Нельзя копировать Android Room implementation в desktop; переносится **контракт и семантика**, а не конкретный storage engine.

---

## Контрольный снимок S2 — интеграция хранилищ A2.1

**Этап:** A2.1  
**Code head:** 582a7d286bd83b0ac2895d1c50c0cf23b13a2167

### Семантика

Android runtime получает физический Room backend через Android bridge. Runtime/store layer больше не создаёт canonical JSON persistence, когда backend передан.

Persistence lifecycle включает:

write → shutdown → new runtime/backend → read-back

То есть persistence проверяется не только внутри одного process lifetime, но и через новый runtime/backend boundary.

### Обязательные инварианты

- Room остаётся единственным canonical Android physical backend.
- Conversation deletion не удаляет approved Memory.
- Runtime operations сохраняют свой lifecycle/status отдельно от Conversation/Memory.
- Backend identity может диагностироваться как android-room.
- Canonical DATA/*.json / *.jsonl persistence не должна появляться при Android Room mode.
- Известные plaintext payload markers не должны присутствовать в Room DB/WAL/SHM.
- Lifecycle shutdown/reinitialize не должен менять Core semantics.

### Android acceptance

CI A2.1 green; физическая device acceptance является отдельным обязательным gate.

### Desktop migration note

Windows/Linux parity должна реализовать те же observable semantics:
- backend injection в Runtime;
- canonical backend selection;
- persistence across runtime/process restart;
- независимость Conversation и Memory;
- Operation lifecycle persistence;
- отсутствие второго competing source of truth.

Конкретный desktop storage backend выбирается отдельно. Android Room schema и Android Keystore APIs не являются desktop API contract.

---

## Контрольный снимок S3 — атомарная финализация хода A2.2

**Этап:** A2.2 — атомарная финализация хода

Android A2.2 вводит общий логический контракт финализации хода: после durable checkpoint, внешнего model-call и успешной валидации/Pulse финальный набор результата фиксируется одним вызовом `PersistenceBackend.commit_atomic_turn` на canonical backend.

### Семантика

- Внешний вызов модели остаётся вне длительной SQL-транзакции.
- Финальный commit включает assistant message, conversation manifest, history entry, session state, final core state и operation `COMPLETED`.
- `UNKNOWN` не получает `COMPLETED` и не вызывает silent retry.
- Ошибка физической финализации не должна оставлять частично зафиксированный финальный набор записей.

### Android

Python Core остаётся доменным authority. Android Kotlin/Room реализует только физическую границу: `AndroidRoomPersistenceGateway.commitAtomicTurn()` собирает физические entities и выполняет их записи внутри одного `RoomDatabase.runInTransaction`.

Контрактные тесты A2.2 проверяют orchestration и failure boundary через `PersistenceBackend`-adapter. Физическая rollback-проверка именно Room остаётся отдельным acceptance gate.

### Ограничение

Этот snapshot фиксирует изменение общего логического контракта Core и не является заявлением о завершённой A2.2 acceptance. Windows/Linux должны при возвращении разработки реализовать эквивалентную семантику, не копируя реализацию Android Room.

## Future snapshot rule

Следующая запись добавляется только если Android/Core изменяет общий контракт, например:
- меняется lifecycle/state machine;
- меняется persistence contract;
- вводится новый canonical storage semantic;
- меняется Conversation/Memory/History/State boundary;
- меняется model-call/retry/error semantics;
- меняется runtime ownership или service boundary.

Для чисто Android-specific UI/Activity/Compose изменений snapshot не требуется.

Когда Windows/Linux development будет официально возобновлён, этот ledger используется как migration checklist, а затем каждая реализованная desktop adaptation сверяется с соответствующим snapshot и Core tests.

**G22.txt и GENOME/genome.txt не являются частью этого журнала и остаются immutable.**
