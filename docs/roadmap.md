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
- [x] проверка ревизии/SHA GENOME
- [x] основа Android Keystore/AES-GCM
- [x] Android unit tests
- [x] отладочный APK в CI + проверка безопасности

### A0.D1. Диагностика устройства / приёмка устройства
- [x] модуль диагностики устройства
- [x] фактическая проверка на vivo — прогон на vivo V2366HA / Android API 36
- [x] диагностические данные GENOME/Python/рантайма
- [x] диагностические данные сессии/тестового хода/ПУЛЬС
- [x] диагностические данные Keystore/хранилища
- [x] диагностические данные перезапуска/восстановления процесса
- [x] экспорт диагностических материалов без секретов
- [x] отчёт о приёмке A0 / `RECOVERY_OK`

Тестовая модель устройства в историческом плане остаётся vivo X100 Ultra / OriginOS 6, но фактический принятый A0.D1 device — V2366HA/API 36. Матрица Android 13–17 остаётся отдельным A11 контуром.

### A1. Соответствие Core
- [ ] расширенный typed Kotlin ↔ Python bridge
- [ ] запуск/восстановление/жизненный цикл сессии
- [ ] семантическое соответствие сессии/разговора/состояния/памяти/истории
- [ ] authorization `~1` semantic compatibility
- [ ] сквозной путь детерминированного тестового провайдера
- [ ] Pulse parity
- [ ] checkpoints операций рантайма и явная граница UNKNOWN
- [ ] runtime events / diagnostics
- [ ] A1 regression tests

### Текущая контрольная точка Android
A1.6 — граница операции и восстановления — реализован. Свежая проверка соответствия A1 на устройстве `20260930-144146` принята со статусом `RECOVERY_OK`. A2.0 Persistence Foundation реализован; текущий этап — A2.1 Store Integration. Production recovery/reconcile остаётся A5.

### A2. Персистентность
- [ ] Persistence Contract implementation
- [ ] Room/SQLite backend
- [ ] шифрование чувствительных полей payload
- [ ] atomic transactions
- [ ] recovery checkpoints
- [ ] migrations
- [ ] duplicate prevention / idempotency
- [ ] разговор != сохранённая память

### A3. Идентичность и защищённые полномочия
- [ ] identity_id/device_id
- [ ] identity_secret
- [ ] QR/manual transfer
- [ ] MergeIdentity transaction
- [ ] tombstones
- [ ] runtime instance registration
- [ ] verifier/KDF полномочий Алека
- [ ] sealed authority payload
- [ ] transient capability grants

### A4. Кира:Сбор
- [ ] GitHub App / авторизация пользователя
- [ ] encrypted envelopes
- [ ] signing/verification
- [ ] private sync
- [ ] core update
- [ ] sync cursor
- [ ] conflict/rollback handling
- [ ] shared snapshot consumption

### A5. Восстановление рантайма
- [x] основа автомата операций (A1.6)
- [x] UNKNOWN boundary semantics (A1.6)
- [ ] production checkpoint/reconcile
- [ ] отсутствие молчаливого повтора неопределённого вызова модели
- [ ] deterministic recovery tests

### A6. Фоновый рантайм
- [ ] выбор конструкции фонового сервиса из фактических ограничений Android
- [ ] Android 13 notifications
- [ ] соответствие типу/разрешениям FGS на Android 14+
- [ ] обработка тайм-аутов/ограничений Android 15
- [ ] Android 16 quota interactions
- [ ] проверка поведения Android 17/OEM
- [ ] путь запуска/восстановления после загрузки там, где это разрешено
- [ ] battery/OEM diagnostics
- [ ] Кира:Сон
- [ ] no “immortal process” assumption

### A7. Основной интерфейс
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

### A8. Провайдеры
- [ ] OpenRouter credentials/storage
- [ ] каталог OpenRouter + ModelRequest/Response
- [ ] Gemini credentials/storage
- [ ] каталог Gemini + ModelRequest/Response
- [ ] provider error handling
- [ ] no secrets in UI/logs/APK

### A9. Защита GENOME
- [ ] privileged authorization
- [ ] candidate file
- [ ] parse/validate
- [ ] revision/SHA verification
- [ ] diff
- [ ] explicit confirmation
- [ ] atomic activation
- [ ] no direct UI write to GenomeStore

### A10. КираЧек
- [ ] идентичность приложения/Core/GENOME
- [ ] provider/model
- [ ] persistence
- [ ] runtime/background
- [ ] sync
- [ ] permissions/restrictions
- [ ] recent critical errors
- [ ] recovery readiness
- [ ] краткое общее состояние здоровья

### A11. Матрица реальных устройств и тестов
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

### A12. APK Alpha / релиз
- [ ] упаковка классического APK для релиза
- [ ] отладочная подпись только для разработки
- [ ] release signing architecture
- [ ] аудит безопасности/утечек упакованного приложения
- [ ] release artifact verification

### Сквозной контур A3b. Защита полномочий
- [ ] PlatformSecureStore
- [ ] password verifier
- [ ] no hardcoded secrets
- [ ] предгенерационный контур рефлексии
- [ ] Response Disclosure Guard
- [ ] изоляция полномочий и модельного контекста
- [ ] тесты модели угроз обратной инженерии

### Не входит в первую Android Alpha
- [ ] локальная Qwen/локальный механизм вывода без сети
- [ ] полноценная server aggregation
- [ ] сложная глобальная фильтрация/обезличивание на Android
- [ ] token streaming
- [ ] полноценное автономное агентное планирование

Пока A0.D1 и последующие acceptance gates не закрыты, Android Alpha не считается функционально эквивалентной desktop Alpha.
