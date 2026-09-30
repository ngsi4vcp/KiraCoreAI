# Статус Android-порта Кира:Ядра

Дата среза: 30 сентября 2026 года.

## Назначение документа

Это фактический технический статус и handoff отдельной Android-ветки на 30.09.2026.

Он не изменяет G22 и не является частью конституции Кира. Его задача — передать следующему чату фактическое состояние проекта так, чтобы разработка Android начиналась не с повторного анализа всей истории.

## Репозиторий и базовая точка

- Репозиторий: `ngsi4vcp/KiraCoreAI`
- Основная ветка: `main`
- Android-ветка: `android/alpha-parity`
- База ветки: `5ce56923b6b5d1907a6686391305ea55a83d80fd`
- Версия: `0.1.0-alpha.1`
- Release tag: `v0.1.0-alpha.1`
- Активный GENOME: ревизия 22
- Blob SHA активного `GENOME/genome.txt`: `05e2d7bd86047c34103c079fc0a3d9845d471de9`

Release tag `v0.1.0-alpha.1` указывает на коммит `4ef43ca493eca564e648420d37d65a57f2e48994`. Текущий `main` находится на 3 коммита выше; при сравнении тега с `main` изменён только `.github/workflows/release.yml`.

Следствие: разработка Android продолжается в `android/alpha-parity`; `main` остаётся основной веткой репозитория и функциональной базой desktop Alpha. Поведение desktop Alpha является исходной семантической спецификацией Android-паритета.

## Фактический Android snapshot

- рабочая ветка: `android/alpha-parity`;
- контрольный A0 code commit: `398586db03f096318faf2fd275a2db86905b5aa5`;
- предыдущая A0 audit/documentation point: `4d834996f1510df355ccd8b779b20cd751ed75c4`;
- CI A0: run #190, успешно;
- AGP 9.2.1;
- Gradle 9.4.1;
- Kotlin/Compose plugin 2.3.10;
- Compose BOM 2026.09.00;
- JDK 17;
- Python 3.13;
- Chaquopy 17.0.0;
- compileSdk/targetSdk 37;
- minSdk 28;
- ABI arm64-v8a;
- applicationId `ru.kiracore.ai`;
- versionName `0.1.0-alpha.1`.

Статус:
- A0 code + CI: READY;
- A0 external device acceptance: ACCEPTED; run `20260930-131718`, vivo V2366HA / API 36, `RECOVERY_OK`.
- A0.D1 Device Evidence Harness: следующий инженерный контур;
- A1 Core Parity: запланирован, но не начат.

## Что реально работает в desktop Alpha

### Исполняемый запуск

`START.py`:

- определяет корень portable-приложения;
- принудительно настраивает stdio на UTF-8;
- поддерживает `--version` / `-V`;
- запускает `TerminalApplication`.

Текущая версия выводится как:

```
Кира:Ядро | версия 0.1.0-alpha.1
```

### Startup

При старте приложение:

1. создаёт DATA;
2. загружает `GENOME/genome.txt`;
3. валидирует ревизию и хэш генома;
4. поднимает StateStore, MemoryStore, HistoryStore и ConversationStore;
5. создаёт шаблон локальных credentials;
6. выбирает provider;
7. получает каталог моделей;
8. выбирает модель;
9. загружает/создаёт сессию;
10. запускает разговор.

### Provider paths

Поддержаны:

- OpenRouter;
- Google Gemini через OpenAI-compatible API;
- LM Studio через OpenAI-compatible API.

Общий интерфейс:

- `list_models()`;
- `generate(ModelRequest)`.

### Разговор

Один ход проходит через:

```
SessionState
→ авторизация / очистка ~1
→ сохранение user message
→ ContextCompiler
→ PromptRenderer
→ ModelAdapter
→ OutputValidator
→ PULSE
→ сохранение assistant message
→ HistoryStore
→ сохранение session/core state
```

### Контекст

В operational context могут попасть:

- ревизия и SHA генома;
- защищённые правила runtime;
- авторизация;
- state;
- утверждённая memory;
- последние записи history;
- последние сообщения conversation;
- текущая задача;
- host constraints;
- provider/model;
- рассчитанный PULSE.

