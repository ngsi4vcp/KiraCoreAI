from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from kiracore.models import MemoryRecord
from kiracore.model_contract import ModelResponse
from kiracore.persistence_backend import RoomPersistenceBackend
from kiracore.runtime import KiraRuntime


class FakeModel:
    provider = "a2-test"

    def list_models(self, query=""):
        return []

    def generate(self, request):
        return ModelResponse(
            text="Ответ A2.1",
            provider=request.provider,
            model=request.model,
        )


class DurableRoomGateway:
    """Тестовая заглушка Room gateway с повторным открытием."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.state = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {
                "core_state": None,
                "sessions": {},
                "manifests": {},
                "messages": [],
                "memory": {},
                "history": [],
                "operations": {},
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _flush(self) -> None:
        self.path.write_text(
            json.dumps(self.state, ensure_ascii=False),
            encoding="utf-8",
        )

    def saveCoreState(self, payload):
        self.state["core_state"] = json.loads(payload)
        self._flush()

    def loadCoreState(self):
        value = self.state["core_state"]
        return None if value is None else json.dumps(value)

    def saveSession(self, payload):
        value = json.loads(payload)
        self.state["sessions"][value["session_id"]] = value
        self._flush()

    def listSessions(self):
        return json.dumps(
            sorted(
                self.state["sessions"].values(),
                key=lambda item: item["updated_at"],
                reverse=True,
            )
        )

    def saveConversationManifest(self, payload):
        value = json.loads(payload)
        self.state["manifests"][value["session_id"]] = value
        self._flush()

    def listConversationManifests(self):
        return json.dumps(
            sorted(
                self.state["manifests"].values(),
                key=lambda item: item["updated_at"],
                reverse=True,
            )
        )

    def appendConversationMessage(self, payload):
        value = json.loads(payload)
        self.state["messages"] = [
            item for item in self.state["messages"] if item["id"] != value["id"]
        ]
        self.state["messages"].append(value)
        self._flush()

    def recentConversation(self, session_id, limit):
        if limit <= 0:
            return "[]"
        values = [
            item
            for item in self.state["messages"]
            if item["session_id"] == session_id
        ]
        values.sort(key=lambda item: item["timestamp"], reverse=True)
        values = list(reversed(values[:limit]))
        return json.dumps(values)

    def deleteConversation(self, session_id):
        self.state["messages"] = [
            item
            for item in self.state["messages"]
            if item["session_id"] != session_id
        ]
        self.state["manifests"].pop(session_id, None)
        self._flush()

    def saveMemory(self, payload):
        value = json.loads(payload)
        self.state["memory"][value["id"]] = value
        self._flush()

    def listMemory(self):
        return json.dumps(list(self.state["memory"].values()))

    def appendHistory(self, payload):
        value = json.loads(payload)
        self.state["history"].append(value)
        self._flush()

    def listHistory(self):
        return json.dumps(self.state["history"])

    def saveOperation(self, payload):
        value = json.loads(payload)
        self.state["operations"][value["operation_id"]] = value
        self._flush()

    def loadOperation(self, operation_id):
        value = self.state["operations"].get(operation_id)
        return None if value is None else json.dumps(value)

    def listOperations(self):
        return json.dumps(
            list(reversed(list(self.state["operations"].values())))
        )

    def close(self):
        return None


class AndroidPersistenceBackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source_root = Path(__file__).parents[1]
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "GENOME").mkdir()
        (self.root / "GENOME" / "genome.txt").write_text(
            (self.source_root / "GENOME" / "genome.txt").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        self.gateway_path = self.root / "room-gateway-fixture.json"
        self.gateway = DurableRoomGateway(self.gateway_path)
        self.backend = RoomPersistenceBackend(self.gateway)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_a2_store_integration_and_restart_readback(self) -> None:
        runtime = KiraRuntime.start(self.root, backend=self.backend)
        manifest = runtime.create_session("a2-test", "embedded/a2-test")

        response = runtime.run(
            manifest.session_id,
            "~1 A2 integration",
            FakeModel(),
            "a2-test",
            "embedded/a2-test",
        )
        self.assertEqual(response.text, "Ответ A2.1")

        runtime.memory_store.add_candidate(
            MemoryRecord(
                id="memory-a2",
                type="fact",
                content="A2.1 candidate",
                source="test",
            )
        )
        approved = runtime.approve_memory(
            manifest.session_id,
            "memory-a2",
        )
        self.assertEqual(approved.status, "approved")

        persisted_conversation = self.backend.recent_conversation(
            manifest.session_id,
            10,
        )
        self.assertEqual(
            [item["role"] for item in persisted_conversation],
            ["user", "assistant"],
        )
        persisted_operations = self.backend.list_operations()
        self.assertEqual(len(persisted_operations), 1)
        self.assertEqual(
            persisted_operations[0]["phase"],
            "COMPLETED",
        )
        self.assertTrue(self.backend.list_history())
        persisted_memory = {
            item["id"]: item for item in self.backend.list_memory()
        }
        self.assertEqual(
            persisted_memory["memory-a2"]["status"],
            "approved",
        )

        self.assertFalse(any((self.root / "DATA").rglob("*.json")))
        self.assertFalse(any((self.root / "DATA").rglob("*.jsonl")))

        self.gateway.close()
        reopened_gateway = DurableRoomGateway(self.gateway_path)
        reopened_backend = RoomPersistenceBackend(reopened_gateway)
        restarted = KiraRuntime.start(self.root, backend=reopened_backend)
        resumed = restarted.resume_session(manifest.session_id)
        self.assertIsNotNone(resumed)
        self.assertEqual(
            resumed.session_id,
            manifest.session_id,
        )
        self.assertEqual(
            len(restarted.conversation_store.recent(manifest.session_id)),
            2,
        )
        self.assertEqual(
            [record.status for record in restarted.memory_store.approved()],
            ["approved"],
        )
        self.assertEqual(
            restarted.last_operation.phase,
            "COMPLETED",
        )

        restarted.conversation_store.delete(manifest.session_id)
        self.assertEqual(
            restarted.conversation_store.recent(manifest.session_id),
            [],
        )
        self.assertEqual(
            len(restarted.memory_store.approved()),
            1,
        )

    def test_store_rejects_two_canonical_backends(self) -> None:
        from kiracore.persistence import JsonPersistence
        from kiracore.stores import StateStore

        with self.assertRaises(ValueError):
            StateStore(
                JsonPersistence(self.root / "sessions"),
                backend=self.backend,
            )


if __name__ == "__main__":
    unittest.main()
