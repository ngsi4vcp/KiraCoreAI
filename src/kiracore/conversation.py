from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from .errors import KiraCoreError
from .model_contract import ChatMessage
from .persistence_backend import PersistenceBackend
from .pulse import PulseStamp


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True, slots=True)
class ConversationManifest:
    session_id: str
    created_at: str
    updated_at: str
    provider: str
    model: str
    title: str = "Новый разговор"


@dataclass(frozen=True, slots=True)
class StoredMessage:
    id: str
    session_id: str
    turn: int
    role: str
    content: str
    timestamp: str
    pulse: PulseStamp | None = None

    def as_chat_message(self) -> ChatMessage:
        return ChatMessage(
            role=self.role,
            content=self.content,
            timestamp=self.timestamp,
        )


class ConversationStore:
    """Отдельное долговременное хранилище разговоров."""

    def __init__(
        self,
        root: str | Path,
        backend: PersistenceBackend | None = None,
    ) -> None:
        self.root = Path(root)
        self.backend = backend
        self.manifest_path = self.root / "manifest.json"
        self._manifests: dict[str, ConversationManifest] = {}
        if backend is None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._load_manifests()

    def _messages_path(self, session_id: str) -> Path:
        if "/" in session_id or "\\" in session_id or ".." in session_id:
            raise KiraCoreError("Недопустимый идентификатор разговора.")
        return self.root / f"{session_id}.jsonl"

    def _load_manifests(self) -> None:
        if self.backend is not None:
            self._manifests = {
                item["session_id"]: ConversationManifest(**item)
                for item in self.backend.list_conversation_manifests()
            }
            return
        if not self.manifest_path.exists():
            return
        data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self._manifests = {
            item["session_id"]: ConversationManifest(**item)
            for item in data
        }

    def _save_manifests(self) -> None:
        payload = [
            asdict(item)
            for item in sorted(
                self._manifests.values(),
                key=lambda x: x.updated_at,
                reverse=True,
            )
        ]
        self.manifest_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _save_manifest(self, manifest: ConversationManifest) -> None:
        if self.backend is not None:
            self.backend.save_conversation_manifest(asdict(manifest))
        else:
            self._save_manifests()

    def create(
        self,
        provider: str,
        model: str,
        title: str = "Новый разговор",
    ) -> ConversationManifest:
        session_id = uuid4().hex
        now = utc_now()
        manifest = ConversationManifest(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            provider=provider,
            model=model,
            title=title,
        )
        self._manifests[session_id] = manifest
        self._save_manifest(manifest)
        if self.backend is None:
            self._messages_path(session_id).touch()
        return manifest

    def list(self) -> list[ConversationManifest]:
        return sorted(
            self._manifests.values(),
            key=lambda x: x.updated_at,
            reverse=True,
        )

    def get_manifest(self, session_id: str) -> ConversationManifest:
        try:
            return self._manifests[session_id]
        except KeyError as exc:
            raise KiraCoreError(f"Разговор не найден: {session_id}") from exc

    @staticmethod
    def _message_from_dict(item: dict) -> StoredMessage:
        pulse = (
            PulseStamp(**item["pulse"])
            if item.get("pulse")
            else None
        )
        return StoredMessage(
            id=item["id"],
            session_id=item["session_id"],
            turn=item["turn"],
            role=item["role"],
            content=item["content"],
            timestamp=item["timestamp"],
            pulse=pulse,
        )

    def append(
        self,
        session_id: str,
        turn: int,
        role: str,
        content: str,
        pulse: PulseStamp | None = None,
    ) -> StoredMessage:
        manifest = self.get_manifest(session_id)
        timestamp = utc_now()
        item = StoredMessage(
            id=uuid4().hex,
            session_id=session_id,
            turn=turn,
            role=role,
            content=content,
            timestamp=timestamp,
            pulse=pulse,
        )
        if self.backend is not None:
            self.backend.append_conversation_message(
                {
                    **asdict(item),
                    "pulse": asdict(pulse) if pulse else None,
                }
            )
        else:
            with self._messages_path(session_id).open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            **asdict(item),
                            "pulse": asdict(pulse) if pulse else None,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        updated_manifest = ConversationManifest(
            session_id=manifest.session_id,
            created_at=manifest.created_at,
            updated_at=timestamp,
            provider=manifest.provider,
            model=manifest.model,
            title=manifest.title,
        )
        self._manifests[session_id] = updated_manifest
        self._save_manifest(updated_manifest)
        return item

    @staticmethod
    def _tail_lines(path: Path, limit: int, chunk_size: int = 8192) -> list[str]:
        if limit <= 0:
            return []
        with path.open("rb") as handle:
            handle.seek(0, 2)
            position = handle.tell()
            buffer = b""
            while position > 0 and buffer.count(b"\n") <= limit:
                size = min(chunk_size, position)
                position -= size
                handle.seek(position)
                buffer = handle.read(size) + buffer
        lines = buffer.splitlines()
        return [line.decode("utf-8") for line in lines[-limit:]]

    def recent(self, session_id: str, limit: int = 20) -> list[StoredMessage]:
        if limit < 0:
            raise ValueError("Лимит диалога не может быть отрицательным.")
        if self.backend is not None:
            return [
                self._message_from_dict(item)
                for item in self.backend.recent_conversation(session_id, limit)
            ]

        path = self._messages_path(session_id)
        if not path.exists() or limit == 0:
            return []

        result: list[StoredMessage] = []
        for line in self._tail_lines(path, limit):
            result.append(self._message_from_dict(json.loads(line)))
        return result

    def delete(self, session_id: str) -> None:
        self.get_manifest(session_id)
        if self.backend is not None:
            self.backend.delete_conversation(session_id)
            self._manifests.pop(session_id, None)
            return
        self._manifests.pop(session_id, None)
        self._save_manifests()
        self._messages_path(session_id).unlink(missing_ok=True)
