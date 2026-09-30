from __future__ import annotations

from .context import OperationalContext
from .model_contract import ChatMessage, ModelRequest


class PlainTextPromptRenderer:
    """Преобразует оперативный контекст в запрос модели, не являясь хостом."""

    def __init__(self, max_context_messages: int = 20) -> None:
        self.max_context_messages = max_context_messages

    def render(self, context: OperationalContext) -> ModelRequest:
        protected = "\n\n".join(context.protected_rules.values())
        memory_lines = "\n".join(
            f"- {item.type}: {item.content}"
            for item in context.memory
        ) or "- нет утверждённых записей"
        history_lines = "\n".join(
            f"- {item.date}: {item.event} → {item.change}"
            for item in context.history
        ) or "- нет записей"
        state = context.state

        system = (
            "КОНТЕКСТ КИРА:ЯДРА\n\n"
            f"РЕВИЗИЯ ГЕНОМА: {context.genome_revision}\n"
            f"ЦЕЛЬ: {context.task}\n\n"
            "ЗАЩИЩЁННЫЕ ПРАВИЛА:\n"
            f"{protected}\n\n"
            "АКТИВНОЕ СОСТОЯНИЕ:\n"
            f"ЦЕЛИ: {state.active_goals}\n"
            f"ПРОЕКТЫ: {state.projects}\n"
            f"ЗАДАЧИ: {state.unfinished_tasks}\n"
            f"ПРИОРИТЕТЫ: {state.priorities}\n\n"
            "ПАМЯТЬ:\n"
            f"{memory_lines}\n\n"
            "ИСТОРИЯ:\n"
            f"{history_lines}\n\n"
            "ПУЛЬС управляется runtime. Не генерируй его самостоятельно."
        )

        conversation = [
            ChatMessage(
                role="system",
                content=system,
            )
        ]
        conversation.extend(
            message.as_chat_message()
            for message in context.conversation[-self.max_context_messages:]
        )

        return ModelRequest(
            provider=context.model_provider,
            model=context.model_id,
            messages=tuple(conversation),
            metadata={
                "session_id": context.session_id,
                "turn": context.pulse.turn,
                "pulse": context.pulse.value,
            },
        )
