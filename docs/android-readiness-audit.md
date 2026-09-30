# Аудит готовности Android Alpha — 30.09.2026

## Состояние

Реализационный A0-контур: **кодовый quality pass и CI verification завершены; device evidence ещё не получено**.

## Архитектурно зафиксировано

Эти пункты означают наличие утверждённых контрактов и решений, а не завершённую реализацию Android A0.


- [x] G22/GENOME как нормативный источник
- [x] разделение GENOME / MEMORY / HISTORY / STATE / CONTEXT / ENVIRONMENT
- [x] Android: Kotlin + Compose + Python 3.13 + Chaquopy
- [x] ARM64, minSdk 28, target/compile SDK 37
- [x] OpenRouter + Gemini для Android Alpha
- [x] русскоязычный пользовательский контур
- [x] основной экран разговора и утверждённое боковое меню
- [x] Pulse UX и runtime ownership
- [x] foreground runtime + recovery contract
- [x] Android 13–17 lifecycle requirements
- [x] Room/SQLite persistence contract
- [x] cross-platform semantic persistence
- [x] GitHub как первый transport/storage Кира:Сбор
- [x] encrypted sync envelope
- [x] identity_id / device_id / identity_secret
- [x] QR/manual identity transfer
- [x] MergeIdentity + tombstone
- [x] temporary runtime_instance_id
- [x] Personal / Shared-by-consent / Shared-derived / Public memory scopes
- [x] privacy filtering memory by identity before ModelRequest
- [x] Pre-Generation Reflection Gate
- [x] Response Disclosure Guard
- [x] разделение authority plane и model context
- [x] документация ADR-0014…ADR-0023
- [x] CI Python-пути для android/alpha-parity
- [x] удалены устаревшие внутренние web citation markers из документации
- [x] единая политика UTF-8 без BOM + CI enforcement

## Реализовано в A0

- [x] Android module + Compose host
- [x] embedded Python 3.13 + Chaquopy bridge
- [x] GENOME revision/SHA validation
- [x] RuntimeService boundary
- [x] RuntimeSnapshot и синхронизация с фактическим core_state
- [x] diagnostics contour
- [x] PlatformSecureStore + Android Keystore/AES-GCM foundation
- [x] CryptoProvider + PersistenceProvider foundation
- [x] Python bridge end-to-end smoke
- [x] restart/persistence smoke на Python runtime
- [x] secret/security smoke по исходникам и APK build output
- [x] Android debug APK CI build
- [x] Android unit tests
- [x] repository-wide UTF-8 smoke

Не следует считать реализованными в A0 только по архитектурному контракту:
- полноценный Chat UI и утверждённое боковое меню;
- Pulse chip/avatar UX;
- Room/SQLite domain persistence;
- foreground-service production hardening/recovery;
- реальные OpenRouter/Gemini calls;
- password authority plane и sealed packaging;
- Кира:Сбор;
- identity transfer/merge UI;
- offline inference.

## Требует реализации — !

- [!] Sealed authority packaging: текущий G22/GENOME остаётся plaintext-источником в репозитории; защищённая упаковка переносится на критический этап. Пароль будет запрошен только тогда.
- [!] Криптографическая авторизация Алека на PC: текущая desktop-сессия ещё использует существующую семантику `~1`; password/KDF/verifier + transient privileged grant нужно довести до исполняемого authority plane.
- [x] Android A0: module, Compose host, Python bridge, RuntimeService и diagnostics реализованы; quality pass выполнен.
- [x] Android CI: Android job собирает debug APK, запускает Android unit tests и security smoke.
- [!] GitHub App Кира:Сбор: кодовый контракт готов, но private repository/App/минимальные permissions должны быть настроены при реализации sync.
- [!] Release signing: финальная схема хранения release key ещё не зафиксирована; debug остаётся текущим режимом.
- [!] Реальный тест на устройстве: vivo X100 Ultra / OriginOS 6 ещё не пройден.
- [!] Реальный Android 13–17 matrix ещё не пройден.
- [!] Локальная сборка и устройство из текущей среды не подтверждены; источником факта сборки должен быть реальный CI run, а device evidence — отдельный smoke на vivo X100 Ultra.
- [!] Сложная фильтрация, обезличивание и обобщение глобального опыта сознательно оставлены на поздний PC-контур.

