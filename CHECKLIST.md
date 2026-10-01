# CHECKLIST — platform/android

## Документы

- [x] AGENTS.md
- [x] STATUS.md
- [x] ROADMAP.md
- [x] CHECKLIST.md
- [x] README.md
- [x] main/DOCUMENTATION.md используется как глобальная карта

## Целостность ветки

- [x] platform/android создана от актуального Core-среза;
- [x] старые Android ветки проинвентаризированы и архивированы;
- [x] итоговая проверка старых веток;
- [x] контрольная точка Android A2.1/A2.2 зафиксирована в `main/MILESTONES.md`;
- [x] финальное удаление старых refs.

## A2.2 — атомарный ход

- [x] устойчивый checkpoint;
- [x] реализация атомарной финализации;
- [x] контрактное покрытие успешного и ошибочного хода;
- [x] UNKNOWN не становится COMPLETED;
- [ ] физическое доказательство отката Room/SQLite;
- [ ] отдельная приёмка A2.2 на устройстве;
- [ ] формальная приёмка A2.2.

## Каждый значимый Android change

- [ ] соответствие Core contract;
- [ ] unit/integration tests;
- [ ] security smoke;
- [ ] UTF-8;
- [ ] build/APK verification, если затронут APK;
- [ ] device evidence, если изменено физическое Android behavior;
- [ ] документационная синхронизация;
- [ ] финальная проверка фактов против Git/CI/evidence.
