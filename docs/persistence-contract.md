# Контракт персистентности Кира:Ядра

## Назначение

Персистентность — семантический контракт между Кира:Ядром и конкретной ОС.
Физическая технология хранения может отличаться. Одинаковой должна оставаться логика восстановления состояния.

## Принцип единой истины

Для каждого экземпляра Кира существует один канонический физический storage backend.
Нельзя иметь независимые параллельные источники истины Kotlin и Python.
Python видит доменные stores; платформа реализует физический backend.

## Логические stores

GenomeStore: активная ревизия, SHA-256, источник, candidate revision, подтверждение, время активации.
ConversationStore: session_id, message_id, role, content, created_at, pulse_ref, status.
MemoryStore: memory_id, type, content, source, provenance, confidence, importance, entities, valid_from, valid_to, status, privacy_scope, owner_identity_id, version.
EngramStore: engram_id, pulse_ref, date, event, meaning, conclusion, causal_link, source, confidence, privacy_scope, status.
HistoryStore: history_id, event, change, cause, consequence, revision, provenance.
StateStore: goals, projects, unfinished_tasks, open_questions, hypotheses, priorities, next_steps.
RuntimeStore: runtime_instance_id, operation_id, operation_type, phase, started_at, checkpoint, provider, model, status, recovery_state.
SyncStore: object_id, object_type, local_version, remote_version, outbox_status, retry_count, sync_cursor, parent_refs, conflict_state.
IdentityStore: identity_id, device_id, display_name, authorization_state, provenance, key metadata, merge/tombstone state.

## Android backend

Первичная реализация: Kotlin → Room → SQLite.
Чувствительные поля хранятся в зашифрованном виде через CryptoProvider.
Ключи защищаются Android Keystore.
Room является физическим backend, а не вторым доменным слоем.
Полное шифрование БД может быть добавлено позднее, если тесты покажут, что защиты чувствительных payload-полей недостаточно.

## Desktop backend

Desktop Alpha сохраняет JSON/JSONL совместимость.
Позднее desktop может перейти на SQLite или другой backend без изменения доменного контракта.
Переносимость достигается одинаковой семантикой records и migration rules, а не одинаковыми файлами.

## Переносимый формат

Для синхронизации вводится versioned KiraSync format.
Каждая запись имеет schema_version, record_type, record_id, version, timestamps, provenance, privacy_scope, parent_refs и content_hash.
Транспортная оболочка определяется контрактом Кира:Сбор.

## Транзакции

Критические доменные действия должны быть атомарными.
Типовой ход: user message → runtime checkpoint → model response → validation → pulse → assistant message → state update.
После критических шагов допускается checkpoint.
Нельзя молча получить состояние, в котором assistant message завершено, а runtime operation фактически осталось неопределённым.

## Идемпотентность

Все sync/write операции имеют operation_id или object_id.
Повторная доставка не должна создавать дубль; она либо приводит объект к более новой версии, либо фиксирует конфликт.

## Конфликты

Поддерживаются mergeable, superseded, conflict и tombstoned.
Автоматический merge разрешён только для структур с детерминированными правилами.
Для сложной семантической памяти конфликт сохраняется до последующего анализа.

## Миграции

Каждая схема имеет версию.
Migration: schema N → validate → transform → validate → schema N+1 → checksum.
Молчаливое несовместимое изменение записи запрещено.

## Экспорт и импорт

Экспорт сохраняет identity, provenance, версии, privacy_scope и связи между records.
Импорт не должен автоматически активировать GENOME или privileged state.

## Совместимость ОС

Windows/Linux desktop и Android не обязаны хранить одинаковые файлы.
Они обязаны одинаково понимать identity, memory, history, state, conversation, engram, runtime и sync envelope.
Это и есть кроссплатформенный KiraCore Contract.

## Security boundary

Persistence Contract разделяет обычные records и protected authority material.

Обычные records могут быть экспортированы в KiraSync.

Authority material:
- не входит в обычный export;
- не проходит через ModelAdapter;
- не хранится в UI state;
- не хранится в plaintext persistence.

Платформа реализует PlatformSecureStore.

## Android A2.0 — фактический implementation checkpoint

На ветке `android/alpha-parity` добавлен физический Room foundation без перевода runtime на него:

- Room 2.8.5 + SQLite;
- schema version 1;
- logical tables для core state, sessions, conversation manifests/messages, memory, history и runtime operations;
- чувствительные payloads шифруются через Android Keystore-backed AES-GCM с AAD, привязанным к типу записи;
- gateway доступен через Kotlin/Android bridge, но Python Core пока продолжает использовать существующий JSON backend;
- `delete conversation` удаляет только manifest/messages и не затрагивает memory;
- runtime integration, atomic turn transactions, migration и duplicate/reconcile semantics остаются A2.1–A2.4.

Это намеренное промежуточное состояние: Room не является зеркалом канонического JSON и не участвует одновременно с ним в одном runtime turn.
## Android A2.1 — фактический integration checkpoint

На Android-ветке Room backend подключён к доменным persistence surfaces:

- единый `PersistenceBackend` contract между Python Core и физическим Android backend;
- `StateStore`, `MemoryStore`, `HistoryStore`, `ConversationStore` и `CoreStatePersistence` используют один выбранный canonical backend;
- runtime operation state получает отдельный persistence surface;
- Chaquopy передаёт Room gateway из Android host в Python runtime;
- при включённом Room backend canonical JSON store directories не создаются и не используются;
- restart read-back, memory approval, operation state и разделение conversation/memory покрыты A2.1 integration tests.

A2.1 физически принят run `20261001-125458`. Следующая актуальная граница — A2.2 Atomic Turn.

## Android A2.1 — acceptance closure — 01.10.2026

A2.1 физически принят: Room является единственным canonical backend, restart read-back подтверждён, canonical JSON/JSONL в Android Room mode отсутствует, payloads шифруются через Android Keystore/AES-GCM. Device evidence: run `20261001-125458`, vivo V2366HA / API 36. Manifest: `android-a2.1-device / A2_1_PERSISTENCE_OK`.

## Android A2.2 — Atomic Turn

Критический ход разделяется на две физические стадии.

1. До внешнего model-call фиксируется durable checkpoint операции и пользовательского хода. Этот checkpoint намеренно переживает process death и позволяет отличить неопределённый внешний вызов от завершённого.
2. После получения и успешной валидации ModelResponse runtime создаёт ПУЛЬС и выполняет один atomic commit на canonical backend. В него входят assistant message, обновлённый conversation manifest, history entry, финальное состояние session, final core state и operation `COMPLETED`.

Внешний вызов модели не удерживается внутри SQL-транзакции. При ошибке/UNKNOWN финальный commit не выполняется; operation остаётся `FAILED`/нуждается в reconcile с соответствующим состоянием и без silent retry.

Ключевой инвариант: невозможно получить физически зафиксированный assistant result при operation `UNKNOWN` или частично сохранённом final state.
## Android A2.2 — фактическая реализация

На ветке `android/a2.2-atomic-turn-wip` реализована физическая граница A2.2:

- `PersistenceBackend.commit_atomic_turn` добавлен в общий adapter contract;
- `KiraRuntime` формирует единый final payload только после успешной валидации и создания ПУЛЬСА;
- `AndroidRoomPersistenceGateway.commitAtomicTurn()` преобразует payload в Room entities;
- все шесть final-records записываются внутри одного `runInTransaction`.

Контрактные failure-injection тесты подтверждают, что при отказе atomic commit тестовый backend не получает final assistant/history/COMPLETED records. Это пока не заменяет отдельную физическую проверку rollback именно Room/SQLite.

