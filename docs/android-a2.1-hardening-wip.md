# WIP: усиление A2.1 — Android

Дата: 30 сентября 2026 года.

## Назначение

Эта ветка является изолированным черновым контуром для усиления и проверки A2.1 Store Integration после внесения lifecycle-исправлений debug evidence harness.

Ветка не открывает A2.2 и не означает приёмку A2.1.

## Исходная точка

- branch: `android/a2.1-hardening-wip`;
- базовый commit: `38ce9e3174865d3ade1d404f0d932952c82c6425`;
- активный GENOME: ревизия 22;
- G22.txt и `GENOME/genome.txt` не изменяются;
- A2.1 кодовый baseline: `219c641a6b74526e0774346b35b3dbe912e96246`;
- lifecycle fixes находятся выше этого baseline и ещё не прошли новый green CI.

## Почему ветка создана

Текущий GitHub Actions run #480 на commit `38ce9e3174865d3ade1d404f0d932952c82c6425` создал все ожидаемые jobs, но завершил их до выполнения первого шага. Это не даёт достоверного результата о коде.

Одновременно физическая device-приёмка A2.1 persistence runtime ещё не выполнена.

Поэтому развитие продолжается в режиме controlled hardening, а acceptance остаётся отдельным гейтом.

## Реализованный hardening

### 1. Reopen read-back для persistence backend

A2.1 integration test больше не переиспользует тот же gateway instance после "restart".

Тест теперь:

1. создаёт runtime с Room backend;
2. выполняет deterministic turn;
3. сохраняет conversation, state, history, memory и operation;
4. закрывает первый gateway instance;
5. создаёт новый gateway instance поверх того же durable test fixture;
6. создаёт новый `RoomPersistenceBackend`;
7. заново создаёт `KiraRuntime`;
8. проверяет session/conversation/memory/operation/core-state read-back;
9. проверяет, что после удаления conversation approved memory сохраняется.

Тестовый fixture хранится вне `DATA/`, поэтому проверка отсутствия canonical JSON/JSONL в runtime storage сохраняется.

## Следующий порядок работ

1. Провести self-audit A2.1 store/backend boundaries и lifecycle ownership.
2. Добавлять только локальные hardening-изменения, которые усиливают доказуемость текущего контракта.
3. Не открывать A2.2 Atomic Turn до green CI актуального code head.
4. После green CI получить APK именно с текущего code head.
5. Выполнить физическую A2.1 device acceptance на vivo V2366HA/API 36 через новый debug probe:
   - backend identity = android-room;
   - create/write session + conversation + operation;
   - controlled runtime shutdown;
   - новый Room gateway/runtime;
   - session/state/operation/conversation read-back;
   - Pulse read-back;
   - отсутствие plaintext JSON/JSONL canonical storage;
   - отсутствие известных conversation payloads в Room DB/WAL/SHM;
   - conversation delete != memory delete остаётся отдельной core/integration проверкой.
6. Только после выполнения предыдущих пунктов обновить operational status и открыть A2.2.
## Stop conditions

Работа останавливается и исправляет foundation, если появляется:

- второй persistence source of truth;
- смешанный JSON + Room canonical mode;
- изменение семантики State/Memory/History/Conversation;
- обход runtime для Pulse;
- lifecycle ownership у Activity;
- неявный retry UNKNOWN model-call;
- изменение G22/GENOME.

## Device evidence implementation

Debug-only A2.1 probe добавляет физическую проверку Room-backed runtime без создания долговечных memory fixtures. Он специально не изменяет production memory semantics.

Проверяемый путь:
Room backend → write → shutdown → новый gateway/runtime → read-back.

Отдельно проверяется отсутствие plaintext conversation payload в Room main DB/WAL/SHM. Это evidence-level check; он не заменяет полноценный cryptographic audit.
## Acceptance boundary

Текущий статус:

- A2.1 implementation: реализован;
- A2.1 code acceptance: подтверждён baseline CI #450 на `219c...`;
- lifecycle fixes: реализованы, новый CI ещё не прошёл;
- physical device persistence acceptance: не выполнена;
- A2.2: не открыт.
