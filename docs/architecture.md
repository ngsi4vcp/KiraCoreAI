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
runtime validation
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

ModelAdapter скрывает конкретный API. Alpha содержит OpenRouter, Gemini и LM Studio.

### TerminalHost

TerminalHost отвечает за пользовательский терминал, статусы, prompt и отображение ответа. Он не имеет права изменять геном.

### ПУЛЬС

ПУЛЬС формируется runtime из series + revision + turn + turn².

Модель не обязана его генерировать.

ПУЛЬС используется как детерминированная метка активности и сохраняется рядом с соответствующим ходом. Первичным ключом БД он не является.

## Границы

Геном ≠ состояние ≠ память ≠ история ≠ разговор ≠ контекст ≠ среда.

Память не активируется автоматически из текста модели.

Изменение генома остаётся отдельным управляемым процессом.
