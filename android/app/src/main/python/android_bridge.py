from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from kiracore.model_contract import ModelResponse
from kiracore.persistence_backend import RoomPersistenceBackend
from kiracore.runtime import KiraRuntime

_RUNTIME: KiraRuntime | None = None
_PERSISTENCE_BACKEND: RoomPersistenceBackend | None = None

EXPECTED_GENOME_REVISION = 22
EXPECTED_GENOME_SHA256 = "dde7ce4b640f9dbcbeed6201559fb118849058e25ceccb9befa663e8ce6b726e"
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


def initialize(project_root: str, room_gateway=None) -> str:
    global _RUNTIME, _PERSISTENCE_BACKEND
    if _RUNTIME is None:
        if room_gateway is not None:
            _PERSISTENCE_BACKEND = RoomPersistenceBackend(room_gateway)
        _RUNTIME = KiraRuntime.start(
            project_root=Path(project_root),
            expected_revision=EXPECTED_GENOME_REVISION,
            expected_sha256=EXPECTED_GENOME_SHA256,
            backend=_PERSISTENCE_BACKEND,
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


def get_genome_info() -> str:
    runtime = _runtime_required()
    return json.dumps(
        {
            "revision": runtime.genome.revision,
            "series": runtime.genome.series,
            "sha256": runtime.genome.sha256,
            "section_count": len(runtime.genome.document.sections),
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


def list_sessions() -> str:
    runtime = _runtime_required()
    return json.dumps(
        [asdict(item) for item in runtime.list_sessions()],
        ensure_ascii=False,
    )


def resume_session(session_id: str | None = None) -> str:
    runtime = _runtime_required()
    manifest = runtime.resume_session(session_id)
    runtime_state = runtime.core_state
    if manifest is None:
        return json.dumps(
            {
                "status": "empty",
                "session": None,
                "runtime_state": runtime_state,
            },
            ensure_ascii=False,
        )
    return json.dumps(
        {
            "status": "resumed",
            "session": asdict(manifest),
            "runtime_state": runtime_state,
        },
        ensure_ascii=False,
    )


def get_runtime_state() -> str:
    runtime = _runtime_required()
    return json.dumps(runtime.core_state, ensure_ascii=False)


def get_conversation(session_id: str, limit: int = 20) -> str:
    runtime = _runtime_required()
    messages = runtime.conversation_store.recent(session_id, limit)
    return json.dumps(
        [asdict(item) for item in messages],
        ensure_ascii=False,
    )


def get_memory() -> str:
    runtime = _runtime_required()
    return json.dumps(
        [asdict(item) for item in runtime.memory_store.approved()],
        ensure_ascii=False,
    )


def get_memory_candidates() -> str:
    runtime = _runtime_required()
    return json.dumps(
        [asdict(item) for item in runtime.memory_store.candidates()],
        ensure_ascii=False,
    )


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


def send_test_turn(session_id: str, task: str) -> str:
    return run_test_turn(session_id, task)


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


def check_health() -> str:
    runtime = _runtime_required()
    state = runtime.core_state
    status = (
        "READY"
        if state.get("runtime_status") not in {None, "error"}
        else "UNKNOWN"
    )
    return json.dumps(
        {
            "status": status,
            "runtime_status": state.get("runtime_status"),
            "active_session_id": state.get("active_session_id"),
            "turn": state.get("turn", 0),
            "pulse": state.get("pulse"),
            "operation": state.get("operation"),
        },
        ensure_ascii=False,
    )


def health() -> str:
    if _RUNTIME is None:
        return "Кира:Ядро не инициализировано"
    runtime = _RUNTIME
    return (
        "Кира:Ядро готово · "
        f"G{runtime.genome.revision} · "
        f"{runtime.genome.sha256[:12]}"
    )


def shutdown() -> str:
    global _RUNTIME, _PERSISTENCE_BACKEND
    if _PERSISTENCE_BACKEND is not None:
        close = getattr(_PERSISTENCE_BACKEND.gateway, "close", None)
        if close is not None:
            close()
    _PERSISTENCE_BACKEND = None
    _RUNTIME = None
    return "Кира:Ядро остановлено"
