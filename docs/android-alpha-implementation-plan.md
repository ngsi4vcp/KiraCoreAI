# Практический план Android Alpha

## Цель

Получить первый реально запускаемый Android-вариант Кира:Ядра, который работает на Android 9+, проверяется на Android 13–17, использует ARM64, Kotlin, Jetpack Compose, Python 3.13 и Chaquopy, сохраняет смысловую совместимость настольным рантаймом, имеет разговорный UI, локальную персистентность, восстановление после смерти процесса и базовый Кира:Сбор через закрытый GitHub.

## Инструментарий на 30.09.2026

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

## A0 — Каркас Android

Создать один application module, одну Activity, Compose, Navigation, theme, notification channel, foreground-service каркас, контур состояния/диагностики и базовый мост Python.
Проверки: APK собирается, устанавливается, Python 3.13 стартует, runtime возвращает status, APK содержит только arm64-v8a.

## A0.D1 — Диагностика устройства / приёмка устройства

Код A0 и проверка CI уже завершены. Перед A1 выполняется внешняя приёмка на устройстве vivo X100 Ultra / OriginOS 6.

A0.D1 использует тот же APK/applicationId, что и кодовый baseline A0, и может включать временный отладочный модуль диагностики устройства.

Требуемые диагностические материалы:
- device/build identity;
- версия Android и сведения об OEM/рантайме;
- Python 3.13 / Chaquopy startup;
- GENOME revision 22 + SHA-256;
- diagnostics and health;
- test session creation;
- deterministic test turn;
- Pulse/state synchronization;
- полный цикл проверки Android Keystore;
- storage write/read;
- service/background observation;
- контролируемый перезапуск процесса и checkpoint восстановления;
- экспорт диагностических материалов без секретов.

Диагностические материалы экспортируются через системный API выбора файла с участием пользователя; полный доступ к файловой системе не требуется.

Переход A0 → A1 определяется в `docs/android-development-checklist.md`.

> Текущий срез: A0.D1 уже принят на фактическом устройстве; разработка находится на A1.6 Operation / Recovery boundary. Этот документ остаётся нормативной последовательностью этапов, а оперативный статус ведётся в `docs/android-port-status.md`.

## A1 — Core Parity

Подключить текущий Python runtime без логической переписи.
Путь: GENOME → Loader → Parser → Validator → GenomeStore → State/Memory/History/Conversation → ContextCompiler → PromptRenderer → ModelAdapter.
Bridge: startRuntime, stopRuntime, getStatus, getGenomeInfo, createSession, listSessions, resumeSession, sendTurn, getMemory, getMemoryCandidates, checkHealth, sleep.
Проверка: запуск → загрузка GENOME → валидация → новая сессия → авторизация → один пользовательский ход → ответ → ПУЛЬС → сохранение → завершение процесса → перезапуск → восстановление.

## A2 — Persistence

Ввести доменный Persistence Contract.
Android: Room/SQLite + CryptoProvider + Keystore.
Python runtime не получает отдельную БД.
Проверить атомарность хода, recovery checkpoints, duplicate prevention, migration и delete conversation != delete retained memory.

## A3 — Identity и безопасность

Реализовать identity_id, device_id, identity_secret, экспорт, QR, ручную фразу, импорт, объединение, tombstone и регистрацию устройства.
Пароль Алека хранится только как verifier/KDF.
Secrets не попадают в model prompt.
SyncManager не должен быть произвольным model tool.

## A4 — Кира:Сбор

Подключить GitHub Sync Provider.
Поддержать проверку доступности, авторизацию GitHub, manifest, снимок core, зашифрованные приватные объекты, outbox, подпись, проверку подписи, расшифровку, объединение, курсор синхронизации и откат.
GitHub является transport/storage, а не доменной базой Киры.

## A5 — Runtime Recovery

Конечный автомат: CREATED → PREPARING → CONTEXT_READY → MODEL_CALL_STARTED → MODEL_CALL_FINISHED или UNKNOWN → VALIDATING → PERSISTING → COMPLETED или FAILED.
UNKNOWN — полноценное состояние.
После process death восстановить checkpoint, не повторять неизвестный model-call молча, провести reconcile и продолжать только после определённого runtime решения.

## A6 — Background Runtime

Основной контур: Activity → RuntimeService → PythonRuntime → Persistence.
Для Android 14+ FGS type должен быть явно заявлен.
Для long-running KiraRuntime исследуется specialUse; dataSync не используется как бессрочный тип.
Реализовать уведомления, путь запуска/восстановления после загрузки, рекомендации по оптимизации батареи, фоновые диагностические проверки и OEM-диагностику, а также Кира:Сон.
Нельзя обещать бессмертие процесса.

## A7 — Main UX

Главная поверхность: full-screen room, Kira avatar, conversation, Pulse chip и текущий operation status.
Side menu: Сессии, Память, Настройки, КираЧек, Геном, Кира:Сбор, Надстройки.
Все пользовательские сообщения — русский.
Первые состояния аватара: ожидание, размышление, работа, ответ, ошибка, сон.
Token streaming в Alpha не требуется.

## A8 — Providers

Alpha: OpenRouter и Google AI Studio/Gemini.
LM Studio на Android исключён.
Provider API не выходит напрямую в UI.

## A9 — Genome Guard

Экран Геном: привилегированная авторизация → просмотр → файл-кандидат → разбор → валидация → проверка ревизии → SHA-256 → сравнение → явное подтверждение → атомарная активация.
GenomeStore не может быть записан MemoryStore, StateStore или UI.

## A10 — КираЧек

Показывает приложение, KiraCore, GENOME, SHA-256, runtime, provider/model, persistence, background service, permissions, sync, последние критические ошибки и recovery readiness.
Итог: Кира работает / Есть предупреждения / Требуется вмешательство.

## A11 — Тестовая матрица

Обязательная матрица: Android 13, 14, 15, 16, 17.
Первое устройство: vivo X100 Ultra / OriginOS 6.
Проверяются фоновое выполнение, завершение процесса, перезагрузка, уведомления, оптимизация батареи, потеря сети, авторизация GitHub, прерывание синхронизации, повреждение хранилища, импорт и объединение identity.

## A12 — APK Alpha

Классический APK.
Debug signing на ранней разработке.
Release signing architecture оформить отдельно до первой распространяемой сборки.

## Не входит в первую Alpha

локальная модель Qwen без сети, локальный inference backend, полноценная серверная агрегация, сложная глобальная фильтрация памяти, потоковая передача токенов и полноценное автономное агентное планирование.

## Критерий завершения

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

До включения полноценного привилегированный интерфейс Android реализовать:

- PlatformSecureStore;
- password verifier;
- sealed authority payload;
- transient capability grant;
- контур предгенерационной рефлексии;
- Response Disclosure Guard;
- отсутствие protected genome text в ModelRequest;
- отсутствие secrets в APK/resources/Python bytecode;
- тесты модель угроз обратной инженерии на packaged APK.

Важно: публичная семантическая проекция может быть извлечена из приложения. Секретными остаются только защищённые материалы и полномочия.
