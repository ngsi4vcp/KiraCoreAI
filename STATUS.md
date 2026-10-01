# STATUS — platform/linux

**Тип:** текущий фактический снимок.

## База

- ветка: `platform/linux`;
- текущий HEAD: контрольная документационная ветка; кодовый миграционный срез: `e115e77f4655e773f1af616c006ba41e3f351db5`;
- Core-срез синхронизирован с `main` на merge-контрольной точке `20372923bb06a3a0f7e6e31419f81233ebd3dde1`;
- общий Core не является независимым форком.

## Реализовано

- [x] START entrypoint;
- [x] TerminalHost;
- [x] terminal selector;
- [x] desktop Alpha application orchestration;
- [x] release packager;
- [x] исторический публичный pre-release `v0.1.0-alpha.1`.

## CI

- CI #566 — SUCCESS на `e115e77f4655e773f1af616c006ba41e3f351db5`;

## Открыто

- Linux external smoke на актуальном срезе;
- release verification после реорганизации;
- следующий Linux release;
- дальнейшие изменения общего Core сначала проходят через `main`.

## Важное

Успешная сборка/CI не означает внешнюю Linux acceptance.
