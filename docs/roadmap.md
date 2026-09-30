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



## Android Alpha — 0.x

### A0. Skeleton
- [ ] Android module
- [ ] Kotlin/Compose
- [ ] Chaquopy/Python 3.13
- [ ] ARM64
- [ ] compileSdk/targetSdk 37
- [ ] diagnostics skeleton

### A1. Core parity
- [ ] GENOME load/validate
- [ ] Session/Conversation
- [ ] OpenRouter
- [ ] Gemini
- [ ] Pulse
- [ ] first end-to-end turn

### A2. Persistence
- [ ] Persistence Contract implementation
- [ ] Room/SQLite backend
- [ ] CryptoProvider
- [ ] recovery checkpoint
- [ ] restart/resume

### A3. Identity
- [ ] identity_id/device_id
- [ ] identity secret
- [ ] QR/manual transfer
- [ ] merge transaction
- [ ] tombstones
- [ ] runtime instance registration

### A4. Kira:Сбор
- [ ] GitHub App authorization
- [ ] encrypted envelope
- [ ] signing/verification
- [ ] private sync
- [ ] core update
- [ ] shared snapshot consumption

### A5. Android lifecycle
- [ ] foreground service
- [ ] Android 13 notifications
- [ ] Android 14+ FGS types
- [ ] Android 15 restrictions
- [ ] Android 16 quota interactions
- [ ] Android 17 local-network/security checks
- [ ] OEM background diagnostics
- [ ] Кира:Сон

### A6. UX
- [ ] Main conversation
- [ ] side menu
- [ ] Pulse chip
- [ ] avatar state model
- [ ] sessions
- [ ] memory
- [ ] settings
- [ ] КираЧек
- [ ] Геном
- [ ] Кира:Сбор
- [ ] Надстройки

### A7. Security hardening
- [ ] privileged Alek auth
- [ ] no secret leakage in logs/APK
- [ ] secure export/import
- [ ] sync conflict handling
- [ ] migration tests

### A8. Real-device matrix
- [ ] Android 13
- [ ] Android 14
- [ ] Android 15
- [ ] Android 16
- [ ] Android 17
- [ ] vivo X100 Ultra / OriginOS 6

Пока эти пункты не закрыты тестами, Android Alpha не считается функционально эквивалентной desktop Alpha.
