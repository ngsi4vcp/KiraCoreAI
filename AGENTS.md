# AGENTS.md — platform/linux

Последовательная реализация KiraCoreAI для Linux x64 поверх принятого Core из `main`.

## Старт цикла

1. `G22.txt`
2. документы `main` по `DOCUMENTATION.md`
3. этот `AGENTS.md`
4. `STATUS.md`
5. `ROADMAP.md`
6. `CHECKLIST.md`
7. связанные технические `docs/*`
8. фактический Git/CI

## Границы

В этой ветке находятся desktop host, Linux release/build и Linux-specific проверки.
Общий Core изменяется только через `main`.

Каждый цикл: Core tests → host tests → Linux smoke → documentation sync → final fact check.
Не объявлять parity только по успешной сборке.
