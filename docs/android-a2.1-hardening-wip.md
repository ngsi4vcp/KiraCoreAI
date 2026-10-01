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
- текущий WIP head после hardening: `12041e49855e544ee10ac057330ce914ca15c558`.

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

Последняя попытка CI: run #481, head `12041e49855e544ee10ac057330ce914ca15c558`, attempt 2. Все five jobs завершились `failure` без шагов (`steps=[]`) за несколько секунд. Это infrastructure/runner blocker, а не результат выполнения тестов.

Текущий статус:

- A2.1 implementation: реализован;
- A2.1 code acceptance: подтверждён baseline CI #450 на `219c...`;
- lifecycle fixes: реализованы, новый CI ещё не прошёл;
- physical device persistence acceptance: не выполнена;
- A2.2: не открыт.


## A2.1 CI — 01.10.2026

После исправления integration test и перевода обязательного CI в Android-only контур актуальный WIP head получил полностью зелёный run **#484**:

- commit: `a97a6c38d2944b1891d357859f7221127f618b40`;
- общий Core-контракт на Python 3.13: PASS;
- Android unit tests + debug APK: PASS;
- APK existence check: PASS;
- Chaquopy packaging smoke: PASS;
- security smoke: PASS;
- диагностический APK опубликован;
- desktop Windows/Linux matrix и package-smoke в этом run не запускались.

Artifact: `kira-android-a2.1-debug-a97a6c38d2944b1891d357859f7221127f618b40`, SHA-256 `9d1541fd0d9ee57693c28487f958798d5c016f8dc1f06fb6154d1a8609487167`.

Исправление теста намеренно использует только публичный `PersistenceBackend`/adapter-контракт и не расширяет production semantics ради тестовой фикстуры.

Следующая обязательная граница A2.1 — физическая device acceptance на актуальном APK: Room backend identity, write → shutdown/restart → read-back, разделение Conversation/Memory и отсутствие canonical JSON/JSONL/plaintext persistence. A2.2 до этой проверки не открывается.


## Фактическая проверка устройства — 01.10.2026

Пользовательский прогон debug APK зафиксирован в коммите `e5d173acf14b90632a23393075723ec06e656c72` ветки `android/alpha-parity`.

Run `20261001-114931` на vivo V2366HA / Android API 36 показал:
- process-death recovery завершился `RECOVERY_OK`;
- GENOME, session/state и ПУЛЬС восстановлены;
- A2.1 persistence smoke остановился на `backend identity`;
- `persistence_backend` не вернулся из Kotlin diagnostics.

Причина: Python diagnostics формировал `persistence_backend`, но Kotlin bridge не переносил это поле во внешний diagnostics object.

Исправление внесено в `d79ab7d418d0ba41286d69ebd3ec903982affe42`. Оно требует нового green CI и нового APK; A2.1 device acceptance пока не закрыта. A2.2 остаётся закрытым.


## Финальный кодовый checkpoint — 01.10.2026

- code head: `b52d2be10a0f31a6cb41f1c17d6b973821298502`;
- CI: run `#495`, полный Android-only PASS;
- artifact: `kira-android-a2.1-debug-b52d2be10a0f31a6cb41f1c17d6b973821298502`;
- artifact SHA-256: `eb5825dd5b5ee6f420c083212d2b9e9aef4b9b784ca9e601ba8e751100eb1974`;
- APK SHA-256: `e9e26ab01086f2c05d7cd5f04ec77f8b3baf8ef85d34af4a3553f8cd92c83f11`;
- physical A2.1 acceptance: не закрыта; требуется повторный прогон на vivo V2366HA / Android API 36.
