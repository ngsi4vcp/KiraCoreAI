# AGENTS.md — platform/android

## Обязательный старт

1. Прочитать `G22.txt`.
2. Прочитать документы `main` согласно его `DOCUMENTATION.md`.
3. Прочитать этот `AGENTS.md`.
4. Прочитать `STATUS.md`, `ROADMAP.md`, `CHECKLIST.md`.
5. Прочитать только те технические `docs/*`, которые указаны в `DOCUMENTATION.md` и связаны с текущей задачей.
6. Проверить фактический HEAD, Core-версию, дерево Android и последний CI/device evidence.

## Роль ветки

Это основная последовательная Android-ветка.

Здесь разрешены:
- Android host/UI;
- Android lifecycle;
- Android secure storage;
- Android persistence adapter;
- Android-specific tests/build;
- Android documentation and release tooling.

Общий Python Core изменяется не здесь. Если нужен новый Core contract или Core behavior, сначала изменить `main`, проверить его Core-тестами и только затем обновить эту ветку.

## Фактическое состояние

Текущая база перенесена с `android/a2.2-atomic-turn-wip`.
A2.1 принят.
A2.2 имеет реализованный срез, но ещё не принят.

Открыты:
- физический Room/SQLite rollback proof;
- отдельная A2.2 device acceptance.

## Рабочий цикл

Контекст → фактический Git → расхождения → план цикла → один шаг → самопроверка → следующий шаг → quality pass → документационная синхронизация → повторная сверка → отчёт.

## Статусы

Пользоваться единой шкалой проекта:
`ПЛАНИРУЕТСЯ → В РАЗРАБОТКЕ → РЕАЛИЗОВАНО → ПРОВЕРЕНО → ПРИНЯТО → ВЫПУЩЕНО`

Не писать «принято», если есть только сборка или contract test.

## Документы ветки

- `STATUS.md` — фактический текущий срез;
- `ROADMAP.md` — Android-план;
- `CHECKLIST.md` — критерии и их состояние;
- `README.md` — краткий вход и текущий release/pre-release/test-release;
- `docs/*` — специализированные Android-контракты и история решений.

Старые `docs/android-*.md` при наличии используются только как совместимость/справочный слой; канонический текущий статус находится в корне.
