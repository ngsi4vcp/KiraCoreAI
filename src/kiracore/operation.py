from __future__ import annotations

from dataclasses import dataclass


class OperationPhase:
    CREATED = "CREATED"
    PREPARING = "PREPARING"
    CONTEXT_READY = "CONTEXT_READY"
    MODEL_CALL_STARTED = "MODEL_CALL_STARTED"
    MODEL_CALL_FINISHED = "MODEL_CALL_FINISHED"
    UNKNOWN = "UNKNOWN"
    VALIDATING = "VALIDATING"
    PERSISTING = "PERSISTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RecoveryState:
    NOT_NEEDED = "NOT_NEEDED"
    CHECKPOINTED = "CHECKPOINTED"
    UNKNOWN = "UNKNOWN"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class OperationState:
    operation_id: str
    session_id: str
    phase: str
    checkpoint: str
    provider: str
    model: str
    recovery_state: str
    error: str | None = None
