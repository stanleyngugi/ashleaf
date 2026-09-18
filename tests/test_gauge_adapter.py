import unittest

from scroll_lab.gauge_adapter import export_gauge_adapter
from scroll_lab.winding import RelativeConstraint, solve_bfs


class GaugeAdapterTests(unittest.TestCase):
    def test_output_contract_and_node_order(self):
        solution = solve_bfs([RelativeConstraint("a", "b", 1)])
        output = export_gauge_adapter(
            solution,
            {"b": {"p": [20, 0, 10], "confidence": 0.8},
             "a": {"p": [0, 0, 10], "confidence": 0.9}},
            name="fixture",
        )
        self.assertEqual(output["points_xyz"], [[0.0, 0.0, 10.0], [20.0, 0.0, 10.0]])
        self.assertEqual(output["winding"], [0, 1])
        self.assertEqual(output["conf"], [0.9, 0.8])

    def test_missing_nodes_are_rejected(self):
        solution = solve_bfs([RelativeConstraint("a", "b", 1)])
        with self.assertRaises(ValueError):
            export_gauge_adapter(solution, {"a": {"p": [0, 0, 0]}}, name="fixture")
