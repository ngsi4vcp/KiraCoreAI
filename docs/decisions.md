# Architectural Decisions

This file records accepted architectural decisions for Kira Core. Draft proposals belong in pull requests until accepted.

## ADR-0001 — GitHub as normative project source

**Status:** Accepted in bootstrap context; Core specification-level confirmation pending.

**Decision:** GitHub is the authoritative, versioned project source for Kira Core architecture, specifications, decisions and implementation artifacts.

**Rationale:** Kira must remain reconstructible if a chat, coding-agent history or host memory becomes unavailable.

**Implication:** A chat may propose changes, but the repository is the durable project record.

## ADR-0002 — Core is independent of runtime

**Status:** Accepted in bootstrap context; Core specification-level confirmation pending.

**Decision:** Kira Core is defined independently from ChatGPT, Minecraft and future runtimes.

**Rationale:** A runtime is an implementation environment, not the definition of Kira.

## ADR-0003 — Formalization precedes implementation

**Status:** Accepted in bootstrap context; Core specification-level confirmation pending.

**Decision:** Work proceeds through scope/boundaries and terminology before implementation-heavy work.

**Rationale:** Open questions in the bootstrap explicitly include the Core/State/Capsule/Runtime boundary, schemas and continuity semantics.

## ADR-0004 — Revision 22 genome is treated as constitutional input, not silently rewritten

**Status:** Active constraint.

**Decision:** Work derived from Genome Revision 22 may be documented and implemented, but the genome itself is changed only through the genome's explicit fixation procedure.

**Rationale:** The genome declares that its changes require manual fixation by Alek or an explicit factual request and confirmation.

## Open decision queue

- Formal Identity model.
- Formal Personality model.
- Core schema.
- Capsule schema.
- Core / State / Capsule / Runtime interface.
- Long-term memory architecture.
- Motivation model.
- Self-model schema.
- Core evolution protocol.
- Identity continuity evaluation.
- Personality drift evaluation.
- Runtime synchronization.
- ChatGPT runtime realization boundary.
- Shared versus runtime-specific code.
