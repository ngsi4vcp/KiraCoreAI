# Переносимая капсула Кира:Ядра

**Ядро:** KiraCoreAI
**Текущий геном:** G22 / Ревизия 22
**Статус:** контракт рантайма Альфы реализован; сценарий релизной сборки для Windows/Linux подготовлен
**Канонический репозиторий:** https://github.com/ngsi4vcp/KiraCoreAI

## Рантайм

GENOME/genome.txt
→ State / Memory / History / Conversation
→ ContextCompiler
→ PromptRenderer
→ ModelAdapter
→ PulseStamp, формируемый рантаймом
→ Persistence
→ TerminalHost

## Модель

Альфа использует нормализованный ModelAdapter с тремя коннекторами:

- OpenRouter;
- Google Gemini;
- LM Studio.

## Память

Разговор хранится отдельно от памяти.

Новая память создаётся candidate и не становится approved без отдельного авторизованного действия.

## ПУЛЬС

ПУЛЬС формируется рантаймом и сохраняется рядом с ходом. Он не является первичным ключом.

Капсула производна от GENOME и архитектурных документов. Она не заменяет GENOME.
