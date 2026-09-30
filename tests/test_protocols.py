import unittest

from kiracore.model_contract import ModelResponse
from kiracore.pulse import pulse_for_turn, pulse_stamp
from kiracore.session import SessionManager
from kiracore.validation import OutputValidator


class ProtocolTests(unittest.TestCase):
    def test_authorization_requires_marker_as_prefix_token(self) -> None:
        self.assertTrue(SessionManager.authorize("~1"))
        self.assertTrue(SessionManager.authorize("~1 продолжение"))
        self.assertFalse(SessionManager.authorize("~10 продолжение"))
        self.assertFalse(SessionManager.authorize("~1foo"))
        self.assertFalse(SessionManager.authorize(" ~1 продолжение"))
        self.assertFalse(SessionManager.authorize("Алек ~1"))

    def test_pulse_is_deterministic(self) -> None:
        self.assertEqual(
            pulse_for_turn(1, revision=22, series=1000),
            "◈ ПУЛЬС:1024 | ХОД:1 | В:22 | Х²:1",
        )
        self.assertEqual(
            pulse_for_turn(7, revision=22, series=1000),
            "◈ ПУЛЬС:1078 | ХОД:7 | В:22 | Х²:49",
        )
        self.assertEqual(
            pulse_stamp(1, 22, 1000).key,
            "1000:22:1:1024",
        )

    def test_validator_does_not_require_model_generated_pulse(self) -> None:
        response = ModelResponse(
            text="обычный ответ",
            provider="openrouter",
            model="example/model",
        )
        self.assertTrue(OutputValidator().validate(response).valid)
