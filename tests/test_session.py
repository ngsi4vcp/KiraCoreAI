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
    def generate(
        self,
        rendered_context: str,
        task: str,
    ) -> str:
        return "Ответ среды\n" + pulse_for_turn(
            1,
            revision=22,
            series=1000,
        )


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
            output = manager.run_turn(
                session.session_id,
                "проверка",
                FakeHost(),
                FakeModel(),
            )
            self.assertTrue(
                output.endswith(
                    pulse_for_turn(1, revision=22, series=1000),
                ),
            )
            snapshot = manager.persistence.load(session.session_id)
            self.assertEqual(snapshot["turn"], 1)
            self.assertTrue(snapshot["authorized_alek"])
            self.assertEqual(snapshot["runtime_status"], "waiting")

    def test_running_state_is_persisted_before_model_call(self) -> None:
        root = Path(__file__).parents[1]
        genome = GenomeLoader(expected_revision=22).load_active(root)

        class FailingModel:
            def generate(
                self,
                rendered_context: str,
                task: str,
            ) -> str:
                raise RuntimeError("модель недоступна")

        with tempfile.TemporaryDirectory() as tmp:
            persistence = JsonPersistence(tmp)
            manager = SessionManager(
                genome,
                StateStore(),
                MemoryStore(),
                HistoryStore(),
                persistence=persistence,
            )
            session = manager.start("~1 старт")
            with self.assertRaises(RuntimeError):
                manager.run_turn(
                    session.session_id,
                    "проверка",
                    FakeHost(),
                    FailingModel(),
                )
            snapshot = persistence.load(session.session_id)
            self.assertEqual(snapshot["turn"], 1)
            self.assertEqual(snapshot["runtime_status"], "running")
            self.assertNotEqual(snapshot["updated_at"], snapshot["created_at"])
