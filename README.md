# KiraCoreAI

## Старт нового рабочего цикла

Перед чтением исходников и изменением кода:

1. `G22.txt`;
2. `MAIN-STATUS.md` — актуальная карта всего проекта;
3. `docs/project-audit-index.md` — обязательный маршрут self-audit;
4. `AGENTS.md` текущей ветки, если он есть;
5. затем документация и код конкретной платформы.

Исторические исследовательские файлы и ранние шаблоны не являются источником текущего статуса.\n
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
