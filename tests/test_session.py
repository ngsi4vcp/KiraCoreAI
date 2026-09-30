import tempfile
import unittest
from pathlib import Path

from kiracore.genome import GenomeLoader
from kiracore.models import OperationalContext
from kiracore.persistence import JsonPersistence
from kiracore.pulse import pulse_for_turn
from kiracore.session import SessionManager
from kiracore.stores import HistoryStore, MemoryStore, StateStore


class FakeHost:
    def render_context(self, context: OperationalContext) -> str:
        return f"G{context.genome_revision}:{context.task}"


class FakeModel:
    def generate(self, rendered_context: str, task: str) -> str:
        return "Ответ среды\n" + pulse_for_turn(1)


class SessionTests(unittest.TestCase):
    def test_session_runs_without_model_specific_state_ownership(self) -> None:
        root = Path(__file__).parents[1]
        genome = GenomeLoader(expected_revision=22).load_active(root)
        with tempfile.TemporaryDirectory() as tmp:
            manager = SessionManager(
                genome,
                StateStore(),
                MemoryStore(),
                HistoryStore(),
                persistence=JsonPersistence(tmp),
            )
            session = manager.start("~1 старт", {"host": "test"})
            output = manager.run_turn(session.session_id, "проверка", FakeHost(), FakeModel())
            self.assertTrue(output.endswith(pulse_for_turn(1)))
            snapshot = manager.persistence.load(session.session_id)
            self.assertEqual(snapshot["turn"], 1)
            self.assertTrue(snapshot["authorized_alek"])
