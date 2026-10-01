# CHECKLIST — platform/android

## Документы

- [x] AGENTS.md
- [x] STATUS.md
- [x] ROADMAP.md
- [x] CHECKLIST.md
- [x] README.md
- [x] main/DOCUMENTATION.md используется как глобальная карта

## Branch integrity

- [x] platform/android создана от актуального Core-среза;
- [x] старые Android ветки проинвентаризированы и архивированы;
- [x] итоговая проверка старых веток;
- [x] контрольная точка Android A2.1/A2.2 зафиксирована в `main/MILESTONES.md`;
- [x] финальное удаление старых refs.

## A2.2

- [x] durable checkpoint;
- [x] atomic finalization implementation;
- [x] contract success/failure coverage;
- [x] UNKNOWN non-COMPLETED;
- [ ] physical Room/SQLite rollback proof;
- [ ] A2.2 device acceptance;
- [ ] A2.2 formal acceptance.

## Каждый значимый Android change

- [ ] соответствие Core contract;
- [ ] unit/integration tests;
- [ ] security smoke;
- [ ] UTF-8;
- [ ] build/APK verification, если затронут APK;
- [ ] device evidence, если изменено физическое Android behavior;
- [ ] документационная синхронизация;
- [ ] финальная проверка фактов против Git/CI/evidence.