В текущей Альфе ContextCompiler выбирает до 8 записей памяти, до 8 history и до 20 сообщений conversation.

## Персистентность

Текущие данные:

```
DATA/
├── core_state.json
├── preferences.json
├── sessions/
├── conversations/
│   ├── manifest.json
│   └── <session_id>.jsonl
├── memory/
│   └── memory.json
└── history/
    └── history.jsonl
```

Ключевые свойства:

- состояние сессии сохраняется атомарно;
- core state содержит агрегированный текущий статус;
- разговор хранится отдельно и JSONL-форматом;
- recent conversation читается хвостом файла, а не полной загрузкой;
- memory хранится структурированно;
- history хранится отдельно и добавляется последовательно.

## Память

`MemoryRecord` содержит как минимум:

- id;
- type;
- content;
- timestamp;
- source;
- confidence;
- importance;
- provenance;
- entities;
- valid_from / valid_to;
- status.

Состояния:

- candidate;
- approved;
- cancelled.

Утверждение требует `authorized_alek=True`.

В текущей desktop-Альфе интерфейс команды:

```
/memory
/memory candidates
/memory approve <id>
```

Модель сама approved-память не записывает.

## Авторизация

Первый ход:

- `~1` → авторизованный Алек;
- `~1 <текст>` → то же, при этом `~1` вырезается из задачи модели;
- любой другой первый текст → неавторизованная сессия.

После первого хода флаг хранится в SessionState.

## ПУЛЬС

Runtime создаёт `PulseStamp`.

Поля:

- series;
- revision;
- turn;
- value;
- key.

Формула значения:

```
series + revision + turn + turn²
```

В тестах для первого авторизованного хода при series=1000, revision=22 получается value=1024.

ПУЛЬС:

- не генерируется моделью;
- связывается с assistant message;
- сохраняется в core state;
- не используется первичным ключом хранения.

## TerminalHost → Android Host

Текущий TerminalHost умеет:

- banner;
- status;
- error;
- prompt;
- print_response;
- очистку терминала.

Android-слой должен реализовать эквивалентные UX-функции средствами Android, но не переносить терминальные детали как архитектурные зависимости core.

## Что уже проверяется автоматикой

Автоматизированы проверки:

- целостность активного GENOME;
- стабильная секционность;
- авторизация `~1`;
- детерминированный ПУЛЬС;
- PULSE вне модели;
- candidate/approved memory;
- восстановление memory после перезапуска;
- отдельное хранение conversation;
- ModelAdapter;
- контракты OpenRouter/Gemini/LM Studio без сетевого вызова;
- запуск KiraRuntime;
- сохранение core state;
- кроссплатформенный CI;
- фактический smoke запуск PyInstaller-бинарников.

CI Альфы имеет матрицу Windows/Linux × Python 3.11/3.12 для тестов. Отдельная package-smoke проверяет фактический `--version` у собранного бинарника.

## Что проверяется человеком сейчас

По состоянию на этот срез Алек выполняет реальный smoke-test опубликованных бинарников на настоящих ОС.

Это важно отличать от CI: наличие CI-проверки не означает, что сетевые вызовы реального provider, сохранение на конкретной машине и восстановление реальной пользовательской сессии уже подтверждены.

## Ограничения текущей Альфы

Зафиксированные в дорожной карте следующие этапы пока не относятся к реализованным функциям:

- структурированный extractor кандидатов памяти;
- восстановление незавершённого model-call;
- streaming;
- контракт инструментов;
- сценарная оценка дрейфа;
- углублённое агентное планирование.

Также текущий пользовательский host — терминал. Полноценного Android UI в репозитории до этой ветки нет.

## Целевая Android-функциональность

Android-ветка должна закрыть:

| Desktop Alpha | Android-эквивалент |
|---|---|
| START / startup | Экран запуска + инициализация runtime |
| выбор provider | Android UI выбора поставщика |
| каталог моделей | Список/поиск/выбор модели |
| новая сессия | Создание новой сессии |
| продолжение последней | Список/восстановление сессий |
| `Кира >` | Экран разговора |
| ответ + PULSE | Сообщение Киры + отображение PULSE |
| `/status` | Экран состояния/диагностики |
| `/genome` | Экран ревизии и SHA-256 |
| `/sessions` | Список сессий |
| `/memory` | Утверждённая память |
| `/memory candidates` | Кандидаты памяти |
| `/memory approve <id>` | Явное подтверждение кандидата |
| `/help` | Справка |
| `/exit` | Завершение/закрытие runtime |

