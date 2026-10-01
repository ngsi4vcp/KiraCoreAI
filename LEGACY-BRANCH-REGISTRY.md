# Реестр веток и контрольных точек реорганизации

Контрольная точка: 2026-10-01.

## Новая постоянная структура

| Ветка | Текущий HEAD | Роль |
|---|---|---|
| `main` | `5d720bc769dca481c3cb4e208e8717c74e48b0b3` | общий Core и архитектура |
| `platform/android` | `a6a41f2515a2b8ec7aea9e596d3cb75bf2cf81c7` | Android |
| `platform/windows-11` | `d8c02b5fad0720239042eadebbaeece7c3b9b1d0` | Windows 11 |
| `platform/linux` | `e32fdbe65e7b35f7d2997ae40f47fe1c9e0031f6` | Linux |
| `archive/history` | обновляется самим архивом | история |

## Старые ветки

| Старая ветка | HEAD на момент миграции | Назначение |
|---|---|---|
| `main` | `d0a1fde148077c219ee89727ec0ea6128b9bd506` | прежняя общая ветка |
| `android/alpha-parity` | `7aff9d700e3c67fea7f8e6f2258546d45f94e658` | Android parity/evidence |
| `android/a2.1-hardening-wip` | `21fe369ba2281fb56b88fde7996c5801eb5af2f9` | A2.1 hardening |
| `android/a2.2-atomic-turn-wip` | `0bdb8f1cd0b1af415d1e07cfd2bb1acb04ff376b` | A2.2 implementation slice |
| `draft/core-foundation` | `8bacb8b171c7204b6849181ed36b02e99b2db66b` | исторический Core draft |

## Контрольная архивная точка

Много-родительская Git-точка:

`cd82719dd97bb9b3767c6ece2c98863ce2081e60`

В неё включены родительские связи с новой структурой и всеми старыми значимыми HEAD. Это сохраняет причинность после будущего удаления branch refs.

## Аудит переноса

Проверено:
- G22/GENOME SHA совпадают во всех новых рабочих ветках и архиве;
- `main` не содержит Android или desktop host;
- `platform/android` содержит Android host и не содержит desktop host;
- `platform/windows-11` и `platform/linux` содержат desktop host и не содержат Android;
- глобальные `PROJECT-*`, `DOCUMENTATION.md`, `MAIN-STATUS.md`, `REPOSITORY-STRUCTURE.md` не дублируются в платформенных корнях;
- Core CI в `main` проходит;
- Linux platform CI проходит;
- Windows platform CI после последней очистки ожидает завершения;
- Android current CI ожидает завершения на run #533.

## Теги

Существующий публичный release tag `v0.1.0-alpha.1` сохранён.

Запланированные контрольные теги реорганизации и A2.2 implementation slice не созданы: доступный GitHub-коннектор не предоставляет операцию создания tag refs.

## Старые branch refs

Старые ветки пока не удалены. Доступный GitHub-коннектор не предоставляет операцию удаления branch refs; попытка удаления через нулевой SHA возвращает `422 Object does not exist`.

Это не отменяет принятую архитектуру. Старые refs намеренно сохранены до появления доступной операции удаления; их содержимое уже каталогизировано в этом архиве, а причинность дополнительно защищена много-родительской точкой.

## Архив

Сам архив не очищается. Финальная очистка требует отдельного решения.
