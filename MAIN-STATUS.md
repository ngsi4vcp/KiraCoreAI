# MAIN-STATUS

**Дата:** 2026-10-01  
**Назначение:** текущий фактический снимок общей ветки.

## Реорганизация

Рабочая ветка переходит к новой модели:

`main` → общий Core  
`platform/android` → Android  
`platform/windows-11` → Windows 11  
`platform/linux` → Linux  
`archive/history` → история

Текущая миграция выполняется из A2.2 code slice. Старые ветки пока сохраняются до финального audit.

## Core

Канонический общий Core берётся из принятой линии текущего development head. Android A2.2 изменения в общем Python Core должны оставаться воспроизводимыми в main, а platform-specific код не должен попадать в main.

G22/GENOME:
- revision 22;
- blob SHA: `05e2d7bd86047c34103c079fc0a3d9845d471de9`;
- в текущей реорганизации без изменений.

## A2.2

Реализованный срез существует, но не принят.
Открыты:
- физическое доказательство rollback на Room/SQLite;
- отдельная device acceptance A2.2.

## Ограничения

Этот статус не является историческим журналом.
Подробности этапов — в `PROJECT-PLAN.md`, критерии — в `PROJECT-CHECKLIST.md`.
