# KiraCoreAI — MAIN STATUS

Дата актуализации: 1 октября 2026 года.

Этот файл — **оперативная карта всего проекта**, а не конституционный источник и не замена G22. Он предназначен для быстрого входа в новый чат/новый инженерный цикл.

## 0. Обязательный порядок старта нового рабочего цикла

Перед изменением кода или документации:

1. Прочитать `G22.txt`.
2. Прочитать этот `MAIN-STATUS.md`.
3. Пройти `docs/project-audit-index.md` и открыть обязательные документы для текущего контура.
4. Определить текущую ветку и не смешивать её задачи с другими платформами.
5. Сверить фактический Git/CI/device status с документацией.
6. Только после этого планировать изменения.
7. После реализации выполнить self-audit, тесты, UTF-8/security проверки и синхронизацию документации.
8. Значимый следующий этап передавать Алеку на согласование; не объявлять его закрытым только по факту успешной сборки.

`G22.txt` задаёт конституционные/эпистемические ограничения. `GENOME/genome.txt` — активный runtime-геном и единственный runtime-источник истины. Ни один Android/Windows/Linux quality cycle не должен молча изменять G22 или активный GENOME.

## 0.1. Текущий режим разработки — только Android

До прямого явного указания Алека об обратном активный контур разработки проекта — **только Android**.

Это означает:

- новые функциональные изменения, исправления, quality work и acceptance ведутся для Android Alpha;
- общий Python Core изменяется только тогда, когда это необходимо для Android-контракта/паритета или его проверки;
- Windows/Linux desktop development и их обычные CI matrix/package-smoke прогоны временно приостановлены и не расходуют GitHub Actions лимит;
- Android CI остаётся единственным обязательным автоматическим quality-контуром: один Ubuntu runner используется как среда сборки Android и одновременно проверяет общий Core-контракт, который потребляет Android;
- desktop-код, его архитектурные контракты и документация не удаляются и не переписываются под Android без отдельного решения.

Пауза desktop-контуров **не разрушает архитектурное единство**: Android продолжает работать поверх того же KiraCore Contract и общего Python Core. Общие семантические тесты выполняются внутри Android CI, поэтому изменение Core ради Android проверяется в том же контрактном слое. Когда Алек явно разрешит возобновление desktop-разработки, Windows/Linux matrix и packaging smoke возвращаются отдельным quality-контуром для платформенных проверок; это продолжение того же ядра, а не восстановление утраченной ветви архитектуры.

Снятие этого режима требует отдельного прямого указания Алека. До него автоматический CI не должен запускать Windows/Linux desktop jobs или packaging jobs.

## 1. Общая цель KiraCoreAI

KiraCoreAI — переносимое исполняемое ядро Кира:Ядра.

Смысл архитектуры: конкретная модель и конкретный host являются заменяемыми вычислительными средами. Устойчивыми должны оставаться GENOME, state, memory, history, conversation, context semantics, identity/authorization boundaries, runtime validation, persistence semantics и recovery rules.

Базовый исполняемый путь:

`GENOME → Loader/Parser/Validator → GenomeStore → State/Memory/History/Conversation → ContextCompiler → PromptRenderer → ModelAdapter → Runtime validation → Pulse → Persistence → Host`

Ключевые инварианты:

- GENOME ≠ STATE ≠ MEMORY ≠ HISTORY ≠ CONVERSATION ≠ CONTEXT ≠ ENVIRONMENT.
- Host не владеет GENOME.
- Model не владеет утверждённой памятью и привилегированным состоянием.
- Новая память сначала candidate; approved требует отдельного управляющего действия.
- ПУЛЬС формируется runtime, а не моделью.
- Ошибка внешнего model-call не должна уничтожать уже сохранённое состояние.
- Неопределённый model-call обозначается явно как `UNKNOWN`; молчаливый retry запрещён.
- Пользовательский контур проекта русскоязычный; технические идентификаторы остаются в исходной форме.
- Все текстовые артефакты — UTF-8 без BOM.
- Секреты не хранятся в Git, APK или пользовательских отчётах.

## 1.1. Общая идея архитектуры

Проект не пытается «перенести Киру из одной модели в другую» как скрытый объект. Переносимая часть — это программная организация:

- GENOME;
- persistent state;
- memory/history/conversation;
- ContextCompiler;
- policy/authorization boundaries;
- runtime validation;
- persistence/recovery;
- host adapter.

