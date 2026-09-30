КИРА:ЯДРО — АЛЬФА

1. Распакуйте архив целиком.
2. Не перемещайте отдельно START и GENOME.
3. Запустите:
   Windows: START.exe
   Linux:   ./START

При первом запуске Кира автоматически создаст:
- DATA/ — состояние, сессии, память, историю и диалоги;
- SECRETS/credentials.ini — локальный файл секретов.

Перед подключением OpenRouter или Google Gemini впишите ключ в соответствующую секцию SECRETS/credentials.ini.

LM Studio может работать без удалённого ключа. По умолчанию:
http://localhost:1234/v1

Команды:
 /help
 /status
 /genome
 /sessions
 /memory
 /memory candidates
 /memory approve <id>
 /exit

Секреты не должны попадать в Git, логи или снимки проекта.
