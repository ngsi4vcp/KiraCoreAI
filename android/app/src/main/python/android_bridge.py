from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from kiracore.model_contract import ModelResponse
from kiracore.runtime import KiraRuntime

_RUNTIME: KiraRuntime | None = None

EXPECTED_GENOME_REVISION = 22
EXPECTED_GENOME_SHA256 = "05e2d7bd86047c34103c079fc0a3d9845d471de9"
CORE_VERSION = "0.1.0a1"


class _A0TestModel:
    provider = "a0-test"

    def list_models(self, query: str = ""):
        return []

    def generate(self, request):
        return ModelResponse(
            text="Тестовый ход A0 успешно выполнен.",
            provider=request.provider,
            model=request.model,
        )


def _runtime_required() -> KiraRuntime:
    if _RUNTIME is None:
        raise RuntimeError("Кира:Ядро ещё не инициализировано.")
    return _RUNTIME


def initialize(project_root: str) -> str:
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = KiraRuntime.start(
            project_root=Path(project_root),
            expected_revision=EXPECTED_GENOME_REVISION,
            expected_sha256=EXPECTED_GENOME_SHA256,
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


def load_genome() -> str:
    runtime = _runtime_required()
    loaded = runtime.genome
    return json.dumps(
        {
            "status": "loaded",
            "genome_revision": loaded.revision,
            "genome_sha256": loaded.sha256,
        },
        ensure_ascii=False,
    )


def create_session(
    provider: str,
    model: str,
    identity_id: str | None = None,
) -> str:
    runtime = _runtime_required()
    manifest = runtime.create_session(
        provider=provider,
        model=model,
        identity_id=identity_id,
    )
    return json.dumps(asdict(manifest), ensure_ascii=False)


def get_runtime_state() -> str:
    runtime = _runtime_required()
    return json.dumps(runtime.core_state, ensure_ascii=False)


def run_test_turn(session_id: str, task: str) -> str:
    runtime = _runtime_required()
    response = runtime.run(
        session_id=session_id,
        task=task,
        model=_A0TestModel(),
        provider="a0-test",
        model_id="embedded/a0-test",
    )
    return json.dumps(
        {
            "response": asdict(response),
            "runtime_state": runtime.core_state,
        },
        ensure_ascii=False,
    )


def diagnostics() -> str:
    return json.dumps(
        {
            "core_version": CORE_VERSION,
            "python_version": sys.version.split()[0],
            "expected_genome_revision": EXPECTED_GENOME_REVISION,
            "expected_genome_sha256": EXPECTED_GENOME_SHA256,
            "providers": ["OpenRouter", "Gemini"],
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


def shutdown() -> str:
    global _RUNTIME
    _RUNTIME = None
    return "Кира:Ядро остановлено"
