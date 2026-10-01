# Core Architecture Evolution Snapshots

## Назначение

Этот файл — **семантический журнал эволюции общего Kira Core**, а не копия исходного кода.

Пока активен Android-only режим, Android может опережать desktop-реализацию. Каждый шаг, который меняет архитектуру Core, persistence contract, runtime semantics или иной общий логический контракт, должен добавлять сюда краткий snapshot.

Цель: когда Windows/Linux-контур будет возобновлён, восстановить не только что изменилось в коде, что уже видно из Git, но и какая архитектурная семантика была принята, какие инварианты обязательны и что именно должен реализовать desktop-контур.

### Правило ведения

Snapshot добавляется **только при изменении общего архитектурного или логического контракта**. Обычные bugfix, refactor без изменения semantics, UI-изменения Android и CI-only изменения сюда не попадают.

Каждый snapshot содержит:
1. этап и commit;
2. что изменилось семантически;
3. новые/сохранённые инварианты;
4. влияние на Android;
5. обязательные migration notes для Windows/Linux;
6. что намеренно не менялось.

Git остаётся единственным источником полного кода и истории изменений. Этот файл не заменяет Git history, tests, G22/GENOME или persistence contract.

---

## Snapshot S0 — Core parity baseline

**Этап:** A1 Core Parity  
**Статус:** историческая базовая точка.

### Семантика

- Python Core остаётся доменным authority.
- State, Memory, History и Conversation являются разными семантическими поверхностями.
- PULSE генерируется runtime, а не моделью.
- Unknown model calls не должны молча retry.
- Activity/UI не владеет runtime lifecycle; runtime/service владеет runtime.
- Persistence не должна смешивать независимые семантические поверхности.

### Desktop migration note

Windows/Linux должны сохранять эти Core semantics независимо от Android UI, service и storage implementation.

---

## Snapshot S1 — A2.0 Persistence Foundation

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

## Snapshot S2 — A2.1 Store Integration

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
