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


class InMemoryRoomGateway:
    """Контрактный stand-in для Android Room gateway."""

    def __init__(self) -> None:
        self.core_state = None
        self.sessions = {}
        self.manifests = {}
        self.messages = []
        self.memory = {}
        self.history = []
        self.operations = {}

    def saveCoreState(self, payload):
        self.core_state = json.loads(payload)

    def loadCoreState(self):
        return None if self.core_state is None else json.dumps(self.core_state)

    def saveSession(self, payload):
        value = json.loads(payload)
        self.sessions[value["session_id"]] = value

    def listSessions(self):
        return json.dumps(
            sorted(
                self.sessions.values(),
                key=lambda item: item["updated_at"],
                reverse=True,
            )
        )

    def saveConversationManifest(self, payload):
        value = json.loads(payload)
        self.manifests[value["session_id"]] = value

    def listConversationManifests(self):
        return json.dumps(
            sorted(
                self.manifests.values(),
                key=lambda item: item["updated_at"],
                reverse=True,
            )
        )

    def appendConversationMessage(self, payload):
        value = json.loads(payload)
        self.messages = [
            item for item in self.messages if item["id"] != value["id"]
        ]
        self.messages.append(value)

    def recentConversation(self, session_id, limit):
        if limit <= 0:
            return "[]"
        values = [
            item
            for item in self.messages
            if item["session_id"] == session_id
        ]
        values.sort(key=lambda item: item["timestamp"], reverse=True)
        values = list(reversed(values[:limit]))
        return json.dumps(values)

    def deleteConversation(self, session_id):
        self.messages = [
            item for item in self.messages if item["session_id"] != session_id
        ]
        self.manifests.pop(session_id, None)

    def saveMemory(self, payload):
        value = json.loads(payload)
        self.memory[value["id"]] = value

    def listMemory(self):
        return json.dumps(list(self.memory.values()))

    def appendHistory(self, payload):
        value = json.loads(payload)
        self.history.append(value)

    def listHistory(self):
        return json.dumps(self.history)

    def saveOperation(self, payload):
        value = json.loads(payload)
        self.operations[value["operation_id"]] = value

    def loadOperation(self, operation_id):
        value = self.operations.get(operation_id)
        return None if value is None else json.dumps(value)

    def listOperations(self):
        values = sorted(
            self.operations.values(),
            key=lambda item: item["updated_at"],
            reverse=True,
        )
        return json.dumps(values)

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
        self.gateway = InMemoryRoomGateway()
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

        self.assertEqual(
            [item["role"] for item in self.gateway.messages],
            ["user", "assistant"],
        )
        self.assertEqual(
            self.gateway.operations[next(iter(self.gateway.operations))]["phase"],
            "COMPLETED",
        )
        self.assertTrue(self.gateway.history)
        self.assertEqual(
            self.gateway.memory["memory-a2"]["status"],
            "approved",
        )

        self.assertFalse(any((self.root / "DATA").rglob("*.json")))
        self.assertFalse(any((self.root / "DATA").rglob("*.jsonl")))

        restarted = KiraRuntime.start(self.root, backend=self.backend)
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
