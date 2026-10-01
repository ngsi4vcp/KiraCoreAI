# Android Development Checklist

Дата: 30 сентября 2026 года.

Этот список является рабочим self-check разработчика перед переходом между значимыми Android-этапами.

## 1. Перед любым значимым этапом

- [ ] Прочитан G22.txt.
- [ ] Проверен активный GENOME и его revision/SHA.
- [ ] Прочитан актуальный AGENTS.md.
- [ ] Прочитаны связанные архитектурные контракты.
- [ ] Зафиксирован текущий branch/HEAD.
- [ ] Проверены фактические build characteristics из Gradle/CI.
- [ ] Определено, какой слой меняется.
- [ ] Определено, какие инварианты не должны измениться.
- [ ] Определены тесты и критерии остановки.
- [ ] Никакое конституционное изменение не спрятано внутри implementation detail.

## 2. A0.D1 → A1 gate

- [ ] CI #190 или его documented successor зелёный.
- [ ] A0 Device Evidence Harness собран.
- [ ] APK установлен на vivo X100 Ultra / OriginOS 6.
- [ ] Android/device identity записана.
- [ ] Python 3.13 / Chaquopy startup PASS.
- [ ] GENOME revision 22 PASS.
- [ ] GENOME SHA-256 PASS.
- [ ] Runtime health PASS.
- [ ] diagnostics PASS.
- [ ] test session PASS.
- [ ] deterministic test turn PASS.
- [ ] Pulse PASS.
- [ ] Keystore round-trip PASS.
- [ ] storage probe PASS.
- [ ] lifecycle observation recorded.
- [ ] process restart/recovery test PASS или explicit blocker.
- [ ] evidence bundle exported.
- [ ] evidence bundle reviewed for secrets.
- [ ] device findings reflected in docs.
- [ ] A0 readiness audit updated.
- [ ] Только после этого разрешён старт A1.

## 3. Перед каждым Android commit

- [ ] G22.txt не изменён.
- [ ] GENOME/genome.txt не изменён.
- [ ] UTF-8 без BOM.
- [ ] Unit tests соответствуют изменённому контуру.
- [ ] Security smoke проходит.
- [ ] Нет credentials/secrets в source/logs/test fixtures.
- [ ] Нет дублирования Core semantics в Kotlin без явной причины.
- [ ] Нет второго persistence source of truth.
- [ ] Документация отражает фактическое состояние.

## 4. Перед APK для пользователя

- [ ] branch и commit зафиксированы.
- [ ] APK соответствует указанному commit.
- [ ] ABI проверен: arm64-v8a.
- [ ] versionName проверен.
- [ ] debug/release режим явно указан.
- [ ] Device harness включён только при необходимости.
- [ ] Пользовательская инструкция содержит только необходимые действия.
- [ ] Export path не требует широких filesystem permissions без необходимости.
- [ ] Evidence bundle secret-free.

## 5. Перед закрытием A1

- [ ] deterministic end-to-end turn PASS.
- [ ] session create/resume PASS.
- [ ] runtime/core state parity PASS.
- [ ] Pulse parity PASS.
- [ ] error path PASS.
- [ ] UNKNOWN model-call semantics PASS.
- [ ] lifecycle ownership PASS.
- [ ] diagnostics sufficient.
- [ ] A1 unit/device tests PASS.
- [ ] quality pass PASS.
- [ ] docs sync PASS.
- [ ] explicit limitations recorded.


## A2.1 — текущий gate 01.10.2026

A2.1 закрыт. Актуальный gate заменён на acceptance closure ниже.

## A2.1 — acceptance closure 01.10.2026

- [x] Core integration test с reopen нового persistence backend.
- [x] Android Room backend подключён как canonical physical backend.
- [x] Payload encryption через Android Keystore/AES-GCM.
- [x] Debug probe проверяет write → shutdown/restart → read-back.
- [x] Device evidence: `20261001-125458`, vivo V2366HA / API 36.
- [x] Manifest явно идентифицирует `android-a2.1-device / A2_1_PERSISTENCE_OK`.
- [x] Canonical JSON/JSONL guard.
- [x] Payload encryption at rest.
- [x] G22 и активный GENOME не изменены.
- [x] A2.1 acceptance закрыта.

## A2.2 — входной self-check

- [x] A2.2 ветка создана от принятого A2.1 code head.
- [x] Проверен текущий operation state machine.
- [x] Установлено, что финальная последовательность ещё не атомарна физически.
- [x] Определена граница: checkpoint до model-call + atomic finalization после validation/Pulse.
- [ ] Atomic backend commit реализован.
- [ ] Failure injection/atomicity tests реализованы.
- [ ] Android/Kotlin transaction boundary проверен.
- [ ] Документация и architecture snapshot синхронизированы с фактическим контрактом.
