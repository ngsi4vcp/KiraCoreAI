import tempfile
import unittest
from pathlib import Path

from kiracore.errors import UnknownModelCall
from kiracore.model_contract import ModelResponse
from kiracore.operation import OperationPhase, RecoveryState
from kiracore.runtime import KiraRuntime


class FakeModel:
    provider = "test"

    def list_models(self, query=""):
        return []

    def generate(self, request):
        return ModelResponse(
            text="Ответ runtime",
            provider=request.provider,
            model=request.model,
        )


class UnknownModel:
    provider = "unknown-test"

    def list_models(self, query=""):
        return []

    def generate(self, request):
        raise UnknownModelCall("deterministic test: external state unknown")


class RuntimeTests(unittest.TestCase):
    def test_start_loads_active_genome_and_persists_core_state(self) -> None:
        root = Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            runtime_root = Path(tmp)
            (runtime_root / "GENOME").mkdir()
            source = root / "GENOME" / "genome.txt"
            (runtime_root / "GENOME" / "genome.txt").write_text(
                source.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            runtime = KiraRuntime.start(runtime_root)
            self.assertEqual(runtime.genome.revision, 22)

            manifest = runtime.create_session("test", "example/model")
            response = runtime.run(
                manifest.session_id,
                "~1 привет",
                FakeModel(),
                "test",
                "example/model",
            )
            self.assertEqual(response.text, "Ответ runtime")
            self.assertEqual(runtime.core_state["turn"], 1)
            self.assertEqual(runtime.core_state["pulse"]["value"], 1024)
            self.assertTrue(runtime.core_state["authorized_alek"])


    def test_unknown_model_call_is_persisted_without_retry(self) -> None:
        root = Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            runtime_root = Path(tmp)
            (runtime_root / "GENOME").mkdir()
            source = root / "GENOME" / "genome.txt"
            (runtime_root / "GENOME" / "genome.txt").write_text(
                source.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            runtime = KiraRuntime.start(runtime_root)
            manifest = runtime.create_session("unknown-test", "embedded/unknown")

            with self.assertRaises(UnknownModelCall):
                runtime.run(
                    manifest.session_id,
                    "~1 unknown boundary",
                    UnknownModel(),
                    "unknown-test",
                    "embedded/unknown",
                )

            operation = runtime.core_state["operation"]
            self.assertEqual(operation["phase"], OperationPhase.UNKNOWN)
            self.assertEqual(operation["recovery_state"], RecoveryState.UNKNOWN)
            self.assertEqual(operation["checkpoint"], "model_call_unknown")
            self.assertIn("unknown", operation["error"])
            self.assertEqual(runtime.core_state["turn"], 1)
            self.assertTrue(runtime.core_state["authorized_alek"])

            restored = KiraRuntime.start(runtime_root)
            self.assertEqual(
                restored.core_state["operation"]["operation_id"],
                operation["operation_id"],
            )
            self.assertEqual(
                restored.core_state["operation"]["phase"],
                OperationPhase.UNKNOWN,
            )
