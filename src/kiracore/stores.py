from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import os

from .errors import AuthorizationError, KiraCoreError
from .models import HistoryEntry, MemoryRecord, SessionState
from .persistence import JsonPersistence
from .persistence_backend import PersistenceBackend


class StateStore:
    """Изменяемое состояние сессий с восстановлением после перезапуска."""

    def __init__(
        self,
        persistence: JsonPersistence | None = None,
        backend: PersistenceBackend | None = None,
    ) -> None:
        if persistence is not None and backend is not None:
            raise ValueError("StateStore не допускает два канонических backend.")
        self._items: dict[str, SessionState] = {}
        self.persistence = persistence
        self.backend = backend
        if backend is not None:
            for item in backend.list_sessions():
                try:
                    state = self._from_dict(item)
                except (ValueError, KeyError, TypeError):
                    continue
                self._items[state.session_id] = state
        elif persistence and persistence.directory.exists():
            for path in persistence.directory.glob("*.json"):
                try:
                    session_id = path.stem
                    self._items[session_id] = self._from_dict(
                        json.loads(path.read_text(encoding="utf-8"))
                    )
                except (OSError, ValueError, KeyError, TypeError):
                    continue

    def put(self, state: SessionState) -> None:
        self._items[state.session_id] = deepcopy(state)
        if self.backend is not None:
            self.backend.save_session(asdict(state))
        elif self.persistence:
            self.persistence.save(state)

    def get(self, session_id: str) -> SessionState:
        try:
            return deepcopy(self._items[session_id])
        except KeyError as exc:
            raise KiraCoreError(f"Сессия не найдена: {session_id}") from exc

    def exists(self, session_id: str) -> bool:
        return session_id in self._items

    @staticmethod
    def _from_dict(item: dict) -> SessionState:
        from .models import StateSnapshot

        state = StateSnapshot(**item.get("state", {}))
        return SessionState(
            session_id=item["session_id"],
            identity_id=item.get("identity_id"),
            turn=item.get("turn", 0),
            authorized_alek=item.get("authorized_alek", False),
            authorization_marker=item.get("authorization_marker"),
            provider=item.get("provider"),
            model=item.get("model"),
            environment=item.get("environment", {}),
            state=state,
            runtime_status=item.get("runtime_status", "created"),
            created_at=item.get("created_at") or "",
            updated_at=item.get("updated_at") or "",
        )


class MemoryStore:
    """Постоянное хранилище памяти; автоматическая активация не разрешена."""

    def __init__(
        self,
        path: str | Path | None = None,
        backend: PersistenceBackend | None = None,
    ) -> None:
        if path is not None and backend is not None:
            raise ValueError("MemoryStore не допускает два канонических backend.")
        self._items: dict[str, MemoryRecord] = {}
        self.path = Path(path) if path else None
        self.backend = backend
        self._load()

    def _load(self) -> None:
        if self.backend is not None:
            for item in self.backend.list_memory():
                record = MemoryRecord(**item)
                self._items[record.id] = record
            return
        if not self.path or not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        for item in data.get("records", []):
            record = MemoryRecord(**item)
            self._items[record.id] = record

    def _persist_record(self, record: MemoryRecord) -> None:
        if self.backend is not None:
            self.backend.save_memory(asdict(record))
            return
        if not self.path:
            return
        payload = {
            "schema_version": 1,
            "records": [
                {
                    "id": item.id,
                    "type": item.type,
                    "content": item.content,
                    "timestamp": item.timestamp,
                    "source": item.source,
                    "confidence": item.confidence,
                    "importance": item.importance,
                    "provenance": item.provenance,
                    "entities": item.entities,
                    "valid_from": item.valid_from,
                    "valid_to": item.valid_to,
                    "status": item.status,
                    "owner_identity_id": item.owner_identity_id,
                    "privacy_scope": item.privacy_scope,
                }
                for item in self._items.values()
            ],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(payload, ensure_ascii=False, indent=2)
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.path.parent,
                delete=False,
                prefix=".memory.",
            ) as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
                tmp_path = Path(handle.name)
            os.replace(tmp_path, self.path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    def add_candidate(self, record: MemoryRecord) -> None:
        if record.id in self._items:
            raise KiraCoreError(f"Запись памяти уже существует: {record.id}")
        item = deepcopy(record)
        item.status = "candidate"
        self._items[item.id] = item
        self._persist_record(item)

    def approve(self, record_id: str, authorized_alek: bool) -> MemoryRecord:
        if not authorized_alek:
            raise AuthorizationError("Утверждение памяти требует авторизации Алека.")
        item = self._get(record_id)
        item.status = "approved"
        self._items[record_id] = item
        self._persist_record(item)
        return deepcopy(item)

    def cancel(self, record_id: str, authorized_alek: bool) -> MemoryRecord:
        if not authorized_alek:
            raise AuthorizationError("Отмена памяти требует авторизации Алека.")
        item = self._get(record_id)
        item.status = "cancelled"
        self._items[record_id] = item
        self._persist_record(item)
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

    def candidates(self) -> list[MemoryRecord]:
        return [
            deepcopy(x)
            for x in self._items.values()
            if x.status == "candidate"
        ]


class HistoryStore:
    """Постоянная причинная история; запись только добавлением."""

    def __init__(
        self,
        path: str | Path | None = None,
        backend: PersistenceBackend | None = None,
    ) -> None:
        if path is not None and backend is not None:
            raise ValueError("HistoryStore не допускает два канонических backend.")
        self._items: list[HistoryEntry] = []
        self.path = Path(path) if path else None
        self.backend = backend
        self._load()

    def _load(self) -> None:
        if self.backend is not None:
            self._items = [
                HistoryEntry(**item)
                for item in self.backend.list_history()
            ]
            return
        if not self.path or not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                self._items.append(HistoryEntry(**json.loads(line)))

    def append(self, entry: HistoryEntry) -> None:
        item = deepcopy(entry)
        self._items.append(item)
        if self.backend is not None:
            self.backend.save_history(asdict(item))
            return
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "id": item.id,
                            "date": item.date,
                            "event": item.event,
                            "change": item.change,
                            "cause": item.cause,
                            "significance": item.significance,
                            "consequence": item.consequence,
                            "revision": item.revision,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    def recent(self, limit: int = 10) -> list[HistoryEntry]:
        if limit < 0:
            raise ValueError("Лимит истории не может быть отрицательным.")
        if not limit:
            return []
        return [deepcopy(x) for x in self._items[-limit:]]


class OperationStore:
    """Постоянный журнал runtime-операций для физического backend Android."""

    def __init__(self, backend: PersistenceBackend | None = None) -> None:
        self.backend = backend

    def save(self, operation) -> None:
        if self.backend is not None:
            self.backend.save_operation(asdict(operation))

    def latest(self):
        if self.backend is None:
            return None
        from .operation import OperationState

        items = self.backend.list_operations()
        if not items:
            return None
        payload = items[0]
        return OperationState(
            operation_id=str(payload["operation_id"]),
            session_id=str(payload["session_id"]),
            phase=str(payload["phase"]),
            checkpoint=str(payload["checkpoint"]),
            provider=str(payload["provider"]),
            model=str(payload["model"]),
            recovery_state=str(payload["recovery_state"]),
            error=payload.get("error"),
        )
