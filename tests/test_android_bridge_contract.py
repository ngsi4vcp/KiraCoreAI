from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import android_bridge


class AndroidBridgeContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        root = Path(self.tempdir.name)
        genome_source = Path(__file__).resolve().parents[1] / "GENOME" / "genome.txt"
        genome_target = root / "GENOME" / "genome.txt"
        genome_target.parent.mkdir(parents=True, exist_ok=True)
        genome_target.write_bytes(genome_source.read_bytes())
        android_bridge.initialize(str(root))

    def tearDown(self) -> None:
        android_bridge.shutdown()
        self.tempdir.cleanup()

    def test_a1_bridge_contract(self) -> None:
        genome = json.loads(android_bridge.get_genome_info())
        self.assertEqual(genome["revision"], 22)
        self.assertEqual(genome["series"], 1000)
        self.assertEqual(
            genome["sha256"],
            "dde7ce4b640f9dbcbeed6201559fb118849058e25ceccb9befa663e8ce6b726e",
        )
        self.assertGreater(genome["section_count"], 0)

        first = json.loads(android_bridge.create_session("a0-test", "embedded/a0-test"))
        second = json.loads(android_bridge.create_session("a0-test", "embedded/a0-test"))
        sessions = json.loads(android_bridge.list_sessions())
        self.assertEqual(
            {first["session_id"], second["session_id"]},
            {item["session_id"] for item in sessions},
        )
        self.assertEqual(len(sessions), 2)

        resumed = json.loads(android_bridge.resume_session(first["session_id"]))
        self.assertEqual(resumed["status"], "resumed")
        self.assertEqual(resumed["session"]["session_id"], first["session_id"])
        self.assertEqual(
            resumed["runtime_state"]["active_session_id"],
            first["session_id"],
        )
        self.assertEqual(resumed["runtime_state"]["turn"], 0)

        latest = json.loads(android_bridge.resume_session())
        self.assertEqual(latest["status"], "resumed")
        self.assertEqual(
            latest["session"]["session_id"],
            second["session_id"],
        )

        self.assertEqual(json.loads(android_bridge.get_memory()), [])
        self.assertEqual(json.loads(android_bridge.get_memory_candidates()), [])

        health = json.loads(android_bridge.check_health())
        self.assertIn(health["status"], {"READY", "UNKNOWN"})
        self.assertEqual(
            health["active_session_id"],
            second["session_id"],
        )
        self.assertEqual(health["turn"], 0)

        turn = json.loads(
            android_bridge.send_test_turn(
                first["session_id"],
                "~1 A1 bridge deterministic test",
            )
        )
        self.assertEqual(turn["response"]["provider"], "a0-test")
        self.assertIn("pulse", turn["response"]["raw_metadata"])
        self.assertEqual(turn["runtime_state"]["turn"], 1)

        conversation = json.loads(
            android_bridge.get_conversation(first["session_id"], 20)
        )
        self.assertEqual(
            [item["role"] for item in conversation],
            ["user", "assistant"],
        )
        self.assertEqual(conversation[0]["content"], "A1 bridge deterministic test")
        self.assertEqual(conversation[1]["turn"], 1)
        self.assertEqual(conversation[1]["pulse"]["value"], 1024)

        latest_after_turn = json.loads(android_bridge.resume_session())
        self.assertEqual(latest_after_turn["status"], "resumed")
        self.assertEqual(
            latest_after_turn["session"]["session_id"],
            first["session_id"],
        )


if __name__ == "__main__":
    unittest.main()
