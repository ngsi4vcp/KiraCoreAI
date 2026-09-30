from __future__ import annotations

from .genome import GenomeArtifact, build_protected_rules
from .models import HistoryEntry, MemoryRecord, OperationalContext, SessionState


class ContextCompiler:
    """Собирает минимальный оперативный контекст, не превращая память в контекст целиком."""

    def compile(
        self,
        genome: GenomeArtifact,
        session: SessionState,
        task: str,
        memories: list[MemoryRecord],
        history: list[HistoryEntry],
        host_constraints: dict[str, object] | None = None,
        memory_limit: int = 8,
        history_limit: int = 8,
    ) -> OperationalContext:
        if memory_limit < 0 or history_limit < 0:
            raise ValueError("Лимиты памяти и истории не могут быть отрицательными.")

        ranked = sorted(
            [m for m in memories if m.status == "approved"],
            key=lambda m: (m.importance, m.timestamp),
            reverse=True,
        )
        selected_history = history[-history_limit:] if history_limit else []
        return OperationalContext(
            genome_revision=genome.revision,
            genome_sha256=genome.sha256,
            protected_rules=build_protected_rules(genome.runtime),
            authorization={
                "authorized_alek": session.authorized_alek,
                "marker": session.authorization_marker,
                "turn": session.turn,
            },
            state=session.state,
            memory=tuple(ranked[:memory_limit]),
            history=tuple(selected_history),
            task=task,
            host_constraints=dict(host_constraints or {}),
        )
