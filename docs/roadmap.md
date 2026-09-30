# Roadmap

## Phase 0 — Foundation

- [x] Repository audit
- [x] Confirm main branch
- [x] Rewrite README
- [x] Establish architecture documents
- [x] Establish governance rules
- [x] Establish evaluation model
- [ ] Import canonical G22 artifact
- [ ] Define machine-readable Core schema
- [ ] Define Capsule schema

## Phase 1 — Minimal Harness

- [ ] GenomeLoader
- [ ] checksum/provenance
- [ ] StateStore
- [ ] MemoryStore
- [ ] HistoryStore
- [ ] ContextCompiler
- [ ] HostAdapter
- [ ] ModelAdapter
- [ ] Validator
- [ ] SessionManager
- [ ] persistence
- [ ] unit tests

## Phase 2 — First Host

Candidate: Pi-oriented host adapter / minimal RPC host.

- [ ] host protocol
- [ ] session lifecycle
- [ ] model invocation
- [ ] result validation
- [ ] recovery
- [ ] end-to-end test

## Phase 3 — Behavioral Evaluation

- [ ] identity tests
- [ ] epistemic tests
- [ ] authorization tests
- [ ] level-separation tests
- [ ] drift tests
- [ ] compression/recovery tests
- [ ] persistence tests

## Phase 4 — Additional Hosts

- [ ] Codex host
- [ ] Hermes host
- [ ] local/OpenAI-compatible host
- [ ] comparative evaluation

## Phase 5 — Mature Core

После доказательства минимальных инвариантов: richer memory, planning, motivation, decision architecture, self-model, runtime contracts, autonomous scheduler и deeper evaluation.

Никакой конкретный host не должен диктовать Core architecture.
