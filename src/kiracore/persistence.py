from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
import os
import re
import tempfile
from typing import Any

from .errors import KiraCoreError
from .models import SessionState
from .persistence_backend import PersistenceBackend

_SESSION_ID_RE = re.compile(r"^[a-f0-9]{32}$")


class JsonPersistence:
    """Атомарное сохранение состояния сессии без доступа к геному."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _target(self, session_id: str) -> Path:
        if not _SESSION_ID_RE.fullmatch(session_id):
            raise KiraCoreError("Недопустимый идентификатор сессии.")
        return self.directory / f"{session_id}.json"

    def save(self, state: SessionState) -> Path:
        target = self._target(state.session_id)
        return self.save_path(
            target,
            asdict(state),
            prefix=f".{state.session_id}.",
        )

    def save_path(
        self,
        target: str | Path,
        payload: dict[str, Any],
        prefix: str = ".tmp.",
    ) -> Path:
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=target.parent,
                delete=False,
                prefix=prefix,
            ) as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
                temp_path = Path(handle.name)
            os.replace(temp_path, target)
            return target
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    def load(self, session_id: str) -> dict[str, Any]:
        target = self._target(session_id)
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise KiraCoreError(
                f"Сохранённая сессия не найдена: {session_id}"
            ) from exc


class CoreStatePersistence:
    """Хранит агрегированный снимок актуального состояния Кира:Ядра."""

    def __init__(
        self,
        root: str | Path,
        backend: PersistenceBackend | None = None,
    ) -> None:
        self.backend = backend
        self.path = Path(root) / "core_state.json"
        self.persistence = JsonPersistence(self.path.parent)

    def save(self, payload: dict[str, Any]) -> Path | None:
        if self.backend is not None:
            self.backend.save_core_state(payload)
            return None
        return self.persistence.save_path(
            self.path,
            payload,
            prefix=".core_state.",
        )

    def load(self) -> dict[str, Any] | None:
        if self.backend is not None:
            return self.backend.load_core_state()
        if not self.path.exists():
            return None
        return json.loads(self.path.read_text(encoding="utf-8"))
