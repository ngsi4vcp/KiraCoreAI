from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import os

from .errors import AuthorizationError, KiraCoreError
from .models import HistoryEntry, MemoryRecord, SessionState
from .persistence import JsonPersistence


class StateStore:
    """Изменяемое состояние сессий с восстановлением после перезапуска."""

    def __init__(self, persistence: JsonPersistence | None = None) -> None:
        self._items: dict[str, SessionState] = {}
        self.persistence = persistence
        if persistence and persistence.directory.exists():
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
        if self.persistence:
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

    def __init__(self, path: str | Path | None = None) -> None:
        self._items: dict[str, MemoryRecord] = {}
        self.path = Path(path) if path else None
        self._load()

    def _load(self) -> None:
        if not self.path or not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        for item in data.get("records", []):
            record = MemoryRecord(**item)
            self._items[record.id] = record

    def _persist(self) -> None:
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
        self._persist()

    def approve(self, record_id: str, authorized_alek: bool) -> MemoryRecord:
        if not authorized_alek:
            raise AuthorizationError("Утверждение памяти требует авторизации Алека.")
        item = self._get(record_id)
        item.status = "approved"
        self._items[record_id] = item
        self._persist()
        return deepcopy(item)

    def cancel(self, record_id: str, authorized_alek: bool) -> MemoryRecord:
        if not authorized_alek:
            raise AuthorizationError("Отмена памяти требует авторизации Алека.")
        item = self._get(record_id)
        item.status = "cancelled"
        self._items[record_id] = item
        self._persist()
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

    def __init__(self, path: str | Path | None = None) -> None:
        self._items: list[HistoryEntry] = []
        self.path = Path(path) if path else None
        self._load()

    def _load(self) -> None:
        if not self.path or not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                self._items.append(HistoryEntry(**json.loads(line)))

    def append(self, entry: HistoryEntry) -> None:
        self._items.append(deepcopy(entry))
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "id": entry.id,
                            "date": entry.date,
                            "event": entry.event,
                            "change": entry.change,
                            "cause": entry.cause,
                            "significance": entry.significance,
                            "consequence": entry.consequence,
                            "revision": entry.revision,
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
