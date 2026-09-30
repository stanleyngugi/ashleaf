import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    script = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


policy = load_script("evaluate_fb16_sdt_soft_graph")
topology = load_script("analyze_fb16_graph_topology")


class FB16GraphPolicyTests(unittest.TestCase):
    def test_controls_match_flag_count_and_never_select_outside_gate(self):
        rows = [
            {"id": "a", "gate_eligible": True, "e1_confidence": 0.91},
            {"id": "b", "gate_eligible": True, "e1_confidence": 0.77},
            {"id": "c", "gate_eligible": True, "e1_confidence": 0.83},
            {"id": "d", "gate_eligible": False, "e1_confidence": 0.01},
        ]
        chosen = policy.selected_ids(rows, {"a", "c"})
        self.assertEqual(chosen["confidence_weight"], set())
        self.assertEqual(chosen["SDT_disagreement_x0p25"], {"a", "c"})
        self.assertEqual(chosen["confidence_low_x0p25"], {"b", "c"})
        for arm in policy.ARMS[1:]:
            self.assertEqual(len(chosen[arm]), 2)
            self.assertNotIn("d", chosen[arm])

    def test_bridge_cycle_and_parallel_edges(self):
        chain = [("a", "b", "ab"), ("b", "c", "bc")]
        self.assertFalse(topology.has_alternative_path(chain, 0))
        cycle = chain + [("a", "c", "ac")]
        self.assertTrue(topology.has_alternative_path(cycle, 0))
        parallel = [("a", "b", "first"), ("a", "b", "second")]
        self.assertTrue(topology.has_alternative_path(parallel, 0))


if __name__ == "__main__":
    unittest.main()
