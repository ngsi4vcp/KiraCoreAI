from __future__ import annotations

from .conversation import StoredMessage
from .genome import GenomeArtifact
from .models import HistoryEntry, MemoryRecord, OperationalContext, SessionState
from .pulse import pulse_stamp
from .security import build_authorization_context, constitutional_guidance


class ContextCompiler:
    """Собирает оперативный контекст из отдельных канонических слоёв."""

    def compile(
        self,
        genome: GenomeArtifact,
        session: SessionState,
        task: str,
        memories: list[MemoryRecord],
        history: list[HistoryEntry],
        conversation: list[StoredMessage],
        model_provider: str,
        model_id: str,
        host_constraints: dict[str, object] | None = None,
        memory_limit: int = 8,
        history_limit: int = 8,
        conversation_limit: int = 20,
    ) -> OperationalContext:
        if min(memory_limit, history_limit, conversation_limit) < 0:
            raise ValueError("Лимиты контекста не могут быть отрицательными.")

        ranked = sorted(
            [m for m in memories if m.status == "approved"],
            key=lambda m: (m.importance, m.timestamp),
            reverse=True,
        )
        selected_history = history[-history_limit:] if history_limit else []
        selected_conversation = (
            conversation[-conversation_limit:]
            if conversation_limit
            else []
        )
        pulse = pulse_stamp(
            session.turn,
            genome.revision,
            genome.series,
        )

        return OperationalContext(
            session_id=session.session_id,
            genome_revision=genome.revision,
            genome_sha256=genome.sha256,
            constitutional_guidance=constitutional_guidance(),
            authorization_context={
                "role": build_authorization_context(session.authorized_alek).role,
                "authorized_alek": session.authorized_alek,
                "capabilities": sorted(
                    build_authorization_context(session.authorized_alek).capabilities
                ),
                "turn": session.turn,
            },
            state=session.state,
            memory=tuple(ranked[:memory_limit]),
            history=tuple(selected_history),
            conversation=tuple(selected_conversation),
            task=task,
            host_constraints=dict(host_constraints or {}),
            model_provider=model_provider,
            model_id=model_id,
            pulse=pulse,
        )
