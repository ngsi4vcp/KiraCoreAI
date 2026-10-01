# KiraCoreAI — Android

Основная последовательная Android-ветка: `platform/android`.

## Текущий срез

**Базовая версия разработки:** `0.1.0-alpha.1`  
**Статус:** A2.2 Atomic Turn — реализовано, приёмка открыта.  
**База:** принятие A2.1.  
**Активный GENOME:** revision 22.

Открытые контрольные условия:
- физическое доказательство rollback именно на Room/SQLite;
- отдельная A2.2 device acceptance.

## Текущий test-release / сборка

Публичного Android Release пока нет.

**Текущий тестовый выпуск:** debug APK из CI #560, HEAD `879ca55b42e1972365731e5d5612770a63f8b61c`.

[Скачать текущий Android debug APK artifact](https://github.com/ngsi4vcp/KiraCoreAI/actions/artifacts/11163464055)

[Открыть последние CI-сборки Android](https://github.com/ngsi4vcp/KiraCoreAI/actions/workflows/ci.yml?query=branch%3Aplatform%2Fandroid)

Постоянные релизные APK появятся только после A12 / release acceptance.

## Архитектура

`main` → общий Core  
`platform/android` → Android host/UI/storage/security/tests

Core-срез этой ветки синхронизирован с `main` на контрольной точке `20372923bb06a3a0f7e6e31419f81233ebd3dde1`.

Android не дублирует Core как независимый проект и не переносит domain semantics в Kotlin.

## Технологический стек

Kotlin, Jetpack Compose, Python 3.13, Chaquopy 17.0, Room/SQLite, Android Keystore, ARM64, minSdk 28, target/compileSdk 37.

## Документы

- `AGENTS.md`
- `STATUS.md`
- `ROADMAP.md`
- `CHECKLIST.md`
- `docs/persistence-contract.md`
- `docs/security-architecture.md`
- `docs/kira-sync-contract.md`
- `docs/identity-and-user-memory-contract.md`

Глобальная карта документации — `main/DOCUMENTATION.md`.
