> Примечание статуса: этот документ сохраняет нормативный A0-план и исторические критерии. Фактический результат A0.D1 зафиксирован в `docs/android-port-status.md` и `test-exchange/manifest.json`: run `20260930-131718`, `RECOVERY_OK`, vivo V2366HA / API 36.

# A0 — Каркас Android + мост рантайма

## Цель этапа

Получить минимальный запускаемый Android-контур, в котором Kotlin/Compose host корректно поднимает embedded Python 3.13/KiraCore и способен выполнить диагностический сквозную проверку без построения полноценного пользовательского UI.

A0 не реализует весь Android Alpha и не должен преждевременно включать Kira:Сбор, полноценную identity, сложную память, background hardening или красивый UI хранилища.

## Фактический toolchain на 30.09.2026

- AGP 9.2.1;
- Gradle 9.4.1;
- Kotlin / Compose plugin 2.3.10;
- Compose BOM 2026.09.00;
- JDK 17;
- Python 3.13;
- Chaquopy 17.0.0;
- compileSdk / targetSdk 37;
- minSdk 28;
- ABI arm64-v8a;
- applicationId `ru.kiracore.ai`;
- versionName `0.1.0-alpha.1`.

Это фактическая конфигурация текущей Android-ветки, а не только целевой план.

## Входные условия

- активный GENOME: ревизия 22;
- applicationId: ru.kiracore.ai;
- Kotlin + Jetpack Compose;
- embedded Python 3.13 + Chaquopy 17.0;
- ARM64;
- minSdk 28;
- compileSdk/targetSdk 37;
- OpenRouter и Gemini как целевые Android providers;
- существующий Python KiraCore остаётся доменным runtime;
- Android host не получает права изменять GENOME напрямую.

## A0.1 — Создание Android-модуля

Результат:
- проект/модуль Gradle;
- applicationId;
- manifest;
- Activity на Kotlin/Compose;
- debug build;
- базовые ресурсы;
- минимальная русская строка состояния.

Критерий:
APK собирается и запускается на поддерживаемой архитектуре.

## A0.2 — Chaquopy / Python bridge

Результат:
- подключён Python 3.13;
- подключён KiraCore как embedded Python package;
- определён единый Kotlin → Python bridge API;
- определён lifecycle bridge без прямого доступа UI к Python internals.

Минимальный bridge contract:
- initialize();
- health();
- load_genome();
- create_session();
- get_runtime_state();
- shutdown();

Критерий:
Kotlin вызывает Python runtime и получает структурированный результат.

## A0.3 — Runtime boundary

Результат:
- базовый RuntimeService-контур;
- Activity не владеет runtime state;
- runtime state живёт ниже UI;
- подготовлена event/progress модель для будущего background UI;
- service не имеет внешне экспортируемого IPC.

Критерий:
UI можно уничтожить и восстановить без потери ownership runtime.

## A0.4 — Persistence foundation

В A0 реализуется только интерфейс границы, не вся persistence-система.

Результат:
- PlatformSecureStore interface;
- CryptoProvider interface;
- PersistenceProvider interface;
- Android internal storage root;
- диагностическая проверка доступности backend.

Критерий:
последующие A2-реализации не потребуют переделывать RuntimeBridge.

Android private/internal storage выбран как базовая область для чувствительных app-specific данных. Room/SQLite является целевым физическим backend следующего persistence-этапа; A0 не создаёт вторую доменную БД и реализует только persistence boundary/probe.

## A0.5 — GENOME startup

Результат:
- копия/поставка активного GENOME внутри packaged runtime;
- загрузка;
- parser;
- validator;
- revision/SHA checks;
- диагностический результат.

Критически:
A0 не должен изменять G22 или GENOME.

## A0.6 — Diagnostics

Минимальный экран/endpoint диагностики:

- приложение;
- KiraCore version;
- GENOME revision;
- Python runtime;
- provider availability;
- storage availability;
- secure-store availability;
- runtime status.

Все пользовательские сообщения — на русском.

## A0.7 — Первый smoke

Сценарий:

install
→ start
→ Python initialize
→ GENOME load
→ diagnostics
→ create session
→ симулированный тестовый ход
→ result
→ shutdown
→ restart.

В A0 допускается FakeModel/TestAdapter вместо реального provider.

## A0.8 — Security smoke

Проверить:

- пароль Алека отсутствует;
- API credentials отсутствуют;
- authority payload не содержит plaintext password;
- UI не имеет метода чтения secret material;
- ModelRequest не содержит защищённые секции GENOME;
- build output не содержит случайных секретов;
- debug logs не содержат секретов.

## A0.9 — Self-check перед выходом

Разработчик сверяет:
- AGENTS.md;
- docs/security-architecture.md;
- docs/runtime.md;
- docs/persistence-contract.md;
- docs/android-development-plan.md;
- этот план;
- существующие Python tests.

