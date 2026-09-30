from __future__ import annotations

from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

from .context import ContextCompiler
from .conversation import ConversationManifest, ConversationStore, utc_now
from .genome import GenomeArtifact, GenomeLoader, GenomeStore
from .model_contract import ModelAdapter, ModelResponse
from .persistence import CoreStatePersistence, JsonPersistence
from .rendering import PlainTextPromptRenderer
from .session import SessionManager
from .stores import HistoryStore, MemoryStore, StateStore


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
        self.core_state = core_persistence.load() or self._default_core_state()
        self.last_model_response: ModelResponse | None = None

    @classmethod
    def start(
        cls,
        project_root: str | Path | None = None,
        expected_revision: int | None = None,
        expected_sha256: str | None = None,
    ) -> "KiraRuntime":
        root = (
            Path(project_root).resolve()
            if project_root is not None
            else Path.cwd().resolve()
        )
        for directory in (
            root / "DATA",
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
            JsonPersistence(root / "DATA" / "sessions"),
        )
        memory_store = MemoryStore(root / "DATA" / "memory" / "memory.json")
        history_store = HistoryStore(
            root / "DATA" / "history" / "history.jsonl"
        )
        conversation_store = ConversationStore(
            root / "DATA" / "conversations"
        )
        core_persistence = CoreStatePersistence(root / "DATA")
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
        )

    @staticmethod
    def _default_core_state() -> dict[str, Any]:
        return {
            "schema_version": 1,
            "runtime_status": "initialized",
            "active_session_id": None,
            "turn": 0,
            "pulse": None,
            "active_provider": None,
            "active_model": None,
            "last_error": None,
        }

    def create_session(self, provider: str, model: str) -> ConversationManifest:
        manifest = self.conversation_store.create(provider, model)
        from .models import SessionState

        session = SessionState(
            session_id=manifest.session_id,
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
        try:
            response, pulse = self.session_manager.run_turn(
                session_id=session_id,
                task=task,
                model=model,
                provider=provider,
                model_id=model_id,
            )
        except Exception as exc:
            session = self.state_store.get(session_id)
            self._save_core(
                session,
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
            },
        )
        self._save_core(
            session,
            provider,
            model_id,
            "waiting",
            pulse=pulse,
        )
        return response

    def resume_latest_session(self) -> ConversationManifest | None:
        sessions = self.conversation_store.list()
        return sessions[0] if sessions else None

    def approve_memory(self, session_id: str, record_id: str):
        session = self.state_store.get(session_id)
        return self.memory_store.approve(
            record_id,
            authorized_alek=session.authorized_alek,
        )

    def _save_core(
        self,
        session: Any,
        provider: str,
        model: str,
        status: str,
        pulse: Any = None,
        error: str | None = None,
    ) -> None:
        self.core_state = {
            **self.core_state,
            "schema_version": 1,
            "genome_revision": self.genome.revision,
            "genome_sha256": self.genome.sha256,
            "runtime_status": status,
            "active_session_id": session.session_id,
            "turn": session.turn,
            "pulse": asdict(pulse) if pulse else self.core_state.get("pulse"),
            "active_provider": provider,
            "active_model": model,
            "authorized_alek": session.authorized_alek,
            "state": asdict(session.state),
            "updated_at": session.updated_at,
            "last_error": error,
        }
        self.core_persistence.save(self.core_state)
