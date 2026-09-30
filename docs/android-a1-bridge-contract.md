# Android A1.0 — Bridge Contract

Дата: 30.09.2026.

## Область

Этот контракт фиксирует границу Android Host → текущий Python KiraRuntime для этапа A1.0/A1.1.

Канонический runtime остаётся Python KiraCore. Kotlin не воспроизводит ContextCompiler, PromptRenderer, SessionManager, MemoryStore, HistoryStore, ConversationStore или Pulse-логику.

G22 и GENOME/genome.txt не изменяются.

## Операции

### Runtime

initialize(project_root)

{"status":"ready","genome_revision":22,"genome_sha256":"...","python_root":"..."}

shutdown() — возвращает текстовый статус остановки.

health() — компактный health-ответ для совместимости.

check_health()

{"status":"READY","runtime_status":"waiting","active_session_id":"...","turn":1,"pulse":{"series":1000,"revision":22,"turn":1,"value":1024,"key":"1000:22:1:1024"}}

Не содержит secrets или GENOME body.

### GENOME

get_genome_info()

{"revision":22,"series":1000,"sha256":"...","section_count":0}

### Sessions

create_session(provider, model, identity_id?) возвращает manifest выбранной сессии.

list_sessions() возвращает массив manifest-объектов в порядке updated_at DESC.

resume_session(session_id?) без ID выбирает последнюю сессию; с ID проверяет наличие manifest/state; делает выбранную сессию active в текущем runtime state; не изменяет turn, authorization или conversation; возвращает manifest + текущий runtime_state; отсутствие сессии возвращается как null.

### Conversation

get_conversation(session_id, limit=20) возвращает последние сообщения отдельного conversation-store. Порядок: от старого к новому внутри выбранного хвоста.

Каждое сообщение содержит: id, session_id, turn, role, content, timestamp, pulse.

### Memory

get_memory() — только approved memory.
get_memory_candidates() — только candidate memory.
Никакая операция чтения memory не переводит candidate → approved.

### Детерминированный ход

send_test_turn(session_id, task) использует встроенный deterministic adapter. Реальные provider calls не выполняются.

Возвращает response и runtime_state. Pulse рождается Python runtime.

## Классификация ошибок

Bridge не маскирует ошибки домена:

- NOT_READY — runtime не READY;
- SESSION_NOT_FOUND — неизвестный session_id;
- INVALID_ARGUMENT — нарушен формат входа;
- DOMAIN_ERROR — ожидаемая ошибка KiraCore;
- MODEL_ERROR — ошибка deterministic/model adapter;
- UNKNOWN — операция остановилась в неопределённом внешнем состоянии.

До отдельной реализации полного A1.6 UNKNOWN model-call не выполняются автоматические повторы.

## Ownership

- RuntimeService владеет lifecycle Python.
- KiraRuntime владеет domain state.
- Kotlin bridge владеет только transport/mapping.
- Activity/Compose не получает прямые store references.
- UI не изменяет GENOME/SecureStore/Sync internals.

## Матрица проверки A1.0

| Операция | Python source | Android typed facade | Device smoke |
|---|---|---|---|
| startup/health | PASS baseline | A1.1 | A0.D1 PASS |
| genome info | available | A1.1 | A0.D1 PASS |
| create session | available | A1.1 | A0.D1 PASS |
| list sessions | available via ConversationStore | A1.1 | A1 device |
| resume session | runtime extension | A1.1 | A1 device |
| conversation | available via ConversationStore | A1.1 | A1 device |
| approved memory | available | A1.1 | A1 device |
| memory candidates | available | A1.1 | A1 device |
| deterministic turn | available | A1.1 | A0.D1 PASS |
| Pulse/state | available | A1.1 | A0.D1 PASS |

## Stop conditions

Остановиться и исправить контракт, если Kotlin начинает дублировать Core semantics; UI получает прямые Python/store internals; появляется второй источник истины state/memory/history/conversation; Pulse вычисляется на Android; resume создаёт новую сессию вместо восстановления существующей; candidate memory читается как approved.

## Граница тестов

Тесты типизированного отображения Kotlin — обычные модульные тесты JVM. Заглушки `org.json` из Android framework там не используются; `org.json:json:20260814` применяется только в тестах и не попадает в Android-приложение.

После CI run #305 проверке A1.0/A1.2 не мешают ни JSON-транспорт, ни владение жизненным циклом.

## A1.6 — Граница операции и восстановления

Каждый deterministic turn получает persisted operation state:

- CREATED;
- PREPARING;
- CONTEXT_READY;
- MODEL_CALL_STARTED;
- MODEL_CALL_FINISHED;
- VALIDATING;
- PERSISTING;
- COMPLETED;
- FAILED;
- UNKNOWN.

Поля operation:

- operation_id;
- session_id;
- phase;
- checkpoint;
- provider;
- model;
- recovery_state;
- error.

UNKNOWN используется только для явно неопределённого model-call. Такая операция не повторяется автоматически. После process restart operation остаётся доступной в core_state для последующего reconcile; production recovery/reconcile остаётся A5.