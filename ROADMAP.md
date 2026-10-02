# ROADMAP — platform/android

## Последовательность

A0 Skeleton → A0.D1 Device Acceptance → A1 Core Parity → A2 Persistence → A3 Identity/Authority → A4 Кира:Сбор → A5 Runtime Recovery → A6 Background Runtime → A7 Main UI → A8 Providers → A9 GENOME Protection → A10 КираЧек → A11 Device Matrix → A12 APK Alpha/Release.

## A2

### A2.0 Persistence Foundation
- [x] Room/SQLite;
- [x] entities;
- [x] Android Keystore/AES-GCM boundary;
- [x] gateway через Android bridge.

### A2.1 Store Integration
- [x] canonical Room backend;
- [x] restart read-back;
- [x] conversation/memory separation;
- [x] device acceptance.

### A2.2 Atomic Turn
- [x] durable checkpoint;
- [x] atomic finalization implementation;
- [x] failure injection/contract test;
- [x] UNKNOWN boundary;
- [x] instrumentation test физического Room/SQLite rollback proof реализован;
- [ ] успешный device/emulator run физического rollback proof;
- [ ] отдельная device acceptance;
- [ ] formal acceptance.

### A2.3 Migration / Compatibility
- [ ] versioned schema;
- [ ] migration N→N+1;
- [ ] validation/checksum;
- [ ] explicit legacy import;
- [ ] rollback path.

### A2.4 Recovery / Duplicate Prevention
- [ ] operation/object idempotency;
- [ ] duplicate prevention;
- [ ] crash/restart recovery tests;
- [ ] no silent retry for UNKNOWN.

### A2.5 Device Gate
- [ ] full persistence scenario;
- [ ] restart;
- [ ] migration;
- [ ] security evidence;
- [ ] A2 acceptance.

После A2 — последовательный переход к A3.
