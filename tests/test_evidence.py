"""학습 기록과 재계산 결과의 의미를 비교하고 환경별 부동소수점 차이를 허용한다."""
import json
from pathlib import Path
import unittest
from src.export_evidence import build
from src.toy_lora import fingerprint


class EvidenceTests(unittest.TestCase):
    def test_recorded_cpu_experiment(self):
        saved = json.loads((Path(__file__).parents[1] / "examples/execution.json").read_text())
        actual = build()
        self.assertEqual(saved["scope"], actual["scope"])
        self.assertEqual(saved["experiment"]["config"], actual["experiment"]["config"])
        self.assertEqual(saved["experiment"]["checkpoint_hash"], fingerprint(saved["experiment"]["checkpoint"]))
        self.assertEqual(saved["experiment"]["base_hash_before"], actual["experiment"]["base_hash_before"])
        self.assertAlmostEqual(saved["experiment"]["holdout_mse_after"], actual["experiment"]["holdout_mse_after"], places=12)
        for recorded, recalculated in zip(saved["inference"]["output"], actual["inference"]["output"]):
            self.assertAlmostEqual(recorded, recalculated, places=12)
