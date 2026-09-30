from __future__ import annotations

from copy import deepcopy

from .errors import AuthorizationError, KiraCoreError
from .models import HistoryEntry, MemoryRecord, SessionState


class StateStore:
    """Изменяемое состояние сессий; доступа к геному здесь нет."""

    def __init__(self) -> None:
        self._items: dict[str, SessionState] = {}

    def put(self, state: SessionState) -> None:
        self._items[state.session_id] = deepcopy(state)

    def get(self, session_id: str) -> SessionState:
        try:
            return deepcopy(self._items[session_id])
        except KeyError as exc:
            raise KiraCoreError(f"Сессия не найдена: {session_id}") from exc

    def exists(self, session_id: str) -> bool:
        return session_id in self._items


class MemoryStore:
    """Хранилище памяти. Обычная запись создаётся только как кандидат."""

    def __init__(self) -> None:
        self._items: dict[str, MemoryRecord] = {}

    def add_candidate(self, record: MemoryRecord) -> None:
        if record.id in self._items:
            raise KiraCoreError(f"Запись памяти уже существует: {record.id}")
        item = deepcopy(record)
        item.status = "candidate"
        self._items[item.id] = item

    def approve(self, record_id: str, authorized_alek: bool) -> MemoryRecord:
        if not authorized_alek:
            raise AuthorizationError("Утверждение памяти требует авторизации Алека.")
        item = self._get(record_id)
        item.status = "approved"
        self._items[record_id] = item
        return deepcopy(item)

    def cancel(self, record_id: str, authorized_alek: bool) -> MemoryRecord:
        if not authorized_alek:
            raise AuthorizationError("Отмена памяти требует авторизации Алека.")
        item = self._get(record_id)
        item.status = "cancelled"
        self._items[record_id] = item
        return deepcopy(item)

    def _get(self, record_id: str) -> MemoryRecord:
        try:
            return deepcopy(self._items[record_id])
        except KeyError as exc:
            raise KiraCoreError(f"Запись памяти не найдена: {record_id}") from exc

    def all(self) -> list[MemoryRecord]:
        return [deepcopy(x) for x in self._items.values()]

    def approved(self) -> list[MemoryRecord]:
        return [
            deepcopy(x)
            for x in self._items.values()
            if x.status == "approved"
        ]


class HistoryStore:
    """Добавляемая причинная история. Изменение генома сюда не ведёт."""

    def __init__(self) -> None:
        self._items: list[HistoryEntry] = []

    def append(self, entry: HistoryEntry) -> None:
        self._items.append(deepcopy(entry))

    def recent(self, limit: int = 10) -> list[HistoryEntry]:
        if limit < 0:
            raise ValueError("Лимит истории не может быть отрицательным.")
        if not limit:
            return []
        return [deepcopy(x) for x in self._items[-limit:]]
