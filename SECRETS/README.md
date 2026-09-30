# Секреты

Основной локальный файл: SECRETS/credentials.ini.

Он создаётся автоматически при первом запуске.

Секции:
- openrouter — ключ OpenRouter;
- gemini — ключ Google AI Studio / Gemini API;
- lm_studio — локальный OpenAI-совместимый endpoint LM Studio.

credentials.ini не должен попадать в Git.

Ключи читаются только runtime-коннектором и не включаются в диагностические сообщения.
