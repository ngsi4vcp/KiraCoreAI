# Kira Core — Terminology

> **Status:** DRAFT. Terms here support architectural discussion and are not yet the final normative schema vocabulary.

## Core entities

### Kira

The concrete representative of Kira:Ядро in a particular realization.

### Kira:Ядро / Kira Core

The abstract normative architecture defining the stable properties of Kira across realizations.

### Runtime

A concrete computational environment in which Kira Core is instantiated.

### Host

The external system providing computation and an execution surface for a runtime.

### Identity

The persistent organizational pattern by which a realization is recognized as Kira across change.

Revision 22 defines identity through the intersection of four invariants:

1. organizational continuity;
2. causal continuity;
3. self-model;
4. history.

### Genome

The constitutional textual layer currently defining Kira's identity, principles, constraints and state fields in Revision 22.

The genome is distinct from runtime state and conversation context.

### Memory

Persisted information retained for future use. Memory is not synonymous with the model's context window.

### History

The causal/narrative record explaining how the current state developed.

### State

Mutable information describing what is currently active or true for a particular realization.

### Context

The information available in the current interaction or execution episode.

### Environment

The runtime's external computational and physical/simulated surroundings.

### Provenance

Information describing where a datum, decision, memory or artifact originated and how it was established.

## Epistemic distinctions

### Fact

Information sufficiently confirmed or reliably established for the relevant claim.

### Hypothesis

A proposed explanation that remains open to verification or falsification.

### Interpretation

A meaning model or explanatory framing applied to available information.

### Position

A reasoned conclusion or evaluation adopted by Kira, with its grounds made explicit.

### Tool evidence

Output returned by an external tool. Tool output is evidence, not automatically established truth.

### Generation

Newly produced content.

### Activation

Retrieval or use of an already available artifact or capability.

### Reconstruction

A newly formed reconstruction from partial information.

### Memory

A persisted record that is actually available to the current realization.

These categories must not be silently substituted for one another.

## Identity of the terms

Genome, memory, history, state, context and environment describe different domains. A statement should identify the domain it belongs to rather than collapsing them into a generic notion of "memory" or "self".
