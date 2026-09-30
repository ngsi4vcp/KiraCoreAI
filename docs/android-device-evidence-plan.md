# A0.D1 — Device Evidence / Device Acceptance

Дата: 30 сентября 2026 года.

## 1. Назначение

A0 code и CI verification уже завершены. A0.D1 закрывает внешний доказательный контур: фактическую работу текущего Android foundation на vivo X100 Ultra / OriginOS 6.

A0.D1 не добавляет доменной функциональности. Временная задача — сделать наблюдаемым и воспроизводимым то, что уже существует.

## 2. Фактический baseline

- branch: `android/alpha-parity`;
- code baseline: `398586db03f096318faf2fd275a2db86905b5aa5`;
- applicationId: `ru.kiracore.ai`;
- versionName: `0.1.0-alpha.1`;
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
- GENOME revision 22;
- canonical GENOME SHA-256: `dde7ce4b640f9dbcbeed6201559fb118849058e25ceccb9befa663e8ce6b726e`.

## 3. Почему harness нужен

Текущий A0 APK уже умеет поднимать runtime, но без instrumentation/device evidence мы не знаем фактическое поведение на OEM-железе.

CI #190 доказывает:
- unit tests;
- Gradle build;
- debug APK existence;
- repository/security smoke.

CI не доказывает:
- реальный Chaquopy startup на vivo;
- Keystore behavior на конкретном устройстве;
- OEM lifecycle behavior;
- process death/recovery;
- реальные storage characteristics.

## 4. Архитектура harness

Harness размещается только в debug source set.

Он использует:
- тот же `ru.kiracore.ai`;
- тот же embedded GENOME;
- тот же `KiraRuntimeService`;
- тот же `KiraRuntimeBridge`;
- тот же Python `android_bridge.py`;
- тот же PlatformSecureStore.

Он не должен создавать второй runtime и не должен иметь отдельную доменную БД.

### UI

Минимальный debug-screen:
- запуск smoke;
- текущая phase;
- текущий check;
- PASS/FAIL;
- export evidence;
- повтор запуска;
- controlled restart/recovery.

### Event stream

Каждая проверка пишет структурированное событие:
- timestamp;
- event_id;
- phase;
- status;
- duration_ms;
- safe_details.

## 5. Сценарий проверки

### D1.0 Окружение

Записать:
- Android SDK level;
- OS release;
- manufacturer/model;
- ABI;
- app version;
- безопасные безопасные метаданные устройства/runtime.

### D1.1 Startup

Проверить:
- Activity launch;
- RuntimeService start;
- Python initialization;
- runtime READY.

### D1.2 GENOME

Проверить:
- revision = 22;
- SHA-256 = canonical;
- GENOME load succeeds;
- no mutation of packaged source.

### D1.3 Diagnostics / health

Проверить:
- app version;
- core version;
- Python version;
- runtime phase;
- storage writable;
- secure store available;
- provider labels only.

### D1.4 Session

Создать deterministic test session.

Проверить:
- session_id exists;
- active_session_id enters RuntimeSnapshot;
- turn starts at expected value;
- state equals Python core state.

### D1.5 Test turn

Использовать только deterministic test adapter.

Проверить:
- response exists;
- provider/model metadata correct;
- no network provider is contacted;
- runtime state advances;
- PulseStamp created by runtime.

### D1.6 Keystore

Проверить round-trip:
1. generate random test payload;
2. put into PlatformSecureStore;
3. get;
4. compare exact bytes;
5. delete;
6. verify absence.

Evidence stores only:
- operation success/failure;
- payload size;
- timing;
- safe exception class/message.

Сами bytes и keys не сохраняются.

### D1.7 Storage

Проверить:
- DATA root exists;
- write probe;
- read probe;
- cleanup.

### D1.8 Lifecycle

Наблюдать:
- home/background;
- return to Activity;
- service state;
- runtime snapshot consistency.

Не считать отсутствие process kill во время короткого теста ошибкой.

### D1.9 Controlled process restart

До restart сохранить только safe checkpoint:
- session_id;
- turn;
- pulse;
- genome revision/SHA;
- evidence run id.

После следующего запуска harness обнаруживает checkpoint и выполняет recovery comparison.

Критерий:
- GENOME снова проходит verification;
- runtime стартует;
- состояние не получает несовместимые значения;
- session/turn/pulse либо восстанавливаются, либо documented limitation фиксируется как blocker.

### D1.10 Export

Evidence bundle создаётся во внутреннем app storage и затем экспортируется пользователем.

Предпочтительные механизмы:
- Storage Access Framework / `ACTION_CREATE_DOCUMENT`;
- либо `MediaStore.Downloads` для собственного файла на Android 10+.

Широкий доступ `MANAGE_EXTERNAL_STORAGE` для harness запрещён.

## 6. Evidence bundle

```
kira-device-evidence/
├── manifest.json
├── device.json
├── app.json
├── runtime.json
├── genome.json
├── storage.json
├── keystore.json
├── lifecycle.json
├── recovery.json
├── checks.json
├── events.jsonl
└── README.txt
```

### Security rule

Bundle не содержит:
- passwords;
- API keys;
- identity_secret;
- authority verifier material;
- protected GENOME text;
- private keys;
- SecureStore values;
- raw user messages.

## 7. User procedure

1. Установить APK.
2. Открыть debug evidence screen.
3. Нажать «Запустить полный A0 smoke».
4. Дождаться завершения.
5. Выполнить restart/recovery, если harness отделяет этот шаг.
6. Экспортировать bundle через системный picker в Download.
7. Передать ZIP без изменения файлов внутри.

Для пользователя никаких adb-команд не требуется.

## 8. Acceptance

A0.D1 = ACCEPTED только если:
- startup PASS;
- GENOME PASS;
- diagnostics PASS;
- session PASS;
- deterministic turn PASS;
- Pulse PASS;
- Keystore PASS;
- storage PASS;
- lifecycle observations recorded;
- recovery PASS или явный blocker;
- bundle без секретов;
- результаты проанализированы и отражены в документации.

## 9. Stop conditions

A1 не начинается, если:
- startup нестабилен;
- GENOME hash не совпадает;
- Python bridge падает;
- Keystore не работает;
- runtime state расходится с Python core;
- process recovery теряет критическое состояние;
- evidence содержит секреты.

## 10. Платформенные основания

Для сохранения диагностического файла не требуется полный доступ ко всей файловой системе. Android предоставляет Storage Access Framework и системный picker для выбора места сохранения; собственные файлы в `MediaStore.Downloads` на Android 10+ могут записываться без storage-related permission.

Для будущего production background runtime тип foreground service будет определён отдельным этапом по фактическому use case. Нельзя заранее объявлять `dataSync` бессрочным типом: актуальная документация Android описывает ограничения длительности для `dataSync`/применимых типов и дополнительные ограничения на background work в Android 16.

Официальные источники:
- https://developer.android.com/guide/topics/providers/document-provider
- https://developer.android.com/training/data-storage/shared/media
- https://developer.android.com/develop/background-work/services/fgs/service-types
- https://developer.android.com/develop/background-work/services/fgs/timeout
- https://developer.android.com/develop/background-work/services/fgs/changes
