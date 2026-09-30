from __future__ import annotations

from .context import OperationalContext
from .model_contract import ChatMessage, ModelRequest
from .security import AuthorizationContext, render_reflection_instruction


class PlainTextPromptRenderer:
    """Преобразует контекст в ModelRequest; это не хост."""

    def __init__(self, max_context_messages: int = 20) -> None:
        self.max_context_messages = max_context_messages

    def render(self, context: OperationalContext) -> ModelRequest:
        memory_lines = "\n".join(
            f"- {item.type}: {item.content}"
            for item in context.memory
        ) or "- нет утверждённых записей"
        history_lines = "\n".join(
            f"- {item.date}: {item.event} → {item.change}"
            for item in context.history
        ) or "- нет записей"

        state = context.state
        auth = AuthorizationContext(
            role=str(context.authorization_context["role"]),
            authorized_alek=bool(context.authorization_context["authorized_alek"]),
            capabilities=frozenset(context.authorization_context["capabilities"]),
        )
        guidance = "\n".join(
            f"- {item}" for item in context.constitutional_guidance
        )
        system = (
            "КОНТЕКСТ КИРА:ЯДРА\n\n"
            f"РЕВИЗИЯ ГЕНОМА: {context.genome_revision}\n"
            f"ТЕКУЩАЯ ЗАДАЧА: {context.task}\n\n"
            "СЕМАНТИЧЕСКАЯ ПРОЕКЦИЯ КОНСТИТУЦИИ:\n"
            f"{guidance}\n\n"
            "ПРАВА ТЕКУЩЕЙ СЕССИИ:\n"
            f"Роль: {auth.role}\n"
            f"Привилегированная авторизация: {auth.authorized_alek}\n"
            f"Доступные возможности runtime: "
            f"{', '.join(sorted(auth.capabilities)) or 'нет'}\n\n"
            "ПРЕДГЕНЕРАЦИОННАЯ ПРОВЕРКА:\n"
            f"{render_reflection_instruction(auth)}\n\n"
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

        messages = [ChatMessage(role="system", content=system)]
        messages.extend(
            item.as_chat_message()
            for item in context.conversation[-self.max_context_messages:]
        )
        return ModelRequest(
            provider=context.model_provider,
            model=context.model_id,
            messages=tuple(messages),
            metadata={
                "session_id": context.session_id,
                "turn": context.pulse.turn,
                "pulse": context.pulse.value,
            },
        )
