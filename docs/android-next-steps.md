# Android — следующий инженерный маршрут

Дата: 30 сентября 2026 года.

## Текущая точка

- branch: `android/alpha-parity`
- device evidence run: `20260930-144146`
- device: vivo V2366HA / Android API 36
- A1 Core Parity: **ACCEPTED** для текущего среза
- текущий этап: **A2.1 Store Integration** — реализация завершена; последний полностью зелёный Android-only CI — run `#495`, commit `b52d2be10a0f31a6cb41f1c17d6b973821298502`. Физический A2.1 прогон `20261001-114931` остановился на `backend identity`; исправление внесено в `d79ab7d418d0ba41286d69ebd3ec903982affe42`. Новая device-приёмка ещё не выполнена.
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
- запрет открытого хранения секретных материалов в persistence/UI;
- самопроверка: сборка, модульные тесты, проверка безопасности, UTF-8, содержимое APK.

Фактически уже реализовано в текущем срезе:

`Room schema + gateway` реализованы в commit `54f185bba7360f0551ad2e460b91e0758bdf484f`; CI подтвердит сборку. Runtime ещё не переведён на смешанный режим.

### A2.1 Store Integration

Подключить единый backend к логическим stores:

`StateStore + ConversationStore + MemoryStore + HistoryStore + CoreStatePersistence + RuntimeStore`

Требование: Android не должен иметь одновременно canonical JSON stores и canonical Room stores.

Критерии:

- создание/список/восстановление сессии;
- conversation append/recent;
- разделение candidate/approved памяти;
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
- удаление разговора ≠ удаление сохранённой памяти.

### A2.4 Recovery / Duplicate Prevention

- operation_id/object_id идемпотентность;
- повторная доставка не создаёт дубль;
- crash/restart tests;
- UNKNOWN не вызывает silent retry;
- reconcile boundary подготавливает A5.

### A2.5 A2 Device Gate

На реальном устройстве повторить запуск, создание/восстановление сессии, разговор, разделение памяти, core state, перезапуск процесса, восстановление хранилища, миграционный тест и проверку отсутствия секретов.

A2 принимается только после CI + device evidence + self-audit.

## После A2

A3 Идентичность/полномочия → A4 Кира:Сбор → A5 Восстановление рантайма/сверка → A6 Фоновый режим/FGS → A7 Основной интерфейс → A8 OpenRouter + Gemini → A9 Защита GENOME → A10 КираЧек → A11 матрица Android 13–17/OEM → A12 распространяемый APK Alpha.

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

## Актуальная контрольная точка — 01.10.2026

A2.1 Store Integration **ACCEPTED**.

- code head: `21fe369ba2281fb56b88fde7996c5801eb5af2f9`;
- CI #501: SUCCESS;
- device evidence: `20261001-125458`, vivo V2366HA / API 36;
- manifest: `android-a2.1-device / A2_1_PERSISTENCE_OK`;
- evidence commit: `a03bc0e95a0e95bddce0506f991cbe08740ba889`;
- следующая ветка разработки: `android/a2.2-atomic-turn-wip`.

A2.2 открыт. Первая задача — ввести реальный atomic finalization boundary в едином canonical persistence backend, не перенося domain semantics в Kotlin.
