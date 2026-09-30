# Исполняемый слой

Единая точка старта: KiraRuntime.start().

При старте runtime:

1. загружает GENOME/genome.txt;
2. разбирает документ GenomeParser;
3. проверяет его GenomeValidator;
4. строит GenomeRuntimeIndex через GenomeCompiler;
5. помещает неизменяемый снимок в GenomeStore;
6. создаёт StateStore, MemoryStore и HistoryStore;
7. создаёт SessionManager, работающий с тем же снимком генома.

Нормативный путь: GENOME/genome.txt.

G22.txt в корне проекта не участвует в запуске и используется только как шаблон для разработки новой ревизии.

После загрузки выполняется цепочка:

GENOME/genome.txt → parser → validator → compiler → immutable store → state/memory/history → context/session.

GenomeParser отвечает только за синтаксическое извлечение секций.

GenomeValidator отвечает за документные и конституционные инварианты.

GenomeCompiler строит производные индексы по стабильным ID, частям и TARGETS.

GenomeStore удерживает неизменяемый снимок активного генома.

ContextCompiler получает защищённые секции через эти индексы и не выполняет эвристический поиск по Markdown-заголовкам.

Геном не получает API записи из StateStore, MemoryStore или HistoryStore.
