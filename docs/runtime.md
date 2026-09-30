# Исполняемый слой

Runtime загружает активный геном через GenomeLoader.load_active().

Нормативный путь: GENOME/genome.txt.

G22.txt в корне проекта не участвует в запуске и используется только как шаблон для разработки новой ревизии.

После загрузки выполняется цепочка:

текст → parser → validator → compiler → immutable store → context/session.

GenomeParser отвечает только за синтаксическое извлечение секций.

GenomeValidator отвечает за документные и конституционные инварианты.

GenomeCompiler строит производные индексы по стабильным ID, частям и TARGETS.

GenomeStore удерживает неизменяемый снимок активного генома.

ContextCompiler получает защищённые секции через эти индексы и не выполняет эвристический поиск по Markdown-заголовкам.

Геном не получает API записи из StateStore, MemoryStore или HistoryStore.
