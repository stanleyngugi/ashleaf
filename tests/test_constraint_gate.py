import unittest

from scroll_lab.constraint_gate import decide_relative_constraint


class ConstraintGateTests(unittest.TestCase):
    def _decide(self, **overrides):
        options = dict(answered=True, predicted_dw=1, e1_confidence=.8,
                       both_normals_valid=True, normal_chord_dot_min=.8,
                       registration_verified=True)
        options.update(overrides)
        return decide_relative_constraint(**options)

    def test_accept_requires_both_numeric_signals_and_registration(self):
        self.assertEqual(self._decide().action, "accept")
        frame = self._decide(registration_verified=False)
        self.assertEqual((frame.action, frame.reason, frame.numeric_eligible),
                         ("review", "FRAME_REGISTRATION_UNVERIFIED", True))

    def test_tangent_is_not_claimed_as_same_winding(self):
        decision = self._decide(normal_chord_dot_min=.2)
        self.assertEqual((decision.action, decision.reason),
                         ("withhold", "CHORD_TANGENTIAL_TO_SHEET"))

    def test_borderline_or_low_confidence_goes_to_review(self):
        self.assertEqual(self._decide(normal_chord_dot_min=.6).reason,
                         "CHORD_ALIGNMENT_BORDERLINE")
        self.assertEqual(self._decide(e1_confidence=.5).reason, "E1_CONFIDENCE_LOW")

    def test_zero_and_unanswered_are_withheld(self):
        self.assertEqual(self._decide(predicted_dw=0).reason, "ZERO_RELATIVE_PROPOSAL")
        self.assertEqual(self._decide(answered=False, predicted_dw=None,
                                      e1_confidence=None).reason, "E1_UNANSWERED")

    def test_invalid_signal_is_rejected(self):
        with self.assertRaises(ValueError):
            self._decide(normal_chord_dot_min=float("nan"))


if __name__ == "__main__":
    unittest.main()
