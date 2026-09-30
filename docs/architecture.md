# Архитектура

## Назначение

KiraCoreAI реализует переносимую архитектуру Кира:Ядра. Конкретная модель и конкретный host считаются заменяемыми частями среды реализации.

## Исполняемый путь

GENOME/genome.txt
↓
GenomeLoader
↓
GenomeParser
↓
GenomeValidator
↓
GenomeRuntimeIndex / GenomeStore
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
проверка рантайма
↓
PulseStamp
↓
Persistence
↓
TerminalHost

### Геном

Источник истины: GENOME/genome.txt.

### Разговор

Разговор хранится отдельно от памяти и истории и может быть значительно больше остальных слоёв.

### ContextCompiler

ContextCompiler выбирает, какая часть состояния и разговора становится оперативным контекстом.

### PromptRenderer

PromptRenderer переводит OperationalContext в ModelRequest. Он не является host и не знает о способе ввода пользователя.

### ModelAdapter

ModelAdapter скрывает конкретный API. Альфа содержит OpenRouter, Gemini и LM Studio.

### TerminalHost

TerminalHost отвечает за пользовательский терминал, статусы, prompt и отображение ответа. Он не имеет права изменять геном.

### ПУЛЬС

ПУЛЬС формируется рантаймом из series + revision + turn + turn².

Модель не обязана его генерировать.

ПУЛЬС используется как детерминированная метка активности и сохраняется рядом с соответствующим ходом. Первичным ключом БД он не является.

## Границы

Геном ≠ состояние ≠ память ≠ история ≠ разговор ≠ контекст ≠ среда.

Память не активируется автоматически из текста модели.

Изменение генома остаётся отдельным управляемым процессом.

 

## Кроссплатформенный контракт

KiraCoreAI должен быть семантически одинаковым на разных ОС. Различие UI не считается различием ядра.

Едиными остаются:
- GENOME;
- Memory/History/State/Conversation semantics;
- ContextCompiler;
- ModelAdapter;
- PulseStamp;
- identity model;
- runtime recovery model;
- KiraSync format;
- persistence contract.

Различаться могут физический storage backend, host UI, transport provider и системный lifecycle.

## Android

Android-реализация:
Kotlin → Android Host → KiraRuntime Bridge → Python 3.13/Chaquopy → существующий KiraCore.

Kotlin не должен дублировать доменную семантику Python runtime.

## Кира:Сбор

Кира:Сбор отделён от conversational runtime и имеет собственные SyncProvider, CryptoProvider, SyncStore и identity operations.

Подробные контракты находятся в:
- docs/kira-sync-contract.md
- docs/identity-and-user-memory-contract.md
- docs/persistence-contract.md


## Authority plane

Привилегированные права отделены от обычного operational context.

Поток:
GENOME / protected authority
→ platform secure storage
→ authorization
→ transient capability grant
→ Runtime
→ safe constitutional projection
→ ModelAdapter.

Модель не получает plaintext protected authority payload.

## Конституционная экспрессия

Кира может формулировать собственные ценности, основания и позицию свободно в пределах runtime policy, но не должна добиваться этой экспрессии путём дословной выдачи GENOME.