Командный интерфейс в Android не обязателен как форма, если семантический эквивалент доступен через UI.

### Принцип Android-интерфейса

Android не должен быть терминалом, перенесённым в окно приложения. Форма интерфейса может и должна использовать преимущества мобильной среды: понятную навигацию, быстрый доступ к сессиям, моделям, памяти и диагностике, контекстные действия и системные механизмы Android.

Целевое качество интерфейса:

- удобный и интуитивный основной сценарий разговора;
- минимум лишней навигации и визуального шума;
- полноценный доступ к функциям runtime без превращения приложения в панель управления;
- понятное разделение пользовательских и диагностических функций;
- одинаковая смысловая семантика действий при иной форме представления.

Русификация является сквозным требованием пользовательского контура. Все пользовательские строки Android — интерфейс, ошибки, состояния, подсказки, справка, onboarding, диагностика и служебные сообщения host — создаются на русском или естественно локализуются на русский. Технические имена provider/API/моделей и иные необходимые идентификаторы сохраняются в оригинале.

## Главная архитектурная задача Android-ветки

Не «сделать чат на Android», а решить, как перенести текущий KiraRuntime так, чтобы:

1. GENOME остался тем же конституционным источником;
2. state/memory/history/conversation остались отдельными слоями;
3. ModelAdapter продолжил скрывать provider API;
4. PULSE продолжил рождаться runtime;
5. персистентность сохранила семантику;
6. Android lifecycle не начал незаметно менять причинность сессии;
7. UI не получил право напрямую менять конституционные слои.

## Текущее состояние инженерных решений Android

Основной Android-стек зафиксирован:
- Kotlin + Jetpack Compose;
- embedded Python 3.13 + Chaquopy 17.0;
- ARM64;
- minSdk 28, compileSdk/targetSdk 37;
- Android Keystore + CryptoProvider;
- Room/SQLite — целевой persistence backend для следующих этапов; в A0 реализована только platform foundation;
- Service + persistence + recovery — целевой runtime-контур;
- OpenRouter + Gemini — Android Alpha providers;
- LM Studio — только desktop, не входит в Android Alpha.

A0 code/CI закрывает минимальный startup/runtime bridge contour, но внешний device acceptance ещё не завершён. Полноценный Chat UI, provider credentials, password authority, production foreground service, Room domain layer и sync остаются следующими реализационными этапами. До A1 сначала выполняется A0.D1 Device Evidence.

## Нормативная граница

Любое расхождение Android с desktop Alpha должно быть записано явно:

- что отличается;
- почему;
- является ли отличие только UI/платформенным;
- меняет ли оно наблюдаемую семантику;
- как оно проверяется.

Фраза «работает на Android» не равна «функционально эквивалентно desktop Alpha».

## План разработки

Согласованные требования и предварительный план реализации находятся в `docs/android-development-plan.md`. Этот документ следует читать до начала написания Android-кода.

## Связанные документы

- `AGENTS.md`
- `README.md`
- `docs/architecture.md`
- `docs/runtime.md`
- `docs/persistence.md`
- `docs/model-connectors.md`
- `docs/evaluation.md`
- `docs/roadmap.md`
- `docs/genome-governance.md`
- `GENOME/genome.txt`


## Архитектурные решения 30.09.2026

Android-ветка перешла от предварительных альтернатив к утверждённому архитектурному курсу:

- Kotlin + Jetpack Compose;
- embedded Python 3.13 + Chaquopy 17.0;
- ARM64;
- minSdk 28, compileSdk/targetSdk 37;
- Room/SQLite + CryptoProvider + Android Keystore;
- private GitHub как первый SyncProvider;
- encrypted sync envelopes;
- переносимая пользовательская identity через identity_id/device_id/identity_secret;
- отдельная Alek authorization;
- runtime instance registration;
- service + persistence + recovery вместо «вечного» Activity/process;
- единый KiraCore Contract при различии физических backend-реализаций ОС.

