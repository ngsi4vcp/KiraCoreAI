# Дорожная карта

## Альфа 0.1.0-alpha.1

- [x] активный KIRA-GENOME
- [x] раздельные слои
- [x] локальная персистентность
- [x] отдельное хранилище разговоров
- [x] единый ModelAdapter
- [x] коннектор OpenRouter
- [x] коннектор Google Gemini
- [x] коннектор LM Studio
- [x] терминальный интерфейс
- [x] динамический выбор модели
- [x] runtime-ПУЛЬС
- [x] START для упаковки
- [x] релизная сборка для Windows/Linux
- [ ] первая внешняя проверка Альфы по сценарию smoke-test

## После первого запуска Альфы

1. стандартизировать ConversationStore по фактической нагрузке;
2. добавить структурированный extractor кандидатов памяти;
3. добавить восстановление незавершённого model-call;
4. добавить streaming;
5. добавить контракт инструментов и рантайма;
6. провести сценарную оценку дрейфа;
7. только после этого углублять агентное планирование.

Не следует до первого Alpha усложнять хранение в распределённую БД или добавлять полноценный vector search без фактической потребности.


## Android Alpha — текущая дорожка

Android развивается отдельной веткой `android/alpha-parity`, сохраняя desktop semantic contract.

- [x] A0 foundation + CI
- [x] A0.D1 device acceptance — evidence `20260930-131718`, vivo V2366HA / API 36
- [x] A1 Core Parity — CI + свежий device evidence `20260930-144146`, `RECOVERY_OK`
- [ ] A2 Persistence — Room/SQLite + CryptoProvider/Keystore + единый physical backend
- [ ] A3 Identity / Authority
- [ ] A4 Кира:Сбор
- [ ] A5 Runtime Recovery / Reconcile
- [ ] A6 Background / FGS hardening
- [ ] A7 Main UX
- [ ] A8 OpenRouter + Gemini providers
- [ ] A9 Genome Guard
- [ ] A10 КираЧек
- [ ] A11 Android 13–17 / OEM matrix
- [ ] A12 distributable APK Alpha

Пошаговый operational route: `android/alpha-parity` → `docs/android-next-steps.md`.

Desktop external smoke остаётся независимой незакрытой задачей и не заменяется Android acceptance.
