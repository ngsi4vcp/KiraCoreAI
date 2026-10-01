# Реестр веток и контрольных точек реорганизации

Контрольная точка: 2026-10-01.

## Новая постоянная структура

| Ветка | Текущий HEAD | Роль |
|---|---|---|
| `main` | `efb2e3677064d68c303b6910d0cf4cb2ae6a36cb` | общий Core и архитектура |
| `platform/android` | `a6a41f2515a2b8ec7aea9e596d3cb75bf2cf81c7` | Android |
| `platform/windows-11` | `8de9207ab1633e3094118ec7e846e298a4b435b8` | Windows 11 |
| `platform/linux` | `169e4526e6da340e6d3fc59540574c4ae3de1095` | Linux |
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
- G22/GENOME SHA совпадают между рабочими ветками;
- Android branch больше не содержит desktop host/release tooling;
- Windows/Linux содержат desktop host/release tooling;
- main не содержит Android или desktop host;
- Core тесты проходят в main;
- Windows/Linux platform CI проходят;
- Android актуальный CI остаётся открытым до завершения run #533.

## GitHub connector limitation

Текущий GitHub-коннектор предоставляет создание/перемещение веток, но не предоставляет операции удаления branch refs или создания новых tag refs. Поэтому старые ветки пока **не удалены**, а новые reorg/A2.2 control tags не созданы этим инструментом. Это техническое ограничение инструментария, а не изменение принятой архитектуры.

Существующий публичный релизный тег `v0.1.0-alpha.1` сохраняется.

## Правило

Удаление старых refs и финальная очистка архива не являются обязательными до отдельной доступной операции удаления и финального audit. История уже защищена архивной много-родительской точкой.
