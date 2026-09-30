from __future__ import annotations

from pathlib import Path

from .genome import GenomeArtifact, GenomeLoader, GenomeStore
from .session import SessionManager
from .stores import HistoryStore, MemoryStore, StateStore


class KiraRuntime:
    """Единая точка запуска KiraCoreAI с загрузкой активного генома."""

    def __init__(
        self,
        genome: GenomeArtifact,
        genome_store: GenomeStore,
        state_store: StateStore,
        memory_store: MemoryStore,
        history_store: HistoryStore,
        session_manager: SessionManager,
    ) -> None:
        self.genome = genome
        self.genome_store = genome_store
        self.state_store = state_store
        self.memory_store = memory_store
        self.history_store = history_store
        self.session_manager = session_manager

    @classmethod
    def start(
        cls,
        project_root: str | Path | None = None,
        expected_revision: int | None = None,
        expected_sha256: str | None = None,
    ) -> "KiraRuntime":
        genome = GenomeLoader(
            expected_sha256=expected_sha256,
            expected_revision=expected_revision,
        ).load_active(project_root)

        genome_store = GenomeStore(genome)
        state_store = StateStore()
        memory_store = MemoryStore()
        history_store = HistoryStore()
        session_manager = SessionManager(
            genome=genome,
            state_store=state_store,
            memory_store=memory_store,
            history_store=history_store,
        )

        return cls(
            genome=genome,
            genome_store=genome_store,
            state_store=state_store,
            memory_store=memory_store,
            history_store=history_store,
            session_manager=session_manager,
        )