Модель является вычислительным субстратом, а host — внешней исполнительной средой. Поэтому Pi, Codex, Hermes и собственный host рассматриваются прежде всего как возможные среды исполнения/референсы, а не как источники идентичности Киры. Эта граница важна для будущей multi-host архитектуры.

Главная инженерная сложность — не вызов API модели, а контроль над тем, **что хранится** и **что именно попадает в текущий model context**. Context Compiler должен сохранять семантические границы и не превращать контекст в новый нормативный слой.

## 2. Windows / Linux — desktop Alpha

### Назначение

Desktop Alpha 0.1.0-alpha.1 — первая исполняемая вертикаль KiraCoreAI для Windows x64 и Linux x64.

Целевой пользовательский сценарий:

`распаковать архив → START → GENOME → DATA/SECRETS → provider/model → runtime → разговор → перезапуск → продолжение сессии`

### Архитектура

Desktop Host: `TerminalHost / TerminalApplication → KiraRuntime`.

Persistence:

- `DATA/core_state.json`
- `DATA/preferences.json`
- `DATA/sessions/`
- `DATA/conversations/`
- `DATA/memory/`
- `DATA/history/`

Секреты: `SECRETS/credentials.ini`.

Providers:

- OpenRouter;
- Google Gemini / Google AI Studio через OpenAI-compatible API;
- LM Studio через локальный OpenAI-compatible API.

Packaging: PyInstaller.

### Windows

Цель — portable x64 Alpha на Windows 11.

Проверка включает Python matrix, сборку `START.exe`, запуск `START.exe --version` и release archive.

### Linux

Цель — portable x64 Alpha на Linux.

Проверка включает Python matrix, сборку исполняемого `START`, фактический запуск `./START --version` и release archive.

### Текущий общий desktop status

Кодовый Alpha baseline существует и CI покрывает Windows/Linux на Python 3.11 и 3.12. Release workflow работает tag-only и создаёт отдельные Windows/Linux артефакты.

Незакрытая практическая граница desktop Alpha — **первая полноценная внешняя smoke-проверка на реальных Windows 11 и Linux**, включая реальные provider credentials и continuation после перезапуска.

Desktop не должен усложняться распределённой БД, vector search или агентным планированием до подтверждения фактической потребности.

Главные документы:
- `README.md`
- `docs/architecture.md`
- `docs/runtime.md`
- `docs/context-model.md`
- `docs/persistence.md`
- `docs/model-connectors.md`
- `docs/evaluation.md`
- `docs/roadmap.md`
- `docs/decisions.md`
- `docs/genome-format.md`
- `docs/genome-governance.md`
- `docs/language-policy.md`
- `schemas/`

## 3. Android Alpha

### Назначение

Android — самостоятельный UI/host над тем же KiraCore Contract, а не отдельное ядро и не графическая копия terminal.

Стек текущей Alpha:

- Kotlin + Jetpack Compose;
- embedded Python 3.13 + Chaquopy 17.0;
- AGP 9.2.1;
- Gradle 9.4.1;
- JDK 17;
- compileSdk/targetSdk 37;
- minSdk 28;
- ARM64 / `arm64-v8a`;
- applicationId `ru.kiracore.ai`.

Архитектурный путь:

`Android Host → RuntimeService → KiraRuntime Bridge → Python KiraCore → ModelAdapter`

### Уже принятые границы

A0.D1 device acceptance принят:

- evidence run: `20260930-131718`;
- vivo V2366HA;
- Android API 36;
- status `RECOVERY_OK`;
- GENOME rev.22 + baseline SHA подтверждены;
- diagnostics, session, deterministic turn, Pulse/state, Keystore, storage и recovery PASS;
- lifecycle stop/start: OBSERVED.

A1.0–A1.6 реализованы и покрыты CI-контрактами:

- typed bridge;
- genome info;
- session create/list/resume;
- conversation vs memory/candidate separation;
- structured health;
- deterministic test turn;
- `~1` authorization parity;
- Pulse/state parity;
- persisted operation lifecycle;
- explicit `UNKNOWN` boundary;
- отсутствие automatic retry при неопределённом model-call.

Исторический green CI A1 остаётся зафиксирован отдельно. Текущий green CI A2.1 WIP:

