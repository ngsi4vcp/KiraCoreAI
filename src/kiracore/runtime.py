from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import uuid4

from .context import ContextCompiler
from .conversation import ConversationManifest, ConversationStore
from .genome import GenomeArtifact, GenomeLoader, GenomeStore
from .model_contract import ModelAdapter, ModelResponse
from .operation import OperationPhase, OperationState, RecoveryState
from .persistence import CoreStatePersistence, JsonPersistence
from .persistence_backend import PersistenceBackend
from .pulse import pulse_stamp
from .rendering import PlainTextPromptRenderer
from .session import SessionManager
from .stores import HistoryStore, MemoryStore, OperationStore, StateStore


_KEEP_PULSE = object()


class KiraRuntime:
    """Основной runtime Кира:Ядра."""

    def __init__(
        self,
        root: Path,
        genome: GenomeArtifact,
        genome_store: GenomeStore,
        state_store: StateStore,
        memory_store: MemoryStore,
        history_store: HistoryStore,
        conversation_store: ConversationStore,
        core_persistence: CoreStatePersistence,
        session_manager: SessionManager,
        operation_store: OperationStore,
        backend: PersistenceBackend | None = None,
    ) -> None:
        self.root = root
        self.genome = genome
        self.genome_store = genome_store
        self.state_store = state_store
        self.memory_store = memory_store
        self.history_store = history_store
        self.conversation_store = conversation_store
        self.core_persistence = core_persistence
        self.session_manager = session_manager
        self.operation_store = operation_store
        self.persistence_backend = backend
        self.core_state = core_persistence.load() or self._default_core_state()
        self.last_model_response: ModelResponse | None = None
        self.last_operation: OperationState | None = (
            operation_store.latest()
            or self._operation_from_payload(self.core_state.get("operation"))
        )

    @classmethod
    def start(
        cls,
        project_root: str | Path | None = None,
        expected_revision: int | None = None,
        expected_sha256: str | None = None,
        backend: PersistenceBackend | None = None,
    ) -> "KiraRuntime":
        root = (
            Path(project_root).resolve()
            if project_root is not None
            else Path.cwd().resolve()
        )
        (root / "DATA").mkdir(parents=True, exist_ok=True)
        if backend is None:
            for directory in (
                root / "DATA" / "sessions",
                root / "DATA" / "conversations",
                root / "DATA" / "memory",
                root / "DATA" / "history",
            ):
                directory.mkdir(parents=True, exist_ok=True)

        genome = GenomeLoader(
            expected_sha256=expected_sha256,
            expected_revision=expected_revision,
        ).load_active(root)

        state_store = StateStore(
            None if backend is not None else JsonPersistence(root / "DATA" / "sessions"),
            backend=backend,
        )
        memory_store = MemoryStore(
            None if backend is not None else root / "DATA" / "memory" / "memory.json",
            backend=backend,
        )
        history_store = HistoryStore(
            None if backend is not None else root / "DATA" / "history" / "history.jsonl",
            backend=backend,
        )
        conversation_store = ConversationStore(
            root / "DATA" / "conversations",
            backend=backend,
        )
        core_persistence = CoreStatePersistence(root / "DATA", backend=backend)
        prompt_renderer = PlainTextPromptRenderer()
        context_compiler = ContextCompiler()
        session_manager = SessionManager(
            genome=genome,
            state_store=state_store,
            memory_store=memory_store,
            history_store=history_store,
            conversation_store=conversation_store,
            prompt_renderer=prompt_renderer,
            context_compiler=context_compiler,
        )

        return cls(
            root=root,
            genome=genome,
            genome_store=GenomeStore(genome),
            state_store=state_store,
            memory_store=memory_store,
            history_store=history_store,
            conversation_store=conversation_store,
            core_persistence=core_persistence,
            session_manager=session_manager,
            operation_store=OperationStore(backend),
            backend=backend,
        )

    @staticmethod
    def _default_core_state() -> dict[str, Any]:
        return {
            "schema_version": 1,
            "runtime_status": "initialized",
            "active_session_id": None,
            "identity_id": None,
            "turn": 0,
            "pulse": None,
            "active_provider": None,
            "active_model": None,
            "authorized_alek": False,
            "state": {},
            "last_error": None,
            "operation": None,
        }

    def create_session(
        self,
        provider: str,
        model: str,
        identity_id: str | None = None,
    ) -> ConversationManifest:
        manifest = self.conversation_store.create(provider, model)
        from .models import SessionState

        session = SessionState(
            session_id=manifest.session_id,
            identity_id=identity_id,
            provider=provider,
            model=model,
            runtime_status="active",
        )
        self.state_store.put(session)
        self._save_core(
            session,
            provider,
            model,
            "session_created",
            pulse=None,
        )
        return manifest

    def run(
        self,
        session_id: str,
        task: str,
        model: ModelAdapter,
        provider: str,
        model_id: str,
    ) -> ModelResponse:
        session = self.state_store.get(session_id)
        operation_id = uuid4().hex
        self._set_operation(
            OperationState(
                operation_id=operation_id,
                session_id=session_id,
                phase=OperationPhase.CREATED,
                checkpoint="created",
                provider=provider,
                model=model_id,
                recovery_state=RecoveryState.CHECKPOINTED,
            )
        )
        self._set_operation_phase(
            operation_id,
            OperationPhase.PREPARING,
            "preparing",
        )

        def operation_update(phase: str, checkpoint: str) -> None:
            recovery_state = (
                RecoveryState.COMPLETED
                if phase == OperationPhase.COMPLETED
                else RecoveryState.CHECKPOINTED
            )
            self._set_operation_phase(
                operation_id,
                phase,
                checkpoint,
                recovery_state=recovery_state,
            )

        try:
            turn_finalizer = None
            if self.persistence_backend is not None:

                def finalize_turn(
                    final_session,
                    assistant_message,
                    conversation_manifest,
                    history_entry,
                    pulse,
                ):
                    previous_operation = self.last_operation
                    if (
                        previous_operation is None
                        or previous_operation.operation_id != operation_id
                    ):
                        raise RuntimeError(
                            "Не удалось завершить текущую операцию атомарно."
                        )

                    final_operation = OperationState(
                        operation_id=operation_id,
                        session_id=session_id,
                        phase=OperationPhase.COMPLETED,
                        checkpoint="completed",
                        provider=provider,
                        model=model_id,
                        recovery_state=RecoveryState.COMPLETED,
                    )
                    final_core_state = self._build_core_state(
                        final_session,
                        provider,
                        model_id,
                        "waiting",
                        pulse=pulse,
                    )
                    final_core_state["operation"] = asdict(final_operation)

                    self.persistence_backend.commit_atomic_turn(
                        {
                            "core_state": final_core_state,
                            "session": asdict(final_session),
                            "conversation_manifest": asdict(conversation_manifest),
                            "assistant_message": {
                                **asdict(assistant_message),
                                "pulse": (
                                    asdict(pulse)
                                    if pulse is not None
                                    else None
                                ),
                            },
                            "history": asdict(history_entry),
                            "operation": asdict(final_operation),
                        }
                    )
                    self.last_operation = final_operation
                    self.core_state = final_core_state

                turn_finalizer = finalize_turn

            response, pulse = self.session_manager.run_turn(
                session_id=session_id,
                task=task,
                model=model,
                provider=provider,
                model_id=model_id,
                operation_update=operation_update,
                turn_finalizer=turn_finalizer,
            )
        except Exception as exc:
            from .errors import UnknownModelCall

            is_unknown = isinstance(exc, UnknownModelCall)
            self._set_operation_phase(
                operation_id,
                OperationPhase.UNKNOWN if is_unknown else OperationPhase.FAILED,
                "model_call_unknown" if is_unknown else "failed",
                recovery_state=(
                    RecoveryState.UNKNOWN if is_unknown else RecoveryState.FAILED
                ),
                error=str(exc),
            )
            current_session = self.state_store.get(session_id)
            self._save_core(
                current_session,
                provider,
                model_id,
                "error",
                error=str(exc),
            )
            raise

        self.last_model_response = response
        session = self.state_store.get(session_id)
        response = ModelResponse(
            text=response.text,
            provider=response.provider,
            model=response.model,
            request_id=response.request_id,
            finish_reason=response.finish_reason,
            usage=response.usage,
            raw_metadata={
                **response.raw_metadata,
                "pulse": asdict(pulse),
                "pulse_rendered": pulse.render(),
            },
        )
        if self.persistence_backend is None:
            self._save_core(
                session,
                provider,
                model_id,
                "waiting",
                pulse=pulse,
            )
        return response

    def list_sessions(self) -> list[ConversationManifest]:
        return self.conversation_store.list()

    def resume_session(
        self,
        session_id: str | None = None,
    ) -> ConversationManifest | None:
        manifest = (
            self.conversation_store.get_manifest(session_id)
            if session_id is not None
            else self.resume_latest_session()
        )
        if manifest is None:
            return None

        session = self.state_store.get(manifest.session_id)
        provider = session.provider or manifest.provider
        model = session.model or manifest.model
        pulse = (
            pulse_stamp(
                session.turn,
                self.genome.revision,
                self.genome.series,
            )
            if session.turn > 0
            else None
        )

        self._save_core(
            session,
            provider,
            model,
            "resumed",
            pulse=pulse,
        )
        return manifest

    def resume_latest_session(self) -> ConversationManifest | None:
        sessions = self.list_sessions()
        return sessions[0] if sessions else None

    def approve_memory(self, session_id: str, record_id: str):
        session = self.state_store.get(session_id)
        return self.memory_store.approve(
            record_id,
            authorized_alek=session.authorized_alek,
        )



    @staticmethod
    def _operation_from_payload(payload: Any) -> OperationState | None:
        if not isinstance(payload, dict):
            return None
        required = (
            "operation_id",
            "session_id",
            "phase",
            "checkpoint",
            "provider",
            "model",
            "recovery_state",
        )
        if any(key not in payload for key in required):
            return None
        return OperationState(
            operation_id=str(payload["operation_id"]),
            session_id=str(payload["session_id"]),
            phase=str(payload["phase"]),
            checkpoint=str(payload["checkpoint"]),
            provider=str(payload["provider"]),
            model=str(payload["model"]),
            recovery_state=str(payload["recovery_state"]),
            error=payload.get("error"),
        )

    def _set_operation(self, operation: OperationState) -> None:
        self.last_operation = operation
        self.operation_store.save(operation)
        self.core_state = {
            **self.core_state,
            "operation": asdict(operation),
        }
        self.core_persistence.save(self.core_state)

    def _set_operation_phase(
        self,
        operation_id: str,
        phase: str,
        checkpoint: str,
        recovery_state: str = RecoveryState.CHECKPOINTED,
        error: str | None = None,
    ) -> None:
        previous = self.last_operation
        if previous is None or previous.operation_id != operation_id:
            return
        self._set_operation(
            OperationState(
                operation_id=previous.operation_id,
                session_id=previous.session_id,
                phase=phase,
                checkpoint=checkpoint,
                provider=previous.provider,
                model=previous.model,
                recovery_state=recovery_state,
                error=error,
            )
        )

    def _build_core_state(
        self,
        session: Any,
        provider: str,
        model: str,
        status: str,
        pulse: Any = _KEEP_PULSE,
        error: str | None = None,
    ) -> dict[str, Any]:
        pulse_payload = (
            self.core_state.get("pulse")
            if pulse is _KEEP_PULSE
            else asdict(pulse) if pulse is not None else None
        )
        return {
            **self.core_state,
            "schema_version": 1,
            "genome_revision": self.genome.revision,
            "genome_sha256": self.genome.sha256,
            "runtime_status": status,
            "active_session_id": session.session_id,
            "identity_id": session.identity_id,
            "turn": session.turn,
            "pulse": pulse_payload,
            "active_provider": provider,
            "active_model": model,
            "authorized_alek": session.authorized_alek,
            "state": asdict(session.state),
            "updated_at": session.updated_at,
            "last_error": error,
        }

    def _save_core(
        self,
        session: Any,
        provider: str,
        model: str,
        status: str,
        pulse: Any = _KEEP_PULSE,
        error: str | None = None,
    ) -> None:
        self.core_state = self._build_core_state(
            session,
            provider,
            model,
            status,
            pulse=pulse,
            error=error,
        )
        self.core_persistence.save(self.core_state)
