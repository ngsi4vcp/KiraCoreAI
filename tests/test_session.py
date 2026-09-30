import tempfile
import unittest

from kiracore.conversation import ConversationStore
from kiracore.genome import GenomeLoader
from kiracore.model_contract import ModelResponse
from kiracore.persistence import JsonPersistence
from kiracore.session import SessionManager
from kiracore.stores import HistoryStore, MemoryStore, StateStore


class FakeModel:
    provider = "test"

    def list_models(self, query=""):
        return []

    def generate(self, request):
        return ModelResponse(
            text="Ответ среды",
            provider=request.provider,
            model=request.model,
        )


class SessionTests(unittest.TestCase):
    def test_session_runs_and_adds_runtime_pulse(self) -> None:
        from kiracore.models import SessionState

        root = __import__("pathlib").Path(__file__).parents[1]
        genome = GenomeLoader(expected_revision=22).load_active(root)

        with tempfile.TemporaryDirectory() as tmp:
            conversation = ConversationStore(f"{tmp}/conversations")
            manifest = conversation.create("test", "example/model")
            state_store = StateStore(JsonPersistence(f"{tmp}/sessions"))
            state_store.put(SessionState(
                session_id=manifest.session_id,
                provider="test",
                model="example/model",
            ))

            manager = SessionManager(
                genome=genome,
                state_store=state_store,
                memory_store=MemoryStore(),
                history_store=HistoryStore(f"{tmp}/history.jsonl"),
                conversation_store=conversation,
            )
            response, pulse = manager.run_turn(
                manifest.session_id,
                "~1 проверка",
                FakeModel(),
                "test",
                "example/model",
            )
            self.assertEqual(response.text, "Ответ среды")
            self.assertEqual(pulse.value, 1024)
            self.assertEqual(
                conversation.recent(manifest.session_id, 10)[-1].pulse.value,
                1024,
            )
            self.assertTrue(
                state_store.get(manifest.session_id).authorized_alek
            )
            history = HistoryStore(f"{tmp}/history.jsonl")
            self.assertEqual(len(history.recent()), 1)
            self.assertEqual(history.recent()[0].event, "Завершение хода сессии")
            self.assertIn("проверка", history.recent()[0].cause)
