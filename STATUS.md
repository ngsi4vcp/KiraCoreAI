# STATUS — platform/windows-11

**Тип:** текущий фактический снимок.

## База

- ветка: `platform/windows-11`;
- текущий HEAD: `417fc854626c53fb06bbb760cd7cc98f7eab08c6`;
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

- предыдущий миграционный CI #543 — SUCCESS;
- новый sync CI #547 — выполнялся после merge-sync; результат проверять по GitHub перед новым изменением статуса.

## Открыто

- Windows 11 external smoke на актуальном срезе;
- release verification после реорганизации;
- следующий Windows release;
- дальнейшие изменения общего Core сначала проходят через `main`.

## Важное

Успешная сборка/CI не означает внешнюю Windows 11 acceptance.
