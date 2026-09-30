# Исполняющий слой

Единая точка запуска продукта — START, который запускает TerminalApplication и KiraRuntime.

При запуске:

1. определяется корень portable-приложения;
2. создаётся DATA;
3. загружается GENOME/genome.txt;
4. парсится и валидируется KIRA-GENOME;
5. строится неизменяемый GenomeStore;
6. восстанавливаются сессии, память, история и разговоры;
7. читается SECRETS/credentials.ini;
8. выбирается коннектор;
9. получается актуальный каталог моделей;
10. выбирается модель;
11. начинается разговорный рантайм.

G22.txt в корне проекта не участвует в runtime.

## После загрузки

ContextCompiler получает только необходимые фрагменты отдельных слоёв.

PromptRenderer превращает их в нормализованный ModelRequest.

ModelAdapter выполняет внешний API-вызов.

Рантайм проверяет ModelResponse, записывает ход и формирует PulseStamp.

Модель не генерирует ПУЛЬС.

## Ошибки

Ошибка вызова модели сохраняется в core_state.json и не должна уничтожать уже сохранённые разговор или состояние.

Сессия останется в рабочем состоянии `running/error` для последующего анализа.



## Runtime recovery contract

Runtime state должен переживать process death через каноническую персистентность.

Минимальная state machine:
CREATED → PREPARING → CONTEXT_READY → MODEL_CALL_STARTED → MODEL_CALL_FINISHED/UNKNOWN → VALIDATING → PERSISTING → COMPLETED/FAILED.

UNKNOWN означает, что runtime не может доказать исход внешнего model-call.

После восстановления UNKNOWN нельзя автоматически повторять модельный запрос без reconcile.

## Android runtime boundary

Android использует:
Activity → RuntimeService → PythonRuntime → Persistence.

Activity не является владельцем причинного runtime-состояния.

Foreground service повышает устойчивость runtime, но не является гарантией бессмертия процесса.

## Безопасный runtime

ModelAdapter не получает доступ к identity secrets, sync tokens и физическому storage.

Crypto/Synchronization операции вызываются только через внутренние типизированные runtime API.

UI не может напрямую изменять GENOME или выполнять MergeIdentity.