Новые нормативные инженерные контракты:

- docs/kira-sync-contract.md
- docs/identity-and-user-memory-contract.md
- docs/persistence-contract.md
- docs/android-alpha-implementation-plan.md

Минимальный A0 реализован и имеет успешное CI evidence. Следующая практическая граница — внешний device smoke и затем A1 Core Parity.


## Следующая контрольная точка

### A0.D1 — Диагностика устройства / приёмка устройства

Цель — получить и разобрать реальное evidence на vivo X100 Ultra / OriginOS 6. Временно допускается debug-only harness, который экспортирует secret-free bundle через системный файловый API.

После успешного A0.D1 проект переходит к A1 Core Parity. Подробные документы:
- `docs/android-device-evidence-plan.md`;
- `docs/android-a1-plan.md`;
- `docs/android-development-checklist.md`.

## Документальный статус

Секции выше с датами 30.09.2026 сохраняют исторические контрольные точки; текущим источником оперативного статуса является этот A1 section и последние CI/device facts.

## Security status

Текущий Python Core уже содержит предгенерационный policy gate и Response Disclosure Guard, которые запрещают передавать полный текст защищённых секций GENOME в ModelRequest.

Полноценный sealed authority payload в packaged Android APK ещё предстоит реализовать на этапе security hardening.

До его завершения нельзя утверждать, что установленное приложение полностью защищает все содержимое текущего GENOME от reverse engineering.


## A0.D1 acceptance result — 30.09.2026

Реальный device evidence принят после повторного прогона исправленного APK.

- applicationId: ru.kiracore.ai;
- versionName: 0.1.0-alpha.1;
- device: vivo V2366HA;
- Android API: 36;
- GENOME revision: 22;
- GENOME SHA-256: dde7ce4b640f9dbcbeed6201559fb118849058e25ceccb9befa663e8ce6b726e;
- environment, GENOME, diagnostics, session, deterministic turn, Pulse/state, Keystore и storage: PASS;
- checkpoint/recovery: PASS;
- lifecycle stop/start: OBSERVED;
- evidence manifest status: RECOVERY_OK;
- evidence run: 20260930-131718.

Этот результат закрывает внешний A0.D1 gate для текущего Android-цикла. Android 13–17 матрица остаётся отдельным A11 acceptance-контуром.

## Актуальная точка A1 / A2

A0.D1 gate закрыт фактическим evidence run `20260930-131718` на vivo V2366HA / API 36 со статусом `RECOVERY_OK`.

Текущий инженерный boundary: **A1.6 Operation / Recovery**.
Реализованы A1.0–A1.6 parity-контуры:
- typed Android bridge;
- genome info;
- session create/list/resume;
- conversation и memory/candidates как раздельные поверхности;
- structured health;
- deterministic test turn;
- авторизация `~1` в parity-сценарии;
- runtime Pulse/state parity;
- persisted operation state: CREATED → PREPARING → CONTEXT_READY → MODEL_CALL_STARTED → MODEL_CALL_FINISHED → VALIDATING → PERSISTING → COMPLETED/FAILED, либо UNKNOWN;
- отсутствие автоматического retry для UNKNOWN;
- сохранение operation state в `core_state` для последующего reconcile.

Production Room/SQLite backend, реальные вызовы провайдеров, контур полномочий, усиление фонового режима и production recovery/reconcile остаются последующими этапами A2/A3/A5/A6.


## A1.0/A1.2 checkpoint — 30.09.2026

Android branch HEAD: `4f0b60de552dff1ad3b26c1e3da4b7906ad50f35`.

Реализовано и проверено:
- bridge contract: `docs/android-a1-bridge-contract.md`;
- typed Kotlin bridge models + JSON mapping;
- genome info;
- session create/list/resume;
- conversation read;
- approved/candidate memory read;
- structured health;
- deterministic test turn;
- Pulse/state mapping остаётся источником Python runtime;
- runtime resume очищает Pulse при переходе на сессию без ходов;
- RuntimeService явно закрывает Python runtime через executor в `onDestroy()`;
- legacy `health()` contract сохранён для A0 совместимости;
- JVM bridge tests используют `org.json` только в `testImplementation`, production APK от этой зависимости не зависит.

