# Коннекторы моделей — Альфа

Ядро использует единый ModelAdapter.

Доступны три коннектора.

## OpenRouter

Используется API по пути `/api/v1`.

Ключ хранится в SECRETS/credentials.ini в секции openrouter.

Каталог моделей загружается при подключении через API, после чего терминальный селектор фильтрует его по мере ввода. OpenRouter документирует GET /api/v1/models и POST /api/v1/chat/completions. citeturn752101search6turn752101search1

## Google Gemini

Используется OpenAI-совместимый интерфейс API Gemini. Один ключ Google AI Studio позволяет получить каталог моделей и отправлять chat completions через совместимый endpoint. Google документирует совместимый base URL и models.list. citeturn752101search4turn752101search2

## LM Studio

Используется локальная конечная точка, совместимая с OpenAI API.

По умолчанию: http://localhost:1234/v1

Каталог моделей: `GET /v1/models`.
Генерация: `POST /v1/chat/completions`.

LM Studio прямо документирует эти конечные точки. citeturn317357search0turn317357search3

## Общий контракт

ModelCatalogItem
↓
ModelRequest
↓
ModelResponse

Конкретная реализация API не должна проникать выше слоя коннектора.
