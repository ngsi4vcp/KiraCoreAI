# Аудит готовности Android Alpha — 30.09.2026

## Состояние

Архитектурный этап перед A0: **предварительно готов к запуску разработки**.

## Чек-лист

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

## Требует реализации — !

- [!] Sealed authority packaging: текущий G22/GENOME остаётся plaintext-источником в репозитории; защищённая упаковка переносится на критический этап. Пароль будет запрошен только тогда.
- [!] Криптографическая авторизация Алека на PC: текущая desktop-сессия ещё использует существующую семантику `~1`; password/KDF/verifier + transient privileged grant нужно довести до исполняемого authority plane.
- [!] Android A0: Android-модуль ещё не создан; текущая ветка содержит архитектурный и security groundwork.
- [!] Android CI: workflow запускается для ветки, но полноценный Android job появится вместе с Android module.
- [!] GitHub App Кира:Сбор: кодовый контракт готов, но private repository/App/минимальные permissions должны быть настроены при реализации sync.
- [!] Release signing: финальная схема хранения release key ещё не зафиксирована; debug остаётся текущим режимом.
- [!] Реальный тест на устройстве: vivo X100 Ultra / OriginOS 6 ещё не пройден.
- [!] Реальный Android 13–17 matrix ещё не пройден.
- [!] Локальный запуск тестов этого среза из текущей среды не выполнен из-за отсутствия сетевого доступа к GitHub; прошедшими считаются только существующие/будущие CI runs после их фактического результата.
- [!] Сложная фильтрация, обезличивание и обобщение глобального опыта сознательно оставлены на поздний PC-контур.

## Следующий этап

**A0 — Android Skeleton + Runtime Bridge.**

Порядок:
1. Android-модуль;
2. Compose Activity;
3. Python 3.13 / Chaquopy bridge;
4. RuntimeService;
5. PlatformSecureStore/CryptoProvider interfaces;
6. загрузка и валидация G22;
7. диагностический статус;
8. первый сквозной smoke без полноценного UI;
9. затем A1 Core Parity.

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
