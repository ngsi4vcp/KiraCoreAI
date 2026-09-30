from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .model_contract import ChatMessage
from .pulse import PulseStamp


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class StateSnapshot:
    active_goals: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    unfinished_tasks: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    working_hypotheses: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    updated_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class MemoryRecord:
    id: str
    type: str
    content: str
    timestamp: str = field(default_factory=utc_now)
    source: str = ""
    confidence: float | None = None
    importance: float = 0.5
    provenance: str = ""
    entities: list[str] = field(default_factory=list)
    valid_from: str | None = None
    valid_to: str | None = None
    status: str = "candidate"
    owner_identity_id: str | None = None
    privacy_scope: str = "Private"


@dataclass(slots=True)
class HistoryEntry:
    id: str
    date: str
    event: str
    change: str
    cause: str
    significance: str
    consequence: str
    revision: str = "G22"


@dataclass(slots=True)
class SessionState:
    session_id: str
    identity_id: str | None = None
    turn: int = 0
    authorized_alek: bool = False
    authorization_marker: str | None = None
    provider: str | None = None
    model: str | None = None
    environment: dict[str, Any] = field(default_factory=dict)
    state: StateSnapshot = field(default_factory=StateSnapshot)
    runtime_status: str = "created"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class OperationalContext:
    session_id: str
    genome_revision: int
    genome_sha256: str
    constitutional_guidance: tuple[str, ...]
    authorization_context: dict[str, Any]
    state: StateSnapshot
    memory: tuple[MemoryRecord, ...]
    history: tuple[HistoryEntry, ...]
    conversation: tuple[Any, ...]
    task: str
    host_constraints: dict[str, Any]
    model_provider: str
    model_id: str
    pulse: PulseStamp


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
