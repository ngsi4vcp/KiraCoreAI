# Дорожная карта

## Альфа 0.1.0-alpha.1

- [x] активный KIRA-GENOME
- [x] раздельные слои
- [x] локальная персистентность
- [x] отдельное хранилище разговоров
- [x] единый ModelAdapter
- [x] коннектор OpenRouter
- [x] коннектор Google Gemini
- [x] коннектор LM Studio
- [x] терминальный интерфейс
- [x] динамический выбор модели
- [x] runtime-ПУЛЬС
- [x] START для упаковки
- [x] релизная сборка для Windows/Linux
- [ ] первая внешняя проверка Альфы по сценарию smoke-test

## После первого запуска Альфы

1. стандартизировать ConversationStore по фактической нагрузке;
2. добавить структурированный extractor кандидатов памяти;
3. добавить восстановление незавершённого model-call;
4. добавить streaming;
5. добавить контракт инструментов и рантайма;
6. провести сценарную оценку дрейфа;
7. только после этого углублять агентное планирование.

Не следует до первого Alpha усложнять хранение в распределённую БД или добавлять полноценный vector search без фактической потребности.



## Android Alpha — 0.x

Текущий порядок этапов синхронизирован с `docs/android-alpha-implementation-plan.md`. A0 и последующие этапы имеют отдельные code/acceptance boundaries.

### A0. Skeleton
- [x] Android module
- [x] Kotlin/Compose
- [x] Chaquopy/Python 3.13
- [x] ARM64
- [x] compileSdk/targetSdk 37
- [x] diagnostics skeleton
- [x] RuntimeService boundary
- [x] GENOME revision/SHA validation
- [x] Android Keystore/AES-GCM foundation
- [x] Android unit tests
- [x] CI debug APK + security smoke

### A0.D1. Device Evidence / Device Acceptance
- [ ] Device Evidence Harness
- [ ] vivo X100 Ultra / OriginOS 6 smoke
- [ ] GENOME/Python/runtime evidence
- [ ] session/test-turn/Pulse evidence
- [ ] Keystore/storage evidence
- [ ] process restart/recovery evidence
- [ ] secret-free evidence export
- [ ] A0 acceptance report

### A1. Core Parity
- [ ] расширенный typed Kotlin ↔ Python bridge
- [ ] startup/resume/session lifecycle
- [ ] session/conversation/state/memory/history semantic parity
- [ ] authorization `~1` semantic compatibility
- [ ] deterministic test provider end-to-end path
- [ ] Pulse parity
- [ ] runtime operation checkpoints and explicit UNKNOWN boundary
- [ ] runtime events / diagnostics
- [ ] A1 regression tests

### A2. Persistence
- [ ] Persistence Contract implementation
- [ ] Room/SQLite backend
- [ ] encrypted sensitive payload fields
- [ ] atomic transactions
- [ ] recovery checkpoints
- [ ] migrations
- [ ] duplicate prevention / idempotency
- [ ] conversation != retained memory semantics

### A3. Identity + Authority Security
- [ ] identity_id/device_id
- [ ] identity_secret
- [ ] QR/manual transfer
- [ ] MergeIdentity transaction
- [ ] tombstones
- [ ] runtime instance registration
- [ ] Alek authority verifier/KDF
- [ ] sealed authority payload
- [ ] transient capability grants

### A4. Kira:Сбор
- [ ] GitHub App / user authorization
- [ ] encrypted envelopes
- [ ] signing/verification
- [ ] private sync
- [ ] core update
- [ ] sync cursor
- [ ] conflict/rollback handling
- [ ] shared snapshot consumption

### A5. Runtime Recovery
- [ ] operation state machine
- [ ] UNKNOWN recovery
- [ ] checkpoint/reconcile
- [ ] no silent repeat of uncertain model-call
- [ ] deterministic recovery tests

### A6. Background Runtime
- [ ] foreground service design selected from actual Android constraints
- [ ] Android 13 notifications
- [ ] Android 14+ FGS type/permission compliance
- [ ] Android 15 timeout/restriction handling
- [ ] Android 16 quota interactions
- [ ] Android 17/OEM behavior verification
- [ ] boot/recovery path where permitted
- [ ] battery/OEM diagnostics
- [ ] Кира:Сон
- [ ] no “immortal process” assumption

### A7. Main UX
- [ ] full-screen conversation
- [ ] side menu
- [ ] Pulse chip
- [ ] avatar state model
- [ ] sessions
- [ ] memory/candidates
- [ ] settings
- [ ] КираЧек
- [ ] Геном
- [ ] Кира:Сбор
- [ ] Надстройки

### A8. Providers
- [ ] OpenRouter credentials/storage
- [ ] OpenRouter catalog + ModelRequest/Response
- [ ] Gemini credentials/storage
- [ ] Gemini catalog + ModelRequest/Response
- [ ] provider error handling
- [ ] no secrets in UI/logs/APK

### A9. Genome Guard
- [ ] privileged authorization
- [ ] candidate file
- [ ] parse/validate
- [ ] revision/SHA verification
- [ ] diff
- [ ] explicit confirmation
- [ ] atomic activation
- [ ] no direct UI write to GenomeStore

### A10. КираЧек
- [ ] app/core/GENOME identity
- [ ] provider/model
- [ ] persistence
- [ ] runtime/background
- [ ] sync
- [ ] permissions/restrictions
- [ ] recent critical errors
- [ ] recovery readiness
- [ ] concise overall health state

### A11. Real-device/Test Matrix
- [ ] Android 13
- [ ] Android 14
- [ ] Android 15
- [ ] Android 16
- [ ] Android 17
- [ ] vivo X100 Ultra / OriginOS 6
- [ ] process kill
- [ ] reboot
- [ ] notification behavior
- [ ] battery optimization
- [ ] network loss
- [ ] storage corruption/recovery
- [ ] identity import/merge
- [ ] sync interruption

### A12. APK Alpha / Release
- [ ] classic APK release packaging
- [ ] debug signing only for development
- [ ] release signing architecture
- [ ] packaged security/leakage audit
- [ ] release artifact verification

### Cross-cutting A3b. Authority Security
- [ ] PlatformSecureStore
- [ ] password verifier
- [ ] no hardcoded secrets
- [ ] Pre-Generation Reflection Gate
- [ ] Response Disclosure Guard
- [ ] authority/model-context isolation
- [ ] reverse-engineering threat-model tests

### Не входит в первую Android Alpha
- [ ] offline local Qwen / local inference backend
- [ ] полноценная server aggregation
- [ ] сложная глобальная фильтрация/обезличивание на Android
- [ ] token streaming
- [ ] полноценное автономное агентное планирование

Пока A0.D1 и последующие acceptance gates не закрыты, Android Alpha не считается функционально эквивалентной desktop Alpha.
