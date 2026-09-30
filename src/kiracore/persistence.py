from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
import os
import tempfile

from .models import SessionState


class JsonPersistence:
    """Атомарное сохранение состояния сессии без доступа к геному."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, state: SessionState) -> Path:
        target = self.directory / f"{state.session_id}.json"
        payload = json.dumps(asdict(state), ensure_ascii=False, indent=2, sort_keys=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=self.directory,
            delete=False,
            prefix=f".{state.session_id}.",
        ) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, target)
        return target

    def load(self, session_id: str) -> dict:
        target = self.directory / f"{session_id}.json"
        return json.loads(target.read_text(encoding="utf-8"))
