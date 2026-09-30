# Android — следующий инженерный маршрут

Дата: 30 сентября 2026 года.

## Текущая точка

- branch: `android/alpha-parity`
- device evidence run: `20260930-144146`
- device: vivo V2366HA / Android API 36
- A1 Core Parity: **ACCEPTED** для текущего среза
- текущий этап: **A2.0 Persistence Foundation**
- активный GENOME: revision 22
- GENOME SHA-256: `dde7ce4b640f9dbcbeed6201559fb118849058e25ceccb9befa663e8ce6b726e`

## Общий принцип

Android продолжает реализовываться как host над единым KiraCore Contract. Room не должен стать вторым domain layer или зеркалом Python JSON. После завершения A2 один экземпляр Android должен иметь один канонический физический persistence backend.

## A2 — Persistence

### A2.0 Persistence Foundation

Цель: подготовить физический backend, не меняя семантику Core.

Сделать:

- Room 2.8.x + SQLite;
- versioned Room schema;
- entities для Session, Conversation, Memory, History, Core State и Runtime Operation;
- CryptoProvider/Keystore boundary для чувствительных payloads;
- backend/gateway interface, который может вызываться из Python через Chaquopy;
- migration test boundary;
- запрет plaintext secret material в persistence/UI;
- self-check: build, unit tests, security smoke, UTF-8, APK content.

Фактически уже реализовано в текущем срезе:

`Room schema + gateway` реализованы в commit `54f185bba7360f0551ad2e460b91e0758bdf484f`; CI подтвердит сборку. Runtime ещё не переведён на смешанный режим.

### A2.1 Store Integration

Подключить единый backend к логическим stores:

`StateStore + ConversationStore + MemoryStore + HistoryStore + CoreStatePersistence + RuntimeStore`

Требование: Android не должен иметь одновременно canonical JSON stores и canonical Room stores.

Критерии:

- create/list/resume session;
- conversation append/recent;
- memory candidate/approved separation;
- history append/recent;
- core state;
- operation state;
- restart read-back.

### A2.2 Atomic Turn

Зафиксировать транзакционный boundary:
`user message → checkpoint → model result → validation → Pulse → assistant message → state update → operation COMPLETED`

Ошибочный/неопределённый ход не должен оставлять несовместимый набор записей.

### A2.3 Migration / Compatibility

- schema version;
- migration N → N+1;
- validation до/после;
- checksum;
- rollback;
- импорт старого JSON только через явный migration path;
- delete conversation ≠ delete retained memory.

### A2.4 Recovery / Duplicate Prevention

- operation_id/object_id идемпотентность;
- повторная доставка не создаёт дубль;
- crash/restart tests;
- UNKNOWN не вызывает silent retry;
- reconcile boundary подготавливает A5.

### A2.5 A2 Device Gate

На реальном устройстве повторить startup, session create/resume, conversation, memory separation, core state, process restart, storage recovery, migration test и secret-scan evidence.

A2 принимается только после CI + device evidence + self-audit.

## После A2

A3 Identity / Authority → A4 Кира:Сбор → A5 Runtime Recovery / Reconcile → A6 Background / FGS hardening → A7 Main UX → A8 OpenRouter + Gemini → A9 Genome Guard → A10 КираЧек → A11 Android 13–17/OEM matrix → A12 distributable APK Alpha.

Эта последовательность сохраняет общую дорожную карту проекта. Desktop track идёт отдельно: незакрытая внешняя Windows/Linux smoke-проверка не заменяется Android acceptance.

## Quality Gate каждого подпредела

- G22/GENOME invariants проверены;
- branch/HEAD и changed files проверены;
- tests/CI;
- security smoke;
- UTF-8;
- отсутствие секретов;
- documentation sync;
- explicit known limitations;
- device evidence, когда подпредел меняет physical Android behavior.

Нельзя закрывать подпредел только потому, что APK собирается.
