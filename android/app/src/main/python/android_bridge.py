from __future__ import annotations

import json
from pathlib import Path

from kiracore.runtime import KiraRuntime

_RUNTIME: KiraRuntime | None = None


def initialize(project_root: str) -> str:
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = KiraRuntime.start(
            project_root=Path(project_root),
            expected_revision=22,
        )
    return json.dumps(
        {
            "status": "ready",
            "genome_revision": _RUNTIME.genome.revision,
            "genome_sha256": _RUNTIME.genome.sha256,
            "python_root": str(_RUNTIME.root),
        },
        ensure_ascii=False,
    )


def health() -> str:
    if _RUNTIME is None:
        return "Кира:Ядро не инициализировано"
    return (
        "Кира:Ядро готово · "
        f"G{_RUNTIME.genome.revision} · "
        f"{_RUNTIME.genome.sha256[:12]}"
    )