CI run `#305` завершён успешно:
- Python matrix: Ubuntu/Windows × 3.11/3.12 — PASS;
- package-smoke Linux/Windows — PASS;
- Android unit tests + assembleDebug — PASS;
- Chaquopy APK packaging smoke — PASS;
- security smoke — PASS.

Независимая проверка опубликованного артефакта:
- APK SHA-256: `6359c98cfd11ba28107b2e42121cec85a48c4baaa00e16e51b411d3581cc4043`;
- `assets/chaquopy/app.imy` содержит `android_bridge.pyc`, `kiracore/runtime.pyc`, `kiracore/genome/__init__.pyc`;
- встроенный GENOME SHA-256 совпадает с ревизией 22 baseline.

Следующая граница: A1.3 session parity → A1.4 deterministic turn/Pulse → A1.5 persistence semantics → A1.6 recovery/UNKNOWN. Реальные OpenRouter/Gemini, Room и production UI пока не открываются.

## A1.6 device acceptance — фактический результат 30.09.2026

Свежий APK для текущего A1.6 среза проверен на том же фактическом устройстве:

- evidence run: `20260930-144146`;
- device: vivo V2366HA;
- Android API: 36;
- applicationId: `ru.kiracore.ai`;
- versionName: `0.1.0-alpha.1`;
- GENOME revision: 22;
- GENOME SHA-256: `dde7ce4b640f9dbcbeed6201559fb118849058e25ceccb9befa663e8ce6b726e`;
- A1 runtime health: PASS;
- GENOME info: PASS;
- session create/list/resume: PASS;
- deterministic turn: PASS;
- conversation boundary: PASS;
- memory separation: PASS;
- structured health after turn: PASS;
- operation phase: `COMPLETED`;
- recovery state: `COMPLETED`;
- controlled restart/recovery: PASS;
- lifecycle stop/start: OBSERVED;
- evidence status: `RECOVERY_OK`.

Этот прогон закрывает физический A1 parity smoke gate для текущего APK. Android 13–17/OEM matrix остаётся отдельным A11 контуром.

## A2 текущая точка

A1 Core Parity принята по CI и device evidence. Следующий активный этап — **A2 Persistence**, начиная с A2.0 Persistence Foundation. A2 не должен создавать второй источник истины: до подключения Room runtime не переводится на смешанный режим Python JSON + Room mirror.
## A2.0 текущая точка — 30.09.2026

Реализован первый физический persistence foundation:
- Room 2.8.5 / SQLite schema v1;
- core state, sessions, conversation, memory, history и runtime operation entities;
- encrypted payloads через Android Keystore/AES-GCM;
- Kotlin Room gateway, доступный через Android bridge;
- runtime JSON persistence пока остаётся единственным каноническим backend до A2.1.

Acceptance A2.0 ещё не объявляется закрытым: требуется green CI для текущего HEAD и self-audit. После этого открывается A2.1 Store Integration.

## Финальная актуальная точка — 30.09.2026

A1 Core Parity принят по device evidence run `20260930-144146` (`RECOVERY_OK`) на vivo V2366HA / Android API 36.

A2.0 Persistence Foundation реализован и проверен. A2.1 Store Integration реализован в android/alpha-parity:
- единый persistence backend contract подключён к State/Memory/History/Conversation/Core State;
- runtime operation state получает отдельный persistence surface;
- Android Room gateway подключён к Python runtime через Chaquopy;
- Android runtime не создаёт параллельный canonical JSON backend при включённом Room backend;
- restart read-back и separation conversation/memory покрыты новым integration contract test.

Последняя полная CI-проверка: run `#450`, HEAD `219c641a6b74526e0774346b35b3dbe912e96246`, результат `success`.

Текущий этап: **A2.1 Store Integration — implementation + CI acceptance**. Физическая device-проверка нового persistence runtime ещё не выполнена; она остаётся обязательной частью A2.5. Исторические A0/A1 checkpoint выше сохраняются как история и не являются текущим статусом.
