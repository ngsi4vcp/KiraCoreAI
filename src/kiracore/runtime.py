from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .context import ContextCompiler
from .conversation import ConversationManifest, ConversationStore
from .genome import GenomeArtifact, GenomeLoader, GenomeStore
from .model_contract import ModelAdapter, ModelRequest, ModelResponse
from .persistence import CoreStatePersistence, JsonPersistence
from .pulse import pulse_stamp
from .rendering import PlainTextPromptRenderer
from .stores import HistoryStore, MemoryStore, StateStore


class KiraRuntime:
    """Основной runtime Кира:Ядра: геном, состояние, память, история, диалог и модель."""

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
    ) -> None:
        self.root = root
        self.genome = genome
        self.genome_store = genome_store
        self.state_store = state_store
        self.memory_store = memory_store
        self.history_store = history_store
        self.conversation_store = conversation_store
        self.core_persistence = core_persistence
        self.context_compiler = ContextCompiler()
        self.prompt_renderer = PlainTextPromptRenderer()
        self.core_state = core_persistence.load() or {
            "schema_version": 1,
            "genome_revision": genome.revision,
            "genome_sha256": genome.sha256,
            "runtime_status": "initialized",
            "active_session_id": None,
            "turn": 0,
            "pulse": None,
            "active_provider": None,
            "active_model": None,
        }
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
        (root / "DATA").mkdir(parents=True, exist_ok=True)
        (root / "DATA" / "sessions").mkdir(parents=True, exist_ok=True)
        (root / "DATA" / "conversations").mkdir(parents=True, exist_ok=True)
        (root / "DATA" / "memory").mkdir(parents=True, exist_ok=True)
        (root / "DATA" / "history").mkdir(parents=True, exist_ok=True)
        genome = GenomeLoader(
            expected_sha256=expected_sha256,
            expected_revision=expected_revision,
        ).load_active(root)

        state_store = StateStore(JsonPersistence(root / "DATA" / "sessions"))
        memory_store = MemoryStore(root / "DATA" / "memory" / "memory.jsonl")
        history_store = HistoryStore(root / "DATA" / "history" / "history.jsonl")
        conversation_store = ConversationStore(root / "DATA" / "conversations")
        core_persistence = CoreStatePersistence(root / "DATA")

        return cls(
            root=root,
            genome=genome,
            genome_store=GenomeStore(genome),
            state_store=state_store,
            memory_store=memory_store,
            history_store=history_store,
            conversation_store=conversation_store,
            core_persistence=core_persistence,
        )

    def create_session(self, provider: str, model: str) -> ConversationManifest:
        manifest = self.conversation_store.create(provider, model)
        from .models import SessionState

        session = SessionState(
            session_id=manifest.session_id,
            turn=0,
            runtime_status="active",
        )
        self.state_store.put(session)
        self._save_core(
            session=session,
            provider=provider,
            model=model,
            status="session_created",
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
        session = self._set_session(
            session,
            turn=session.turn + 1,
            status="running",
        )
        self.conversation_store.append(
            session_id,
            session.turn,
            "user",
            task,
        )
        self._save_core(
            session=session,
            provider=provider,
            model=model_id,
            status="running",
        )

        context = self.context_compiler.compile(
            genome=self.genome,
            session=session,
            task=task,
            memories=self.memory_store.all(),
            history=self.history_store.recent(),
            conversation=self.conversation_store.recent(session_id, 20),
            model_provider=provider,
            model_id=model_id,
        )
        request = self.prompt_renderer.render(context)
        response = model.generate(request)
        pulse = pulse_stamp(
            session.turn,
            self.genome.revision,
            self.genome.series,
        )
        self.conversation_store.append(
            session_id,
            session.turn,
            "assistant",
            response.text,
            pulse=pulse,
        )
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
        self.last_model_response = response
        session = self._set_session(session, status="waiting")
        self._save_core(
            session=session,
            provider=provider,
            model=model_id,
            status="waiting",
            pulse=pulse,
        )
        return response

    def _set_session(self, session: Any, turn: int | None = None, status: str | None = None):
        from dataclasses import replace
        from .conversation import utc_now

        updated = replace(
            session,
            turn=session.turn if turn is None else turn,
            runtime_status=session.runtime_status if status is None else status,
            updated_at=utc_now(),
        )
        self.state_store.put(updated)
        return updated

    def _save_core(
        self,
        session: Any,
        provider: str,
        model: str,
        status: str,
        pulse: Any = None,
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
            "state": asdict(session.state),
            "updated_at": session.updated_at,
        }
        self.core_persistence.save(self.core_state)
