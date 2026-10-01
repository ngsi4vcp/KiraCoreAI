# KiraCoreAI

KiraCoreAI — переносимое ядро Кира:Ядро с единым семантическим Core и отдельными платформенными реализациями.

## Архитектура

- `main` — общий Core и архитектурная база;
- `platform/android` — Android;
- `platform/windows-11` — Windows 11;
- `platform/linux` — Linux;
- `archive/history` — архив.

Начинать работу с `G22.txt`, затем читать `AGENTS.md` и `DOCUMENTATION.md`.

## Core

Общий Python Core, схемы, контракты и Core tests живут в `main`.
Платформа получает принятую версию Core и тестирует связку Core+Platform отдельно.

## Геном

Активный runtime-источник: `GENOME/genome.txt`.
`G22.txt` — конституционный/разработческий документ по правилам проекта.
Текущая ревизия генома: 22.

## Документация

Главная карта: `DOCUMENTATION.md`.
Цель и план: `PROJECT-PLAN.md`.
Целевая архитектура: `PROJECT-ARCHITECTURE.md`.
Целевое поведение: `PROJECT-BEHAVIOR.md`.
Проверки: `PROJECT-CHECKLIST.md`.
Текущее состояние Core: `MAIN-STATUS.md`.

Не используйте архив как источник текущего состояния.

## Статус

В момент реорганизации Android A2.2 имеет реализованный, но ещё не принятый срез. Открыты Room/SQLite rollback proof и отдельная device acceptance.
