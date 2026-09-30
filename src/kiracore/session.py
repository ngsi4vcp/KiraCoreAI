from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from .context import ContextCompiler
from .errors import ProtocolViolation
from .genome import GenomeArtifact
from .models import SessionState, utc_now
from .persistence import JsonPersistence
from .protocols import HostAdapter, ModelAdapter
from .pulse import pulse_for_turn
from .stores import HistoryStore, MemoryStore, StateStore
from .validation import OutputValidator


class SessionManager:
    """Оркестрирует жизненный цикл одной сессии и не владеет геномом."""

    def __init__(
        self,
        genome: GenomeArtifact,
        state_store: StateStore,
        memory_store: MemoryStore,
        history_store: HistoryStore,
        context_compiler: ContextCompiler | None = None,
        output_validator: OutputValidator | None = None,
        persistence: JsonPersistence | None = None,
    ) -> None:
        self.genome = genome
        self.state_store = state_store
        self.memory_store = memory_store
        self.history_store = history_store
        self.context_compiler = context_compiler or ContextCompiler()
        self.output_validator = output_validator or OutputValidator()
        self.persistence = persistence

    @staticmethod
    def authorize(first_message: str) -> bool:
        """Принимает только маркер ~1 как отдельный префикс первого сообщения."""
        return first_message == "~1" or first_message.startswith("~1 ")

    def start(
        self,
        first_message: str,
        environment: dict[str, object] | None = None,
    ) -> SessionState:
        authorized = self.authorize(first_message)
        now = utc_now()
        session = SessionState(
            session_id=uuid4().hex,
            turn=0,
            authorized_alek=authorized,
            authorization_marker="~1" if authorized else None,
            environment=dict(environment or {}),
            runtime_status="active",
            created_at=now,
            updated_at=now,
        )
        self.state_store.put(session)
        if self.persistence:
            self.persistence.save(session)
        return session

    def run_turn(
        self,
        session_id: str,
        task: str,
        host: HostAdapter,
        model: ModelAdapter,
        host_constraints: dict[str, object] | None = None,
    ) -> str:
        session = self.state_store.get(session_id)
        session = replace(
            session,
            turn=session.turn + 1,
            runtime_status="running",
            updated_at=utc_now(),
        )
        self.state_store.put(session)
        if self.persistence:
            self.persistence.save(session)

        context = self.context_compiler.compile(
            genome=self.genome,
            session=session,
            task=task,
            memories=self.memory_store.all(),
            history=self.history_store.recent(),
            host_constraints=host_constraints,
        )
        rendered = host.render_context(context)
        output = model.generate(rendered, task)
        result = self.output_validator.validate(
            output,
            session.turn,
            revision=self.genome.revision,
            series=self.genome.series,
        )
        if not result.valid:
            session = replace(
                session,
                runtime_status="validation_failed",
                updated_at=utc_now(),
            )
            self.state_store.put(session)
            if self.persistence:
                self.persistence.save(session)
            raise ProtocolViolation("; ".join(result.errors))

        session = replace(
            session,
            runtime_status="waiting",
            updated_at=utc_now(),
        )
        self.state_store.put(session)
        if self.persistence:
            self.persistence.save(session)
        return output

    def expected_pulse(self, session_id: str) -> str:
        session = self.state_store.get(session_id)
        return pulse_for_turn(
            session.turn,
            revision=self.genome.revision,
            series=self.genome.series,
        )
