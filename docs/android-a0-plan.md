# A0 — Android Skeleton + Runtime Bridge

## Цель этапа

Получить минимальный запускаемый Android-контур, в котором Kotlin/Compose host корректно поднимает embedded Python 3.13/KiraCore и способен выполнить диагностический сквозной smoke без построения полноценного пользовательского UI.

A0 не реализует весь Android Alpha и не должен преждевременно включать Kira:Сбор, полноценную identity, сложную память, background hardening или красивый room UI.

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
- Gradle project/module;
- applicationId;
- manifest;
- Kotlin/Compose Activity;
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

Android private/internal storage выбран как базовая область для чувствительных app-specific данных; Room используется как базовый механизм private structured storage.

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
→ simulated/test turn
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
- sealed authority packaging;
- QR identity;
- identity merge;
- GitHub Sync;
- Kira:Сбор;
- foreground-service hardening для production;
- Android 13–17 matrix;
- полноценный Chat UI;
- avatar;
- Pulse chip UI;
- background notification production contract;
- offline model.

## Definition of Done

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

## Фактическое состояние реализации

На текущем цикле A0 реализован полный skeleton-контур A0.1–A0.6 и bridge smoke-контур A0.7/A0.8:

- Android Gradle project/module создан;
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
- sealed authority packaging;
- Room/SQLite domain persistence вместо текущей platform foundation;
- foreground-service production hardening;
- Android 13–17 matrix;
- реальный vivo X100 Ultra;
- полноценный Chat UI/avatar/Pulse chip;
- OpenRouter/Gemini credentials и реальные model calls.

Неподтверждённое в текущей среде:

- локальная сборка APK;
- запуск на устройстве;
- Android instrumentation tests;
- Android 13–17 matrix.

Причина локальной недоступности: рабочая среда не разрешает сетевое разрешение GitHub, поэтому результат сборки не имитируется и не объявляется успешным без фактического CI/device evidence.
