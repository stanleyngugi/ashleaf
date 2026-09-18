import unittest

from scroll_lab.winding import RelativeConstraint, score_solution, solve_bfs


class WindingTests(unittest.TestCase):
    def test_clean_chain_is_recovered(self):
        edges = [
            RelativeConstraint("a", "b", 1),
            RelativeConstraint("b", "c", 1),
            RelativeConstraint("c", "d", -2),
        ]
        solution = solve_bfs(edges)
        self.assertEqual(solution.labels, {"a": 0, "b": 1, "c": 2, "d": 0})
        self.assertEqual(solution.contradictions, ())
        self.assertEqual(score_solution(solution, edges)["satisfied_fraction"], 1.0)

    def test_cycle_conflict_is_reported(self):
        edges = [
            RelativeConstraint("a", "b", 1, evidence_id="ab"),
            RelativeConstraint("b", "c", 1, evidence_id="bc"),
            RelativeConstraint("a", "c", 3, evidence_id="ac"),
        ]
        solution = solve_bfs(edges)
        self.assertEqual(len(solution.contradictions), 1)
        self.assertLess(score_solution(solution, edges)["satisfied_fraction"], 1.0)

    def test_confidence_order_is_deterministic(self):
        edges = [
            RelativeConstraint("a", "b", 1, confidence=0.1, evidence_id="weak"),
            RelativeConstraint("a", "b", 2, confidence=0.9, evidence_id="strong"),
        ]
        solution = solve_bfs(edges, confidence_order=True)
        self.assertEqual(solution.labels["b"], 2)

    def test_empty_graph(self):
        solution = solve_bfs([])
        self.assertEqual(solution.component_count, 0)
        self.assertEqual(score_solution(solution, [])['satisfied_fraction'], 1.0)
