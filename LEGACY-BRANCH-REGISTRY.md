# Реестр веток и контрольных точек реорганизации

Контрольная точка: 2026-10-01.

## Новая постоянная структура

| Ветка | Текущий HEAD | Роль |
|---|---|---|
| `main` | `9a81230778b76479416d915cb02d76d3ae6da875` | общий Core и архитектура |
| `platform/android` | `328b0eb823e67263156ec6cfd46ac7666f548b8b` | Android |
| `platform/windows-11` | `d2210d69f6fce8c44f2b256340e41803c9ee00a4` | Windows 11 |
| `platform/linux` | `503e0cf2fd31099c4152b8ca20297a67c22bab0c` | Linux |
| `archive/history` | `f4af8af34ed3ace944406c6b5b94f1d2559d49ee` | история |

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

Она связывает новую структуру и старые значимые HEAD, сохраняя причинность.

## Аудит переноса

Проверено:
- G22/GENOME SHA совпадают;
- `main` не содержит Android или desktop host;
- `platform/android` содержит Android host и не содержит desktop host;
- `platform/windows-11` и `platform/linux` содержат desktop host и не содержат Android;
- глобальные `PROJECT-*`, `DOCUMENTATION.md`, `MAIN-STATUS.md`, `REPOSITORY-STRUCTURE.md` не дублируются в платформенных корнях;
- Core CI `main` проходил успешно на контрольном HEAD;
- Android CI #533 проходил успешно до merge-sync; новый sync run #546 ожидает/проходит проверку;
- Windows CI #543 проходил успешно до merge-sync; новый sync run #547 ожидает/проходит проверку;
- Linux sync CI #548 прошёл успешно;
- текущие platform STATUS/README обновлены под новую структуру.

## Теги

Существующий публичный pre-release tag `v0.1.0-alpha.1` сохранён.

Новые контрольные tags не созданы: доступный GitHub-коннектор не предоставляет операцию создания tag refs. Это ограничение инструмента, а не отказ от принятого решения использовать tags.

## Старые branch refs

Старые ветки пока не удалены. Доступный GitHub-коннектор не предоставляет операцию удаления branch refs; попытка удаления через нулевой SHA ранее вернула `422 Object does not exist`.

Старые refs намеренно сохраняются до финального аудита. Их содержимое каталогизировано в этом архиве и защищено историей.

## Архив

Архив не очищается. Финальная очистка требует отдельного решения.