## Следующий этап

**A1 — Core Parity**, но только после закрытия внешнего доказательного контура A0:
1. фактический GitHub CI run для текущего head;
2. подтверждение debug APK;
3. базовый device smoke;
4. затем согласование перехода в A1.

## Граница согласования

Дополнительного изменения общей архитектуры для старта A0 не требуется.

Новые глобальные подтверждения понадобятся только при:
- изменении G22/GENOME;
- изменении identity/privilege model;
- изменении KiraSync protocol;
- изменении состава Alpha;
- переходе к sealed packaging, если это потребует изменения канонического формата GENOME.
## Алгоритм секрета Алека

Пароль не попадает в GitHub и не компилируется в приложение. На критическом этапе он вводится однократно в provisioning-контур; результатом становится зашифрованный authority payload и публичные параметры KDF/verifier. После provisioning plaintext и промежуточные секреты удаляются, выполняется secret scan.


## Quality pass A0 — контрольная точка 30.09.2026

Исправлены замечания самоаудита:
- A0-01: bridge contract доведён до initialize/health/load_genome/create_session/get_runtime_state/run_test_turn/shutdown;
- A0-02: устранена гонка Activity/Service; UI подписывается на RuntimeSnapshot, Service инициализирует runtime асинхронно;
- A0-03: diagnostics расширен до app/core/GENOME/Python/providers/storage/secure-store/runtime;
- A0-04: добавлен Python сквозной bridge smoke; фактический GitHub CI run должен подтвердить сборку и тесты;
- A0-05: добавлен автоматический security smoke без передачи секретов в bridge/UI;
- A0-07: добавлена Android Keystore + AES/GCM реализация PlatformSecureStore;
- A0-08: удалён неполный Gradle Wrapper artifact, CI фиксирует Gradle 9.4.1;
- A0-09: тяжёлая инициализация Python больше не выполняется в Service.onCreate на main thread;
- A0-06 остаётся интерфейсным foundation по границе A0; Room/SQLite доменного persistence переносится на следующий этап согласно плану.

Нерешённые внешние доказательства:
- реальный CI результат текущего head;
- устройство vivo X100 Ultra / OriginOS 6;
- Android 13–17 matrix.


## Верификационный цикл A0 — 30.09.2026

Контрольная точка CI: код и документация quality pass завершены; далее проверяются фактический CI build/test/security и доступные device evidence.


## CI-доказательство A0 — run #161

Контрольный commit: `eaf178c9bd231f85d6ef98ef7b2b95e398ffbde9`.

Фактический GitHub Actions run #161 завершён успешно:
- Python 3.11/3.12 — Ubuntu/Windows: все матричные тестовые jobs успешны;
- package-smoke Linux/Windows: успешны;
- Android A0 smoke: успешен;
- Android API 37.0 SDK установлен;
- `testDebugUnitTest` выполнен успешно;
- `assembleDebug` выполнен успешно;
- debug APK существовал по проверяемому пути `android/app/build/outputs/apk/debug/app-debug.apk`;
- security smoke после сборки прошёл успешно.

Таким образом, A0 имеет фактическое CI evidence для сборки, unit-тестов, Python bridge/security smoke и debug APK.

Не закрыты только внешние device-критерии:
- vivo X100 Ultra / OriginOS 6;
- Android 13–17 реальная matrix;
- instrumentation/device smoke.


## Финальная ревизия A0 — 30.09.2026

Коррекции после последнего успешного run #161:
- UTF-8 enforcement: PYTHONUTF8/PYTHONIOENCODING в CI + tests/utf8_smoke.py без BOM;
- RuntimeSnapshot теперь отражает active_session_id, turn и Pulse из core_state после startup/session/state/test-turn;
- readiness-аудит разделяет архитектурно утверждённые контракты и реально реализованный A0.

G22.txt и GENOME/genome.txt не изменялись.
