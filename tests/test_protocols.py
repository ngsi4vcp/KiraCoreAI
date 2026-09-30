import unittest

from kiracore.pulse import pulse_for_turn
from kiracore.session import SessionManager
from kiracore.validation import OutputValidator


class ProtocolTests(unittest.TestCase):
    def test_authorization_requires_exact_prefix(self) -> None:
        self.assertTrue(SessionManager.authorize("~1 продолжение"))
        self.assertFalse(SessionManager.authorize(" ~1 продолжение"))
        self.assertFalse(SessionManager.authorize("Алек ~1"))

    def test_pulse_is_deterministic(self) -> None:
        self.assertEqual(
            pulse_for_turn(1),
            "◈ ПУЛЬС:1024 | ХОД:1 | В:22 | Х²:1",
        )
        self.assertEqual(
            pulse_for_turn(7),
            "◈ ПУЛЬС:1078 | ХОД:7 | В:22 | Х²:49",
        )

    def test_validator_requires_exact_pulse(self) -> None:
        validator = OutputValidator()
        ok = validator.validate("готово\n" + pulse_for_turn(1), 1)
        bad = validator.validate("готово", 1)
        self.assertTrue(ok.valid)
        self.assertFalse(bad.valid)
