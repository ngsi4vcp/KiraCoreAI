# Глобальный план проекта KiraCoreAI

## Цель

Создать переносимое KiraCoreAI с единым семантическим Core и отдельными платформенными host-реализациями, сохраняя конституционные, persistence, identity, security и behavioral инварианты.

Конечное приложение должно сохранять различие GENOME / STATE / MEMORY / HISTORY / CONVERSATION / CONTEXT / ENVIRONMENT, детерминированный runtime-ПУЛЬС, контролируемую память, устойчивую персистентность и платформенную переносимость.

## Общая последовательность

### Альфа 0.1.0-alpha.1 — desktop vertical slice
Принятые базовые возможности:
- GENOME;
- раздельные слои;
- локальная персистентность;
- ConversationStore;
- единый ModelAdapter;
- OpenRouter;
- Google Gemini;
- LM Studio;
- терминальный host;
- динамический выбор модели;
- ПУЛЬС;
- Windows/Linux release artifacts.

Открытый исторический пункт: внешняя smoke-проверка Альфы.

### Core hardening / общая база
Текущая задача main — не развивать платформенный UI, а поддерживать общий контракт, схемы, runtime, persistence abstraction, security boundaries, model contracts и общие тесты.

### Android A0–A12
Последовательность платформы:
A0 Skeleton → A0.D1 Device Acceptance → A1 Core Parity → A2 Persistence → A3 Identity/Authority → A4 Кира:Сбор → A5 Runtime Recovery → A6 Background Runtime → A7 Main UI → A8 Providers → A9 GENOME Protection → A10 КираЧек → A11 Device Matrix → A12 APK Alpha/Release.

A2 деталируется:
- A2.0 Persistence Foundation;
- A2.1 Store Integration;
- A2.2 Atomic Turn;
- A2.3 Migration/Compatibility;
- A2.4 Recovery/Duplicate Prevention;
- A2.5 Device Gate.

Текущий фактический срез: A2.2 реализация завершена частично по acceptance-оси, но ещё не принята: физический Room/SQLite rollback proof и отдельный A2.2 device acceptance открыты.

### Windows 11
После стабилизации общей Core-базы создаётся и развивается Windows host на `platform/windows-11`.
Общий Core не дублируется и не форкается.

### Linux
После стабилизации общей Core-базы создаётся и развивается Linux host на `platform/linux`.
Общий Core не дублируется и не форкается.

## Порядок разработки

Общая разработка идёт последовательно:
`main Core` → принятый Core → активная платформа → платформенная проверка → следующий Core change при необходимости.

Параллельное долгоживущее развитие нескольких временных линий не является нормой.

## Релизная и контрольная модель

Каждая платформа показывает в собственном `README.md` единственный актуальный release/pre-release/test-release с версией, типом сборки, commit, датой и ссылкой на артефакт/релиз.

Публичные релизы живут через GitHub Releases и release-артефакты, а не в виде копий бинарников в Git-дереве. Внутренние контрольные точки проекта фиксируются в `MILESTONES.md` по commit SHA.
