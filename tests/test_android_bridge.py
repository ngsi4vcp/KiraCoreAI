import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

BRIDGE_ROOT = Path(__file__).parents[1] / "android" / "app" / "src" / "main" / "python"
if str(BRIDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(BRIDGE_ROOT))

import android_bridge  # noqa: E402


class AndroidBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        android_bridge.shutdown()
        self.source_root = Path(__file__).parents[1]
        self.tmp = tempfile.TemporaryDirectory()
        self.runtime_root = Path(self.tmp.name)
        genome_dir = self.runtime_root / "GENOME"
        genome_dir.mkdir(parents=True)
        shutil.copy2(
            self.source_root / "GENOME" / "genome.txt",
            genome_dir / "genome.txt",
        )

    def tearDown(self) -> None:
        android_bridge.shutdown()
        self.tmp.cleanup()

    def test_full_a0_bridge_contract(self) -> None:
        initialized = android_bridge.initialize(str(self.runtime_root))
        self.assertIn('"status": "ready"', initialized)
        self.assertIn('"genome_revision": 22', initialized)
        self.assertIn(
            '"genome_sha256": "dde7ce4b640f9dbcbeed6201559fb118849058e25ceccb9befa663e8ce6b726e"',
            initialized,
        )

        loaded = android_bridge.load_genome()
        self.assertIn('"status": "loaded"', loaded)

        manifest = android_bridge.create_session(
            "a0-test",
            "embedded/a0-test",
        )
        session_id = json.loads(manifest)["session_id"]

        result = json.loads(
            android_bridge.run_test_turn(
                session_id,
                "A0 диагностический тестовый ход.",
            )
        )
        self.assertEqual(
            result["response"]["text"],
            "Тестовый ход A0 успешно выполнен.",
        )
        self.assertEqual(result["runtime_state"]["turn"], 1)
        self.assertEqual(result["runtime_state"]["pulse"]["value"], 1024)

        state = json.loads(android_bridge.get_runtime_state())
        self.assertEqual(state["active_session_id"], session_id)
        self.assertEqual(state["turn"], 1)

        diagnostics = json.loads(android_bridge.diagnostics())
        self.assertEqual(diagnostics["core_version"], "0.1.0a1")
        self.assertEqual(diagnostics["python_version"].split(".")[0], "3")

        self.assertEqual(android_bridge.shutdown(), "Кира:Ядро остановлено")
        self.assertEqual(android_bridge.health(), "Кира:Ядро не инициализировано")

        restarted = json.loads(android_bridge.initialize(str(self.runtime_root)))
        self.assertEqual(restarted["genome_revision"], 22)
        restored_state = json.loads(android_bridge.get_runtime_state())
        self.assertEqual(restored_state["turn"], 1)
        self.assertEqual(restored_state["active_session_id"], session_id)


if __name__ == "__main__":
    unittest.main()