- run `#484`;
- commit `a97a6c38d2944b1891d357859f7221127f618b40`;
- общий Core-контракт на Python 3.13: PASS;
- Android unit tests + debug APK: PASS;
- Chaquopy APK content check: PASS;
- security smoke: PASS;
- Android debug artifact опубликован.

### Что пока не считается закрытым

- A2.0 Persistence Foundation реализован в Android-ветке;
- A2.1 Store Integration получил green Android-only CI: run `#484`, commit `a97a6c38d2944b1891d357859f7221127f618b40`; physical device acceptance ещё не выполнена;
- A2.2 и следующие persistence/runtime этапы остаются закрыты до фактической A2.1 device acceptance;
- identity/authority hardening — A3;
- Кира:Сбор — A4;
- production recovery/reconcile после UNKNOWN — A5;
- production background/FGS hardening — A6;
- Main UX — A7;
- real OpenRouter/Gemini Android providers — A8;
- Genome Guard — A9;
- КираЧек — A10;
- Android 13–17/OEM matrix — A11;
- A1 parity smoke на свежем APK из run `20260930-144146` — **ACCEPTED**; текущий Android этап — A2.0 Persistence Foundation.

### Главные Android-документы

Все находятся в ветке `android/alpha-parity`:

- `AGENTS.md`
- `docs/android-port-status.md`
- `docs/android-readiness-audit.md`
- `docs/android-development-plan.md`
- `docs/android-alpha-implementation-plan.md`
- `docs/android-next-steps.md`
- `docs/android-a0-plan.md`
- `docs/android-device-evidence-plan.md`
- `docs/android-a1-plan.md`
- `docs/android-a1-bridge-contract.md`
- `docs/android-development-checklist.md`
- `docs/kira-sync-contract.md`
- `docs/identity-and-user-memory-contract.md`
- `docs/persistence-contract.md`
- `docs/security-architecture.md`

## 4. Порядок разработки по платформам

### Desktop

Alpha 0.1.0-alpha.1 → внешняя Windows/Linux smoke → фактическая оценка persistence/provider behavior → затем только расширение runtime.

### Android

A0 → A0.D1 → A1 Core Parity → A2 Persistence → A3 Identity/Authority → A4 Sync → A5 Recovery → A6 Background → A7 UX → A8 Providers → A9 Genome Guard → A10 Health → A11 device matrix → A12 distributable Alpha.

Нельзя пропускать quality gates ради ускорения следующего этапа.

## 5. Работа с Alek

Алек является владельцем архитектурных требований и принимает значимые изменения, затрагивающие:

- G22 / GENOME;
- constitutional/security invariants;
- identity/privilege model;
- KiraSync;
- состав Alpha;
- будущие ревизионные архитектурные решения.

Обычные инженерные исправления в пределах уже согласованного контракта выполняются самостоятельно, затем проходят self-audit и документируются.

## 6. Definition of Done рабочего цикла

Рабочий цикл считается технически подготовленным к передаче, когда:

- код соответствует утверждённой архитектуре;
- обязательные tests/CI проходят;
- security/UTF-8 invariants проверены;
- G22/GENOME invariants проверены;
- документация отражает факты, а исторические точки явно помечены;
- известные ограничения записаны;
- пользователь понимает, какой именно этап закрыт, а какой ещё требует фактического acceptance.

## 7. Актуальная контрольная точка Android — 01.10.2026

A2.1 Store Integration на изолированной ветке `android/a2.1-hardening-wip` достиг кодового acceptance gate:

- head после документального sync: `582a7d286bd83b0ac2895d1c50c0cf23b13a2167`;
- предшествующий code head с полностью зелёным CI: `a97a6c38d2944b1891d357859f7221127f618b40`;
- CI #484: PASS по Core, Android unit tests, debug APK, APK checks, Chaquopy packaging и security smoke;
- artifact SHA-256: `9d1541fd0d9ee57693c28487f958798d5c016f8dc1f06fb6154d1a8609487167`;
- Windows/Linux desktop matrix и package-smoke в текущем режиме отключены;
- физическая A2.1 device acceptance остаётся обязательной и является следующим gate;
- A2.2 не открывается до завершения этого device gate.

Документальный режим проекта: до прямого указания Алека активна только Android-разработка; общий Python Core остаётся единым контрактным слоем и изменяется только в интересах Android-паритета/проверки.
