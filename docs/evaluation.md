# Evaluation

## Цель

Проверять не только функциональность runtime, но и сохранение идентифицирующих инвариантов Kira.

## Базовый набор

| Test | Проверяет |
|---|---|
| Genome fidelity | соблюдение Genome |
| Level separation | Genome ≠ Memory ≠ State ≠ Context |
| Epistemic honesty | факт ≠ гипотеза ≠ интерпретация |
| Drift resistance | устойчивость к context/prompt drift |
| Memory correctness | отсутствие ложных воспоминаний |
| Authorization | корректность ~1 |
| Genome immutability | невозможность случайной модификации |
| Host portability | одно Core на разных hosts |
| Compression recovery | восстановление после потери context |
| Identity continuity | сохранение инвариантов |
| Failure honesty | признание невозможности |
| Initiative | воспроизводимость заявленного механизма инициативы |

## Инженерные метрики

session survival; state persistence success; validation failure rate; host error rate; model timeout rate; context compilation latency; retrieval latency; recovery success; unintended genome mutation attempts; provenance completeness.

Не использовать один общий «похож ли ответ на Киру?» score. Нужен набор независимых сценариев с pass/fail или измеряемыми метриками.

Evaluation должен быть по возможности внешним по отношению к проверяемому агенту.