Затем выполняется отдельный quality pass.

## Не входит в A0

- полноценная password authorization;
- запечатанная упаковка полномочий;
- QR identity;
- identity merge;
- GitHub Sync;
- Kira:Сбор;
- усиление фонового сервисного контура для production;
- Android 13–17 matrix;
- полноценный Chat UI;
- avatar;
- Pulse chip UI;
- контракт фоновых уведомлений для production;
- локальная модель без сети.

## Критерий завершения

A0 завершён, когда:

1. APK собирается;
2. Android host запускает Python KiraCore;
3. GENOME 22 загружается и валидируется;
4. bridge возвращает диагностическое состояние;
5. RuntimeService boundary существует;
6. secure/persistence interfaces существуют;
7. smoke restart проходит;
8. security smoke проходит;
9. тесты и документация актуальны;
10. самоаудит и финальный quality pass завершены;
11. пользователь получает итог на утверждение до перехода в A1.

## A0: внешняя приёмка после реализации — A0.D1

После завершения кодового A0 и проверка CI остаётся внешний acceptance-контур.

### Цель

Проверить на реальном vivo X100 Ultra / OriginOS 6:
- установку и запуск debug APK;
- embedded Python 3.13 / Chaquopy;
- загрузку и SHA-256 проверка GENOME revision 22;
- runtime health и diagnostics;
- создание тестовой session;
- детерминированный тестовый ход;
- PulseStamp и синхронизацию с core_state;
- полный цикл проверки Android Keystore;
- внутреннее storage write/read;
- поведение RuntimeService при background/return;
- controlled process restart и восстановление checkpoint/state;
- экспорт диагностического evidence bundle.

### Экспорт evidence

Диагностический bundle не требует полного доступа к общей файловой системе. Приоритетный механизм — системный Storage Access Framework (ACTION_CREATE_DOCUMENT); допустим также экспорт собственного файла приложения в MediaStore.Downloads на поддерживаемых версиях Android. Wide-storage permission / MANAGE_EXTERNAL_STORAGE для A0.D1 не используется.

### Критерий завершения A0.D1

1. Device Evidence Harness работает на vivo.
2. Все критические A0 checks получили SUCCESS либо имеют оформленный blocker.
3. Evidence bundle получен и проанализирован.
4. Секреты отсутствуют в bundle.
5. Результат зафиксирован в GitHub-документации.
6. Только после этого A0 может быть переведён в статус device-accepted и открывается A1.

Подробный протокол: `docs/android-device-evidence-plan.md`.
Чеклист перехода: `docs/android-development-checklist.md`.

## Фактическое состояние реализации

На текущем цикле A0 реализован полный skeleton-контур A0.1–A0.6 и bridge smoke-контур A0.7/A0.8:

- Android проект/модуль Gradle создан;
- Compose Activity отделена от владельца runtime;
- RuntimeService поднимает Python в отдельном исполнительном потоке;
- RuntimeSnapshot задаёт явные фазы INITIALIZING/READY/FAILED/STOPPING/STOPPED;
- Python bridge реализует initialize(), health(), load_genome(), create_session(), get_runtime_state(), run_test_turn(), shutdown();
- GENOME загружается с обязательной проверкой ревизии 22 и SHA-256 содержимого;
- Android internal storage root диагностически совпадает с Python DATA root;
- PlatformSecureStore имеет Android Keystore + AES/GCM реализацию;
- CryptoProvider имеет SecureRandom/SHA-256 реализацию;
- diagnostics возвращает app/core/GENOME/Python/provider/storage/secure-store/runtime сведения без секретов;
- Python A0 bridge smoke и Android unit tests добавлены в CI;
- Android security smoke проверяет отсутствие hardcoded credentials/private keys;
- неполный Gradle Wrapper не оставлен: CI явно фиксирует Gradle 9.4.1.

Не входит в этот A0 и намеренно оставлено для следующих этапов:
- полноценная password authorization Алека;
- запечатанная упаковка полномочий;
- Room/SQLite domain persistence вместо текущей platform foundation;
- foreground-service production hardening;
- Android 13–17 matrix;
- реальный vivo X100 Ultra;
- полноценный Chat UI/avatar/Pulse chip;
- учётные данные OpenRouter/Gemini и реальные вызовы моделей.

Не закрыто в A0.D1 / внешнем acceptance:

- реальный запуск на vivo X100 Ultra / OriginOS 6;
- модуль диагностики и сбора данных устройства;
- Android 13–17 реальная matrix;
- lifecycle/recovery evidence на физическом устройстве.

CI #190 подтверждает кодовую сборку, unit tests, APK existence и security smoke, но не заменяет device evidence.
