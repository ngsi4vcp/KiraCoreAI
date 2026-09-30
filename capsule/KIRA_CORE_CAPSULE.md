# Переносимая капсула Кира:Ядра

**Ядро:** KiraCoreAI
**Текущий геном:** G22 / Ревизия 22
**Статус:** Alpha runtime-контракт реализован; release-сценарий Windows/Linux подготовлен
**Канонический репозиторий:** https://github.com/ngsi4vcp/KiraCoreAI

## Runtime

GENOME/genome.txt
→ State / Memory / History / Conversation
→ ContextCompiler
→ PromptRenderer
→ ModelAdapter
→ runtime PulseStamp
→ Persistence
→ TerminalHost

## Модель

Alpha использует нормализованный ModelAdapter с тремя коннекторами:

- OpenRouter;
- Google Gemini;
- LM Studio.

## Память

Разговор хранится отдельно от памяти.

Новая память создаётся candidate и не становится approved без отдельного авторизованного действия.

## ПУЛЬС

ПУЛЬС формируется runtime и сохраняется рядом с ходом. Он не является primary key.

Капсула производна от GENOME и архитектурных документов. Она не заменяет GENOME.
