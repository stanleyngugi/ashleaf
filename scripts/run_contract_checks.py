#!/usr/bin/env python3
"""Run the dependency-free contract checks used by E0001."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tests.test_contracts import ContractTests


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ContractTests)
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
