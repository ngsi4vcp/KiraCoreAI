# Архитектура KiraCoreAI

## Логическая схема

```
G22 / GENOME
      ↓
KiraCore
      ↓
state / memory / history / conversation
      ↓
context / model contract / runtime
      ↓
platform host
      ↓
OS / storage / UI / transport
```

## `main`

`main` — архитектурная база.

В нём находятся:
- актуальный общий Python Core;
- глобальные схемы;
- общие протоколы и контракты;
- общие тесты Core;
- глобальная проектная документация;
- G22/GENOME;
- общие CI-проверки.

В `main` не должно быть platform-specific host-кода.

## Платформа

Каждая `platform/*` получает принятый Core из `main` и собирает поверх него:
- host;
- UI;
- storage adapter;
- security boundary;
- platform tests;
- platform release tooling;
- platform documentation.

Смысл Core не меняется ради UI-особенности.

## Тестирование

`main`:
Core unit/contract tests.

Платформа:
Core+Platform integration/unit/build/device checks.

Разделение нужно не только архитектурно, но и для контроля ресурса GitHub Actions.

## Persistence

Общий Persistence Contract принадлежит Core.
Физический backend принадлежит платформе.
На Android текущий backend — Room/SQLite; физическая rollback-приёмка A2.2 остаётся открытой.

## Архитектурная истина

При конфликте «цель ↔ текущая реализация» проверяется этап.
При конфликте «обещанный результат принятого этапа ↔ факт» расхождение является проблемой.
При конфликте «документ ↔ код» сначала исследуется расхождение; фактические статусные сведения приводятся к коду и доказательствам.
