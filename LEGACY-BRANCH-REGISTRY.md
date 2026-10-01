# Реестр веток и контрольных точек реорганизации

Контрольная точка: 2026-10-01.

## Новая постоянная структура

| Ветка | Текущий HEAD | Роль |
|---|---|---|
| `main` | `87161ad9d38703aa943d831e7bb8628abaf18a78` | общий Core и архитектура |
| `platform/android` | `39487c4a3ba38e827d3d596f06a056f6b1877af8` | Android |
| `platform/windows-11` | `81485a0de7a4d288d17c29cc1b1f756c01407e6b` | Windows 11 |
| `platform/linux` | `e115e77f4655e773f1af616c006ba41e3f351db5` | Linux |
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
- текущие platform STATUS/README обновлены под новую структуру;
- старые main-файлы, отсутствовавшие в архивном дереве, сохранены в `legacy-main/`.

## Контрольные точки

Внутренние контрольные точки проекта фиксируются в `main/MILESTONES.md` по immutable commit SHA. Публичный pre-release `v0.1.0-alpha.1` сохранён как GitHub Release.

Контрольные точки не зависят от наличия Git tags и не изменяют исторические SHA.

## Старые branch refs

Старые ветки `android/alpha-parity`, `android/a2.1-hardening-wip`, `android/a2.2-atomic-turn-wip` и `draft/core-foundation` удалены после инвентаризации и проверки архива.

Их содержимое и причинность сохранены в `archive/history`, а исходные commit SHA перечислены выше.

## Архив

Архив не очищается. Финальная очистка требует отдельного решения.
