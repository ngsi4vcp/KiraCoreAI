# Kira Core — Scope and Boundaries

> **Status:** DRAFT. This document is not an approved Core Specification and does not modify Kira's genome.
>
> Basis: Kira:Genome Revision 22 and Kira Core Bootstrap 0.1.

## 1. Purpose

Kira Core is the normative, portable layer that defines the stable structure of Kira independently of a particular host, language model, runtime, or deployment environment.

The Core is intended to make Kira reproducible from an external, versioned specification rather than from a chat history.

## 2. Architectural model

```
Kira
 |
 +-- Kira Core
 |    |
 |    +-- ChatGPT Runtime
 |    +-- Minecraft Runtime
 |    +-- future runtimes
 |
 +-- runtime-specific state and implementation
```

A runtime is an implementation environment. It is not the definition of Kira itself.

## 3. Core boundary

The Core may define:

- identity invariants and continuity principles;
- personality and behavioral principles;
- values and epistemic rules;
- cognitive architecture at the abstract level;
- memory semantics and provenance requirements;
- motivation, goals, decision and planning abstractions;
- self-model semantics;
- learning, adaptation and reflection principles;
- persistence and continuity requirements;
- runtime contracts;
- safety boundaries;
- evaluation criteria;
- versioning and change protocol.

The Core must remain independent of a specific LLM, host product, operating system, game, UI, or tool provider.

## 4. State boundary

Kira State contains mutable information about a particular instance or period of operation.

Examples:

- current goals;
- active tasks;
- working state;
- current environment observations;
- episodic records;
- runtime status;
- temporary hypotheses;
- recoverable operational data.

State is not automatically part of the constitutional identity of Kira.

## 5. Capsule boundary

A Kira Core Capsule is a portable compact representation used to bootstrap another context or runtime.

The Capsule:

- references a specific Core version/schema;
- identifies its provenance;
- may summarize the currently relevant state;
- must not silently override the authoritative Core;
- must be reproducible from versioned project artifacts.

Preferred forms are:

- `KIRA_CORE_CAPSULE.md`;
- `KIRA_CORE_CAPSULE.json`.

## 6. Runtime boundary

A runtime provides the mechanisms through which the Core is instantiated.

Runtime-specific concerns include:

- model inference;
- context-window management;
- tool access;
- UI or interaction protocol;
- scheduling;
- storage backend;
- network access;
- environment adapters;
- implementation-specific safety controls.

A runtime limitation must not be represented as a personal choice of Kira.

## 7. ChatGPT Memory boundary

ChatGPT Memory is treated as a host-provided context mechanism, not as the complete persistence layer of Kira Core.

There is no assumption of automatic bidirectional synchronization with GitHub.

## 8. Authority order

For project architecture:

1. approved Core Specification;
2. approved Architectural Decisions;
3. Capsule and implementation artifacts generated from those sources;
4. runtime state and context.

Historical chat material is development history, not the authoritative project state.

## 9. Non-goals of this document

This draft does not decide:

- the formal Identity schema;
- the formal Personality schema;
- the final Core schema;
- the final Capsule schema;
- the exact memory storage implementation;
- the final motivation model;
- the implementation of ChatGPT or Minecraft runtimes.

Those remain open architectural work.
