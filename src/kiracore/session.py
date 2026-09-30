from __future__ import annotations

from dataclasses import replace
from typing import Callable
from uuid import uuid4

from .context import ContextCompiler
from .conversation import ConversationStore, utc_now
from .errors import ProtocolViolation
from .genome import GenomeArtifact
from .model_contract import ModelAdapter, ModelResponse
from .models import HistoryEntry
from .operation import OperationPhase
from .persistence import JsonPersistence
from .pulse import pulse_stamp
from .rendering import PlainTextPromptRenderer
from .stores import HistoryStore, MemoryStore, StateStore
from .validation import OutputValidator


class SessionManager:
    """Единый исполнитель хода сессии."""

    def __init__(
        self,
        genome: GenomeArtifact,
        state_store: StateStore,
        memory_store: MemoryStore,
        history_store: HistoryStore,
        conversation_store: ConversationStore,
        prompt_renderer: PlainTextPromptRenderer | None = None,
        persistence: JsonPersistence | None = None,
        context_compiler: ContextCompiler | None = None,
        output_validator: OutputValidator | None = None,
    ) -> None:
        self.genome = genome
        self.state_store = state_store
        self.memory_store = memory_store
        self.history_store = history_store
        self.conversation_store = conversation_store
        self.prompt_renderer = prompt_renderer or PlainTextPromptRenderer()
        self.persistence = persistence
        self.context_compiler = context_compiler or ContextCompiler()
        self.output_validator = output_validator or OutputValidator()

    @staticmethod
    def authorize(first_message: str) -> bool:
        return first_message == "~1" or first_message.startswith("~1 ")

    @staticmethod
    def strip_authorization_marker(message: str) -> str:
        if message == "~1":
            return ""
        if message.startswith("~1 "):
            return message[3:]
        return message

    def run_turn(
        self,
        session_id: str,
        task: str,
        model: ModelAdapter,
        provider: str,
        model_id: str,
        host_constraints: dict[str, object] | None = None,
        operation_update: Callable[[str, str], None] | None = None,
    ) -> tuple[ModelResponse, object]:
        session = self.state_store.get(session_id)
        first_turn = session.turn == 0
        authorized = self.authorize(task) if first_turn else session.authorized_alek
        clean_task = (
            self.strip_authorization_marker(task)
            if first_turn
            else task
        )
        session = replace(
            session,
            turn=session.turn + 1,
            authorized_alek=authorized,
            authorization_marker="~1" if authorized else None,
            provider=provider,
            model=model_id,
            runtime_status="running",
            updated_at=utc_now(),
        )
        self.state_store.put(session)
        if self.persistence:
            self.persistence.save(session)

        self.conversation_store.append(
            session_id,
            session.turn,
            "user",
            clean_task,
        )

        context = self.context_compiler.compile(
            genome=self.genome,
            session=session,
            task=clean_task,
            memories=self.memory_store.all(),
            history=self.history_store.recent(),
            conversation=self.conversation_store.recent(session_id, 20),
            model_provider=provider,
            model_id=model_id,
            host_constraints=host_constraints,
        )
        request = self.prompt_renderer.render(context)
        if operation_update:
            operation_update(OperationPhase.CONTEXT_READY, "context_ready")
            operation_update(OperationPhase.MODEL_CALL_STARTED, "model_call_started")

        response = model.generate(request)

        if operation_update:
            operation_update(OperationPhase.MODEL_CALL_FINISHED, "model_call_finished")

        if operation_update:
            operation_update(OperationPhase.VALIDATING, "validation_started")
        validation = self.output_validator.validate(response)
        if not validation.valid:
            session = replace(
                session,
                runtime_status="validation_failed",
                updated_at=utc_now(),
            )
            self.state_store.put(session)
            if self.persistence:
                self.persistence.save(session)
            raise ProtocolViolation("; ".join(validation.errors))

        pulse = pulse_stamp(
            session.turn,
            self.genome.revision,
            self.genome.series,
        )
        if operation_update:
            operation_update(OperationPhase.PERSISTING, "persistence_started")
        self.conversation_store.append(
            session_id,
            session.turn,
            "assistant",
            response.text,
            pulse=pulse,
        )
        self.history_store.append(
            HistoryEntry(
                id=uuid4().hex,
                date=utc_now(),
                event="Завершение хода сессии",
                change=f"Завершён ход {session.turn} через {provider}/{model_id}.",
                cause=clean_task[:500] or "Пустая задача пользователя.",
                significance="Результат хода сохранён в разговоре и связан с ПУЛЬС.",
                consequence="Состояние сессии переведено в ожидание следующего хода.",
                revision=f"G{self.genome.revision}",
            )
        )

        session = replace(
            session,
            runtime_status="waiting",
            updated_at=utc_now(),
        )
        self.state_store.put(session)
        if self.persistence:
            self.persistence.save(session)

        if operation_update:
            operation_update(OperationPhase.COMPLETED, "completed")

        return response, pulse
