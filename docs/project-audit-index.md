# Project Audit Index

Короткий обязательный список для self-audit, самопроверки и автоактуализации.

## Старт

1. `G22.txt` — конституционные/эпистемические правила.
2. `MAIN-STATUS.md` — текущая общая карта проекта.
3. Текущая ветка + её `AGENTS.md`.
4. Этот файл — маршрут чтения.
5. Только затем — код, tests и CI.

## Общие документы — читать всегда

- `README.md`
- `docs/architecture.md`
- `docs/runtime.md`
- `docs/context-model.md`
- `docs/persistence.md`
- `docs/evaluation.md`
- `docs/roadmap.md`
- `docs/decisions.md`
- `docs/language-policy.md`
- `docs/utf8-policy.md`
- `docs/genome-format.md`
- `docs/genome-governance.md`
- `schemas/`

GitHub: https://github.com/ngsi4vcp/KiraCoreAI

## Windows / Linux

Дополнительно читать:

- `README.md`
- `docs/terminal-alpha.md`
- `docs/model-connectors.md`
- `docs/evaluation.md`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `scripts/package_release.py`
- `START.py`

Главная проверка: документация → фактический runtime → Python test matrix → package-smoke → release workflow → внешняя smoke.

## Android

Ветка: `android/alpha-parity`

Обязательно:

- `AGENTS.md`
- `docs/android-port-status.md`
- `docs/android-readiness-audit.md`
- `docs/android-development-plan.md`
- `docs/android-next-steps.md` — текущий пошаговый маршрут A2 → A12 и quality gates
- `docs/android-alpha-implementation-plan.md`
- `docs/android-a0-plan.md`
- `docs/android-device-evidence-plan.md`
- `docs/android-a1-plan.md`
- `docs/android-a1-bridge-contract.md`
- `docs/android-development-checklist.md`
- `docs/kira-sync-contract.md`
- `docs/identity-and-user-memory-contract.md`
- `docs/persistence-contract.md`
- `docs/security-architecture.md`

Главная проверка: общий контракт → Android boundary → Python parity → Kotlin mapping → unit tests → APK packaging → security smoke → device evidence.

## Перед каждым auto-update

Проверить:

- не изменены ли `G22.txt` и `GENOME/genome.txt`;
- не смешаны ли platform-specific задачи;
- совпадает ли документация с фактическим Git/CI/device status;
- нет ли stale checkpoint, который выглядит как current;
- русскоязычен ли пользовательский контур;
- UTF-8 без BOM;
- нет ли секретов в Git/build output/evidence;
- сохранено ли разделение GENOME / STATE / MEMORY / HISTORY / CONVERSATION / CONTEXT;
- сохранён ли Pulse ownership в runtime;
- сохранена ли explicit UNKNOWN boundary;
- не объявлен ли этап закрытым без соответствующего acceptance.

## Перед передачей этапа Алеку

Формат:

`самоаудит → найденные отклонения → исправления → tests/CI → device evidence при необходимости → остаточные ограничения → фактическая точка согласования`.

Исторические документы не переписывать задним числом без необходимости; при смене статуса добавлять новую актуальную контрольную точку.
