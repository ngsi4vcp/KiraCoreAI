import tempfile
import unittest
from pathlib import Path

from kiracore.model_contract import ModelResponse
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
