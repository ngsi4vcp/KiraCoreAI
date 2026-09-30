# Исполняемый слой

Единая точка старта продукта — START, который запускает TerminalApplication и KiraRuntime.

При запуске:

1. определяется корень portable-приложения;
2. создаётся DATA;
3. загружается GENOME/genome.txt;
4. парсится и валидируется KIRA-GENOME;
5. строится неизменяемый GenomeStore;
6. восстанавливаются sessions, memory, history и conversations;
7. читается SECRETS/credentials.ini;
8. выбирается connector;
9. получается актуальный каталог моделей;
10. выбирается модель;
11. начинается разговорный runtime.

G22.txt в корне проекта не участвует в runtime.

## После загрузки

ContextCompiler получает только нужные фрагменты отдельных слоёв.

PromptRenderer превращает их в ModelRequest.

ModelAdapter выполняет внешний API-вызов.

Runtime проверяет ModelResponse, записывает ход и формирует PulseStamp.

Модель не генерирует ПУЛЬС.

## Ошибки

Ошибка model-call сохраняется в core_state.json и не должна уничтожать уже сохранённые разговор или состояние.

Сессия останется в статусе running/error для последующего анализа.
