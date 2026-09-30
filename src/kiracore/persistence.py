from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
import os
import re
import tempfile

from .errors import KiraCoreError
from .models import SessionState

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
        payload = json.dumps(
            asdict(state),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.directory,
                delete=False,
                prefix=f".{state.session_id}.",
            ) as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
                temp_path = Path(handle.name)
            os.replace(temp_path, target)
            return target
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    def load(self, session_id: str) -> dict:
        target = self._target(session_id)
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise KiraCoreError(
                f"Сохранённая сессия не найдена: {session_id}"
            ) from exc
