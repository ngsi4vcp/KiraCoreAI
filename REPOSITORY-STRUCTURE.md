# Структура репозитория

## Ветки

```
main
├── общий Core
├── глобальные контракты
├── общие тесты
└── глобальная документация

platform/android
├── актуальный материализованный Core из main
├── android/
├── platform-specific tests
└── platform-specific docs

platform/windows-11
├── актуальный материализованный Core из main
├── Windows host
├── platform-specific tests
└── platform-specific docs

platform/linux
├── актуальный материализованный Core из main
├── Linux host
├── platform-specific tests
└── platform-specific docs

archive/history
└── старые/справочные материалы и историческая причинность
```

## Core между ветками

`main` — единственный канонический источник Core.

Платформенная ветка содержит рабочую копию Core, необходимую для сборки и интеграционного тестирования. Она не является независимым форком.

После изменения Core:
1. изменить Core в `main`;
2. пройти Core CI;
3. синхронизировать принятый Core-срез с активной платформой;
4. пройти platform CI.

Платформа не должна самостоятельно менять общий Core без последующего переноса изменения в `main`.

## Корень main

Канонические документы:
`AGENTS.md`, `DOCUMENTATION.md`, `PROJECT-RULES.md`, `PROJECT-PLAN.md`, `PROJECT-ARCHITECTURE.md`, `PROJECT-BEHAVIOR.md`, `PROJECT-CHECKLIST.md`, `MAIN-STATUS.md`, `REPOSITORY-STRUCTURE.md`.

`паспорт.мд` — временный переходный паспорт текущей реорганизации, не постоянный источник проектной истины.

## Правило каталогов

Корневые проектные документы не дублируются в `docs/`.
`docs/` используется для специализированных технических материалов и контрактов.

Платформа хранит свой operational/documentation слой в корне ветки и специализированные технические документы в `docs/`.

## История

Исторические commit-цепочки не переписываются.
Удаление branch ref не удаляет уже сохранённую причинность в `archive/history`, tags и Git history.
