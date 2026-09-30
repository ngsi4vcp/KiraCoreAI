# Коннекторы моделей Alpha

Ядро использует единый ModelAdapter.

Доступны три коннектора.

## OpenRouter

Используется API /api/v1.

Ключ хранится в SECRETS/credentials.ini в секции openrouter.

Каталог моделей загружается при подключении через API, после чего терминальный селектор фильтрует его во время ввода. OpenRouter документирует GET /api/v1/models и POST /api/v1/chat/completions. citeturn752101search6turn752101search1

## Google Gemini

Используется OpenAI-совместимый интерфейс Gemini API. Один ключ Google AI Studio позволяет получить каталог моделей и отправлять chat completions через совместимый endpoint. Google документирует совместимый base URL и models.list. citeturn752101search4turn752101search2

## LM Studio

Используется локальный OpenAI-совместимый endpoint.

По умолчанию: http://localhost:1234/v1

Каталог: GET /v1/models.
Генерация: POST /v1/chat/completions.

LM Studio прямо документирует эти endpoints. citeturn317357search0turn317357search3

## Общий контракт

ModelCatalogItem
↓
ModelRequest
↓
ModelResponse

Конкретный API не должен проникать выше слоя connector.
