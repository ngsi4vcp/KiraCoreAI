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

Текущее Android состояние:
- `RuntimeService` и bridge boundary реализованы;
- A0.D1 device evidence принято на vivo V2366HA / API 36;
- A1.6 operation boundary реализован, включая persisted operation state и explicit UNKNOWN;
- production foreground-service hardening ещё не реализован;
- текущий Android persistence contour — Room/SQLite как canonical physical backend через Android bridge;
- production reconcile/recovery остаётся A5.

Foreground service и production recovery не должны считаться реализованными только из-за наличия `Service` и `START_STICKY`.

A0.D1 отдельно проверяет фактическое поведение текущего service/runtime на vivo. Production background policy реализуется позже после сверки фактических ограничений Android и результатов device evidence.

## Безопасный runtime

ModelAdapter не получает доступ к identity secrets, sync tokens и физическому storage.

Crypto/Synchronization операции вызываются только через внутренние типизированные runtime API.

UI не может напрямую изменять GENOME или выполнять MergeIdentity.


## Безопасность цикла генерации

Перед каждым вызовом ModelAdapter выполняется Pre-Generation Reflection Gate.

Он формирует безопасную семантическую проекцию конституции и текущих прав сессии. Полный текст защищённых секций GENOME в ModelRequest не попадает.

После ModelAdapter выполняется Response Disclosure Guard.

Model output не может самостоятельно активировать privileged операции.


### Актуальная точка персистентности — 01.10.2026

A2.1 подключает Room/SQLite как физический canonical backend через `PersistenceBackend`. Core остаётся доменным authority, Kotlin не дублирует domain semantics.

Device run `20261001-114931` подтвердил process-death recovery, но остановился на diagnostics backend identity. Исправление bridge внесено в `d79ab7d418d0ba41286d69ebd3ec903982affe42`; повторная физическая acceptance обязательна.
