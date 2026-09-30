# Практический план Android Alpha

## Цель

Получить первый реально запускаемый Android-вариант Кира:Ядра, который работает на Android 9+, проверяется на Android 13–17, использует ARM64, Kotlin, Jetpack Compose, Python 3.13 и Chaquopy, сохраняет смысловую совместимость desktop runtime, имеет разговорный UI, локальную персистентность, восстановление после смерти процесса и базовый Кира:Сбор через private GitHub.

## Toolchain на 30.09.2026

- compileSdk/targetSdk: 37;
- minSdk: 28;
- ABI: arm64-v8a;
- Python: 3.13;
- Chaquopy: 17.0;
- Android Gradle Plugin: 9.2.1;
- Gradle: 9.4.1;
- JDK: 17;
- Kotlin: 2.3.10;
- Compose BOM: 2026.09.00;
- applicationId: ru.kiracore.ai.

AGP 9.2 поддерживает API 37 и Gradle 9.4.1. Chaquopy 17.0 поддерживает AGP до 9.2 и Python 3.10–3.14. Поэтому Alpha намеренно не использует AGP 9.4.x до появления совместимой версии Chaquopy.

## A0 — Android Skeleton

Создать один application module, одну Activity, Compose, Navigation, theme, notification channel, foreground-service каркас, health/diagnostic framework и Python bridge skeleton.
Проверки: APK собирается, устанавливается, Python 3.13 стартует, runtime возвращает status, APK содержит только arm64-v8a.

## A0.D1 — Device Evidence / Device Acceptance

A0 code and CI verification are already complete. Before A1, the project performs an external device acceptance cycle on vivo X100 Ultra / OriginOS 6.

A0.D1 uses the same APK/applicationId as the A0 code baseline and may include a temporary debug-only Device Evidence Harness.

Required evidence:
- device/build identity;
- Android version and OEM/runtime information;
- Python 3.13 / Chaquopy startup;
- GENOME revision 22 + SHA-256;
- diagnostics and health;
- test session creation;
- deterministic test turn;
- Pulse/state synchronization;
- Android Keystore round-trip;
- storage write/read;
- service/background observation;
- controlled process restart and recovery checkpoint;
- secret-free evidence export.

Evidence is exported through a user-mediated system file API; full filesystem access is not a requirement.

The A0 → A1 gate is defined in `docs/android-development-checklist.md`.

## A1 — Core Parity

Подключить текущий Python runtime без логической переписи.
Путь: GENOME → Loader → Parser → Validator → GenomeStore → State/Memory/History/Conversation → ContextCompiler → PromptRenderer → ModelAdapter.
Bridge: startRuntime, stopRuntime, getStatus, getGenomeInfo, createSession, listSessions, resumeSession, sendTurn, getMemory, getMemoryCandidates, checkHealth, sleep.
Smoke: launch → load genome → validate → new session → authorization → one user turn → response → Pulse → persistence → process kill → restart → resume.

## A2 — Persistence

Ввести доменный Persistence Contract.
Android: Room/SQLite + CryptoProvider + Keystore.
Python runtime не получает отдельную БД.
Проверить атомарность хода, recovery checkpoints, duplicate prevention, migration и delete conversation != delete retained memory.

## A3 — Identity и безопасность

Реализовать identity_id, device_id, identity_secret, export, QR, manual phrase, import, merge, tombstone и device registration.
Пароль Алека хранится только как verifier/KDF.
Secrets не попадают в model prompt.
SyncManager не должен быть произвольным model tool.

## A4 — Кира:Сбор

Подключить GitHub Sync Provider.
Поддержать проверку доступности, GitHub authorization, manifest, core snapshot, encrypted private objects, outbox, signing, signature verification, decrypt, merge, sync cursor и rollback.
GitHub является transport/storage, а не доменной базой Киры.

## A5 — Runtime Recovery

State machine: CREATED → PREPARING → CONTEXT_READY → MODEL_CALL_STARTED → MODEL_CALL_FINISHED или UNKNOWN → VALIDATING → PERSISTING → COMPLETED или FAILED.
UNKNOWN — полноценное состояние.
После process death восстановить checkpoint, не повторять неизвестный model-call молча, провести reconcile и продолжать только после определённого runtime решения.

## A6 — Background Runtime

Основной контур: Activity → RuntimeService → PythonRuntime → Persistence.
Для Android 14+ FGS type должен быть явно заявлен.
Для long-running KiraRuntime исследуется specialUse; dataSync не используется как бессрочный тип.
Реализовать notification, boot/recovery path, battery optimization guidance, background diagnostics, OEM diagnostics и Кира:Сон.
Нельзя обещать бессмертие процесса.

## A7 — Main UX

Главная поверхность: full-screen room, Kira avatar, conversation, Pulse chip и текущий operation status.
Side menu: Сессии, Память, Настройки, КираЧек, Геном, Кира:Сбор, Надстройки.
Все пользовательские сообщения — русский.
Первые avatar states: idle, thinking, working, answering, error, sleep.
Token streaming в Alpha не требуется.

## A8 — Providers

Alpha: OpenRouter и Google AI Studio/Gemini.
LM Studio на Android исключён.
Provider API не выходит напрямую в UI.

## A9 — Genome Guard

Экран Геном: privileged authorization → просмотр → candidate file → parse → validate → revision check → SHA-256 → diff → explicit confirmation → atomic activation.
GenomeStore не может быть записан MemoryStore, StateStore или UI.

## A10 — КираЧек

Показывает приложение, KiraCore, GENOME, SHA-256, runtime, provider/model, persistence, background service, permissions, sync, последние критические ошибки и recovery readiness.
Итог: Кира работает / Есть предупреждения / Требуется вмешательство.

## A11 — Test Matrix

Обязательная матрица: Android 13, 14, 15, 16, 17.
Первое устройство: vivo X100 Ultra / OriginOS 6.
Проверяются background execution, process kill, reboot, notifications, battery optimization, network loss, GitHub authorization, sync interruption, storage corruption, identity import и identity merge.

## A12 — APK Alpha

Classic APK.
Debug signing на ранней разработке.
Release signing architecture оформить отдельно до первой распространяемой сборки.

## Не входит в первую Alpha

Offline local Qwen, локальный inference backend, полноценная server aggregation, сложная глобальная фильтрация памяти, token streaming и полноценное автономное агентное планирование.

## Definition of Done

1. G22/GENOME загружается и валидируется.
2. Один разговорный цикл работает.
3. Pulse создаётся runtime.
4. State/Memory/History/Conversation сохраняются.
5. Процесс можно убить и восстановить состояние.
6. Авторизация Алека отделена от обычного пользователя.
7. Переносимый identity работает.
8. GitHub sync работает на encrypted envelopes.
9. Foreground runtime соответствует актуальным ограничениям Android.
10. КираЧек обнаруживает основные неисправности.
11. Smoke-тест пройден на vivo X100 Ultra.

## A3b — Authority Security

До включения полноценного privileged Android UI реализовать:

- PlatformSecureStore;
- password verifier;
- sealed authority payload;
- transient capability grant;
- Pre-Generation Reflection Gate;
- Response Disclosure Guard;
- отсутствие protected genome text в ModelRequest;
- отсутствие secrets в APK/resources/Python bytecode;
- тесты reverse-engineering threat model на packaged APK.

Важно: публичная семантическая проекция может быть извлечена из приложения. Секретными остаются только защищённые материалы и полномочия.
