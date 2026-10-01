# Реестр веток и контрольных точек реорганизации

Контрольная точка миграции: 2026-10-01.

## Новая постоянная структура

| Ветка | HEAD на контрольной точке | Роль |
|---|---|---|
| `main` | `ecf46d498f514a20421649ce044f52d5c974ff66` | общий Core и архитектура |
| `platform/android` | `a6a41f2515a2b8ec7aea9e596d3cb75bf2cf81c7` | Android |
| `platform/windows-11` | `630d8e1a80a4226c3c49c7ad74bd7d614653c61c` | Windows 11 |
| `platform/linux` | `9b6353250c22e11b92638356efbe2b3d903ba433` | Linux |
| `archive/history` | `cd82719dd97bb9b3767c6ece2c98863ce2081e60` | архив и восстановление |

## Старые ветки

| Старая ветка | HEAD на момент миграции | Назначение |
|---|---|---|
| `main` | `d0a1fde148077c219ee89727ec0ea6128b9bd506` | прежняя общая ветка |
| `android/alpha-parity` | `7aff9d700e3c67fea7f8e6f2258546d45f94e658` | Android parity/evidence |
| `android/a2.1-hardening-wip` | `21fe369ba2281fb56b88fde7996c5801eb5af2f9` | A2.1 hardening |
| `android/a2.2-atomic-turn-wip` | `0bdb8f1cd0b1af415d1e07cfd2bb1acb04ff376b` | A2.2 implementation slice |
| `draft/core-foundation` | `8bacb8b171c7204b6849181ed36b02e99b2db66b` | исторический Core draft |

## Причинность

Контрольная archive merge-точка `cd82719dd97bb9b3767c6ece2c98863ce2081e60` имеет родителями новую структуру и старые ветвевые HEAD. Это сделано специально, чтобы удаление старых branch refs после аудита не разрывало достижимость Git-истории.

## Перед удалением старых веток

Обязательны:

1. сравнение веток;
2. проверка значимого кода;
3. проверка документации;
4. проверка release/test artifacts;
5. проверка G22/GENOME;
6. проверка CI;
7. проверка тегов контрольных точек;
8. финальный audit;
9. только затем удаление старых refs.

Удаление содержимого самого архива сейчас не выполняется.
