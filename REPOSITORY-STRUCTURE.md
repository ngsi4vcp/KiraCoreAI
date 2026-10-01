# Структура репозитория

## Ветки

```
main
├── общий Core
├── глобальные контракты
├── общие тесты
└── глобальная документация

platform/android
├── принятый Core из main
├── android/
├── platform-specific tests
└── platform-specific docs

platform/windows-11
├── принятый Core из main
├── Windows host
├── platform-specific tests
└── platform-specific docs

platform/linux
├── принятый Core из main
├── Linux host
├── platform-specific tests
└── platform-specific docs

archive/history
└── старые/справочные материалы и историческая причинность
```

## Корень main

Канонические документы:
`AGENTS.md`, `DOCUMENTATION.md`, `PROJECT-RULES.md`, `PROJECT-PLAN.md`, `PROJECT-ARCHITECTURE.md`, `PROJECT-BEHAVIOR.md`, `PROJECT-CHECKLIST.md`, `MAIN-STATUS.md`, `REPOSITORY-STRUCTURE.md`.

## Правило каталогов

Корневые проектные документы не дублируются в `docs/`.
`docs/` используется для специализированных технических материалов и контрактов.

Платформа хранит свой operational/documentation слой в корне ветки и специализированные технические документы в `docs/`.

## Правило Core

Изменение Core сначала делается в `main`.
После проверки новая версия Core используется платформой.
Платформа не становится отдельным форком Core.

## История

Исторические commit-цепочки не переписываются.
Удаление branch ref не удаляет уже сохранённую причинность в `archive/history`, tags и Git history.
