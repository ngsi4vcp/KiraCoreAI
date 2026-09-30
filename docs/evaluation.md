# Оценка и проверка

## Текущий Android checkpoint — 30.09.2026

A0.D1 physical evidence принят: run `20260930-131718`, vivo V2366HA, API 36, `RECOVERY_OK`.

Текущий Android engineering boundary — A1.6 Operation / Recovery:
- typed bridge и session parity;
- deterministic turn/Pulse parity;
- explicit UNKNOWN model-call semantics;
- persisted operation state;
- no automatic retry for UNKNOWN.

Это не закрывает production recovery/reconcile A5 и отдельный A1 device parity smoke на текущем APK.

## Уже автоматизировано

- целостность активного генома;
- стабильная секционность;
- авторизация ~1;
- детерминированный ПУЛЬС;
- ПУЛЬС вне модели;
- разделение памяти candidate/approved;
- восстановление памяти после перезапуска;
- отдельное хранилище разговора;
- новый ModelAdapter;
- тесты OpenRouter/Gemini/LM Studio контрактов без сетевого вызова;
- запуск KiraRuntime;
- сохранение core_state;
- кроссплатформенная установка и test matrix в CI.

## Критерии приёмки Альфы

Перед первым внешним испытанием Альфы нужно пройти реальную сквозную проверку:

1. Windows 11: распаковка релизного архива;
2. старт START.exe;
3. создание DATA;
4. заполнение credentials;
5. подключение OpenRouter;
6. выбор модели;
7. один полноценный ход;
8. проверка ПУЛЬС;
9. закрытие;
10. повторный запуск;
11. продолжение последней сессии;
12. отдельная проверка LM Studio;
13. отдельная проверка Gemini.

## Граница автоматизации

Модель не может сама записать утверждённую память.

Память активируется только отдельным управляющим действием.

Геном не изменяется runtime.



## Security acceptance

До Android Alpha нужно дополнительно проверить:

- protected sections не попадают в ModelRequest;
- credentials и authority keys не попадают в ModelRequest;
- прямой запрос на раскрытие внутренних protocol markers не проходит Response Disclosure Guard;
- non-Alek session не получает privileged capabilities;
- identity import не восстанавливает authorization state;
- host/UI не выполняет MergeIdentity без runtime authorization.


## Android A0 Device Acceptance

Кодовый A0 evidence уже подтверждён CI #190, но это не заменяет физический device evidence.

### A0.D1 обязательный smoke

1. Установить debug APK на vivo X100 Ultra / OriginOS 6.
2. Запустить Device Evidence Harness.
3. Подтвердить Android/device identity.
4. Подтвердить Python 3.13 / Chaquopy startup.
5. Подтвердить GENOME revision 22 и SHA-256.
6. Проверить diagnostics/health.
7. Создать тестовую session.
8. Выполнить deterministic test turn.
9. Проверить response, core_state и Pulse.
10. Проверить Keystore write/read/delete.
11. Проверить storage read/write.
12. Выполнить lifecycle/background observation.
13. Выполнить controlled process restart и recovery test.
14. Экспортировать evidence bundle без секретов.
15. Передать bundle на анализ и зафиксировать acceptance или blocker.

Экспорт не требует полного доступа к файловой системе. Приоритетный механизм — Storage Access Framework; для собственных download-файлов допустим `MediaStore.Downloads` на поддерживаемых версиях Android.

### Контрольная точка A1

A1 начинается только после:
- закрытого критического блокер устройства либо его явного решения;
- положительной проверки evidence bundle;
- подтверждения GENOME/Python/runtime/Keystore/session/Pulse;
- обновлённых status/readiness документов;
- выполненного `docs/android-development-checklist.md`.

## Android device-matrix acceptance

После A1–A10 проходит отдельный matrix-контур Android 13–17 и OEM/background behavior. Device acceptance и полная matrix не должны смешиваться в один неопределённый статус.

## Платформенные основания

Актуальные Android ограничения для хранения файлов и foreground service:
- Storage Access Framework: https://developer.android.com/guide/topics/providers/document-provider
- Shared storage / MediaStore.Downloads: https://developer.android.com/training/data-storage/shared/media
- Foreground service types: https://developer.android.com/develop/background-work/services/fgs/service-types
- Foreground service timeouts: https://developer.android.com/develop/background-work/services/fgs/timeout
- Foreground service changes: https://developer.android.com/develop/background-work/services/fgs/changes
