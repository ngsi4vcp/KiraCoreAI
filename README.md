# KiraCoreAI

KiraCoreAI — исполняемое ядро проекта Кира:Ядро.

## Альфа 0.1.0-alpha.1

Цель этой Альфы — получить первый вертикальный пользовательский сценарий:

распаковать архив → START → считать GENOME → открыть DATA/SECRETS → выбрать коннектор → получить актуальный каталог моделей → выбрать модель → запустить рантайм → вести разговор → перезапустить и продолжить.

Целевая среда: Windows 11 x64 и Linux x64.

## Источник генома

Активный runtime-геном читается только из GENOME/genome.txt.

G22.txt в корне — шаблон разработки. Runtime его не загружает.

Текст GENOME/genome.txt — единственный источник истины. Парсер и индексы производны от него.

## Рантайм

GENOME/genome.txt
↓
GenomeLoader
↓
GenomeParser
↓
GenomeValidator
↓
GenomeCompiler / GenomeStore
↓
StateStore + MemoryStore + HistoryStore + ConversationStore
↓
ContextCompiler
↓
PromptRenderer
↓
ModelAdapter
↓
ModelResponse
↓
PulseStamp
↓
Persistence
↓
TerminalHost

## Коннекторы моделей

Alpha предоставляет:

- OpenRouter;
- Google Gemini / Google AI Studio через OpenAI-compatible API;
- LM Studio через локальный OpenAI-compatible API.

Каталог моделей получает runtime через API коннектора. Селектор поддерживает поиск по уже загруженному каталогу с выбором стрелками.

Подробности и официальные контракты API: docs/model-connectors.md.

## Локальные данные

При первом старте автоматически создаётся:

DATA/
├── core_state.json
├── preferences.json
├── sessions/
├── conversations/
├── memory/
└── history/

Секреты хранятся отдельно:

SECRETS/credentials.ini

Файл создаётся автоматически из шаблона и не входит в Git.

## Память

Модель не имеет прямого права записывать активную память.

Новая запись должна пройти состояние candidate, а утверждение выполняется отдельно авторизованным действием.

Это сознательная защита от автоматической фиксации галлюцинаций модели.

## ПУЛЬС

ПУЛЬС теперь формируется runtime, а не моделью.

Формула сохраняется:

series + revision + turn + turn²

Он служит детерминированной меткой активности, сохраняется в состоянии и разговоре и не используется как первичный ключ базы.

## Интерфейс

После запуска доступны:

/help
/status
/genome
/sessions
/memory
/memory candidates
/memory approve <id>
/exit

## Сборка

Для релизной сборки используется PyInstaller.

GitHub Actions собирает отдельные релизные артефакты для Windows x64 и Linux x64. В бинарник не встраивается активный геном: GENOME/genome.txt поставляется рядом с исполняемым файлом.

## Проверки

CI запускает тесты на Ubuntu и Windows для Python 3.11 и 3.12.

Локально:

python -m pip install -e .
python -m unittest discover -s tests -v

## Архитектурные инварианты

Геном ≠ состояние ≠ память ≠ история ≠ разговор ≠ контекст ≠ среда.

Хост не владеет геномом.

Модель не владеет памятью и состоянием.

Изменение генома — отдельная управляемая ревизия.

## Документация

- docs/architecture.md
- docs/runtime.md
- docs/context-model.md
- docs/genome-format.md
- docs/genome-governance.md
- docs/model-connectors.md
- docs/persistence.md
- docs/terminal-alpha.md
- docs/evaluation.md
- docs/roadmap.md
- docs/decisions.md
- docs/language-policy.md
- schemas/
- capsule/KIRA_CORE_CAPSULE.md


## Android Alpha

Android-ветка строится как самостоятельный UI поверх того же KiraCore Contract.

Основной стек:
Kotlin + Jetpack Compose + embedded Python 3.13 + Chaquopy 17.0 + ARM64.

Целевая платформа: Android 9+, обязательная проверка Android 13–17.

Application ID: ru.kiracore.ai.

Android Alpha использует OpenRouter и Google AI Studio/Gemini. LM Studio в Android Alpha не включён.

Android UI русскоязычный и не является переносом терминала.

### Android architecture

Android:
Kotlin → Android Host → KiraRuntime Bridge → Python KiraCore → ModelAdapter.

Кира:Сбор:
SyncProvider → CryptoProvider → encrypted envelopes → private GitHub.

### Android documentation

- `AGENTS.md`
- `docs/android-port-status.md`
- `docs/android-readiness-audit.md`
- `docs/android-a0-plan.md`
- `docs/android-device-evidence-plan.md`
- `docs/android-a1-plan.md`
- `docs/android-development-checklist.md`
- `docs/android-development-plan.md`
- `docs/android-alpha-implementation-plan.md`
- `docs/kira-sync-contract.md`
- `docs/identity-and-user-memory-contract.md`
- `docs/persistence-contract.md`

### Текущий статус Android

A0.D1 фактическое device acceptance закрыт: evidence run `20260930-131718` на vivo V2366HA (Android API 36) завершён со статусом `RECOVERY_OK`. Проверены GENOME rev 22/SHA, diagnostics, session, deterministic turn, Pulse/state, Android Keystore, storage и recovery; lifecycle stop/start зафиксирован как OBSERVED.

Текущий инженерный этап — `A1 Core Parity`, достигнут boundary A1.6 Operation / Recovery. Реализованы typed bridge, session create/list/resume, conversation/memory separation, deterministic turn, Pulse/state parity и persisted operation state с явным `UNKNOWN` для неопределённого model-call. Production reconcile/recovery остаётся A5.

Последний CI на текущем кодовом срезе должен оставаться green до выдачи APK; физический A1 parity smoke ещё не считается пройденным, пока его не выполнить на устройстве.

Временный debug-only Device Evidence Harness используется для фактического evidence и не является production UI.

## Безопасность и переносимость

Привилегированный authority plane отделён от модельного контекста.

Модель получает безопасную семантическую проекцию конституции и runtime capabilities, но не пароль, verifier, ключи или полный текст защищённых секций GENOME.

Кира:Сбор использует versioned encrypted envelopes.

Android и desktop реализуют единый семантический Persistence Contract при различии физических storage backend.

Основные документы Android:

- docs/android-development-plan.md
- docs/android-alpha-implementation-plan.md
- docs/security-architecture.md
- docs/kira-sync-contract.md
- docs/identity-and-user-memory-contract.md
- docs/persistence-contract.md
