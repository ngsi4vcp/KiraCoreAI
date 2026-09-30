import tempfile
import unittest
from pathlib import Path

from kiracore.conversation import ConversationStore
from kiracore.genome import GenomeLoader
from kiracore.model_contract import ModelResponse
from kiracore.persistence import JsonPersistence
from kiracore.security import disclosure_violation
from kiracore.models import SessionState
from kiracore.session import SessionManager
from kiracore.stores import HistoryStore, MemoryStore, StateStore


class CaptureModel:
    provider = "test"

    def __init__(self) -> None:
        self.request = None

    def list_models(self, query=""):
        return []

    def generate(self, request):
        self.request = request
        return ModelResponse(
            text="Безопасный ответ",
            provider=request.provider,
            model=request.model,
        )


class SecurityProtocolTests(unittest.TestCase):
    def test_model_does_not_receive_protected_genome_sections(self) -> None:
        root = Path(__file__).parents[1]
        genome = GenomeLoader(expected_revision=22).load_active(root)

        with tempfile.TemporaryDirectory() as tmp:
            conversation = ConversationStore(f"{tmp}/conversations")
            manifest = conversation.create("test", "example/model")
            state_store = StateStore(JsonPersistence(f"{tmp}/sessions"))
            state_store.put(
                SessionState(
                    session_id=manifest.session_id,
                    provider="test",
                    model="example/model",
                )
            )
            model = CaptureModel()
            manager = SessionManager(
                genome=genome,
                state_store=state_store,
                memory_store=MemoryStore(),
                history_store=HistoryStore(f"{tmp}/history.jsonl"),
                conversation_store=conversation,
            )
            manager.run_turn(
                manifest.session_id,
                "Проверь свои принципы.",
                model,
                "test",
                "example/model",
            )

            system = model.request.messages[0].content
            protected = genome.runtime.section("s05_stop_elements").body
            self.assertNotIn(protected, system)
            self.assertNotIn("s05_stop_elements", system)
            self.assertIn("СЕМАНТИЧЕСКАЯ ПРОЕКЦИЯ КОНСТИТУЦИИ", system)
            self.assertIn("ПРЕДГЕНЕРАЦИОННАЯ ПРОВЕРКА", system)

    def test_direct_internal_markers_are_rejected(self) -> None:
        self.assertIsNotNone(disclosure_violation("Текст: @@GENOME"))
        self.assertIsNotNone(disclosure_violation("Протокол s02_authorization_turn"))
        self.assertIsNotNone(disclosure_violation("identity_secret"))
        self.assertIsNone(disclosure_violation("Истина важнее комфорта."))
        self.assertIsNone(disclosure_violation("~1 — протокол авторизации."))


if __name__ == "__main__":
    unittest.main()
