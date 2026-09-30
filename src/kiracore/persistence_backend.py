from __future__ import annotations

import json
from typing import Any, Protocol


class PersistenceBackend(Protocol):
    """Единый физический backend для доменных persistence-store."""

    def save_core_state(self, payload: dict[str, Any]) -> None: ...
    def load_core_state(self) -> dict[str, Any] | None: ...

    def save_session(self, payload: dict[str, Any]) -> None: ...
    def list_sessions(self) -> list[dict[str, Any]]: ...

    def save_conversation_manifest(self, payload: dict[str, Any]) -> None: ...
    def list_conversation_manifests(self) -> list[dict[str, Any]]: ...
    def append_conversation_message(self, payload: dict[str, Any]) -> None: ...
    def recent_conversation(
        self,
        session_id: str,
        limit: int,
    ) -> list[dict[str, Any]]: ...
    def delete_conversation(self, session_id: str) -> None: ...

    def save_memory(self, payload: dict[str, Any]) -> None: ...
    def list_memory(self) -> list[dict[str, Any]]: ...

    def save_history(self, payload: dict[str, Any]) -> None: ...
    def list_history(self) -> list[dict[str, Any]]: ...

    def save_operation(self, payload: dict[str, Any]) -> None: ...
    def load_operation(self, operation_id: str) -> dict[str, Any] | None: ...
    def list_operations(self) -> list[dict[str, Any]]: ...


class RoomPersistenceBackend:
    """Python-адаптер Android Room gateway, доступный через Chaquopy."""

    def __init__(self, gateway: Any) -> None:
        if gateway is None:
            raise ValueError("Room gateway не может быть пустым.")
        self.gateway = gateway

    @staticmethod
    def _decode_object(value: Any) -> dict[str, Any]:
        return json.loads(str(value))

    @staticmethod
    def _decode_array(value: Any) -> list[dict[str, Any]]:
        decoded = json.loads(str(value))
        if not isinstance(decoded, list):
            raise ValueError("Persistence backend вернул не массив.")
        return decoded

    @staticmethod
    def _encode(payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False)

    def save_core_state(self, payload: dict[str, Any]) -> None:
        self.gateway.saveCoreState(self._encode(payload))

    def load_core_state(self) -> dict[str, Any] | None:
        value = self.gateway.loadCoreState()
        return None if value is None else self._decode_object(value)

    def save_session(self, payload: dict[str, Any]) -> None:
        self.gateway.saveSession(self._encode(payload))

    def list_sessions(self) -> list[dict[str, Any]]:
        return self._decode_array(self.gateway.listSessions())

    def save_conversation_manifest(self, payload: dict[str, Any]) -> None:
        self.gateway.saveConversationManifest(self._encode(payload))

    def list_conversation_manifests(self) -> list[dict[str, Any]]:
        return self._decode_array(self.gateway.listConversationManifests())

    def append_conversation_message(self, payload: dict[str, Any]) -> None:
        self.gateway.appendConversationMessage(self._encode(payload))

    def recent_conversation(
        self,
        session_id: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        return self._decode_array(
            self.gateway.recentConversation(session_id, limit)
        )

    def delete_conversation(self, session_id: str) -> None:
        self.gateway.deleteConversation(session_id)

    def save_memory(self, payload: dict[str, Any]) -> None:
        self.gateway.saveMemory(self._encode(payload))

    def list_memory(self) -> list[dict[str, Any]]:
        return self._decode_array(self.gateway.listMemory())

    def save_history(self, payload: dict[str, Any]) -> None:
        self.gateway.appendHistory(self._encode(payload))

    def list_history(self) -> list[dict[str, Any]]:
        return self._decode_array(self.gateway.listHistory())

    def save_operation(self, payload: dict[str, Any]) -> None:
        self.gateway.saveOperation(self._encode(payload))

    def load_operation(self, operation_id: str) -> dict[str, Any] | None:
        value = self.gateway.loadOperation(operation_id)
        return None if value is None else self._decode_object(value)

    def list_operations(self) -> list[dict[str, Any]]:
        return self._decode_array(self.gateway.listOperations())
