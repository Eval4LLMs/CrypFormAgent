import json
import unittest
from pathlib import Path

from crypformagent.pipeline import ArtifactPipeline, load_records


ROOT = Path(__file__).resolve().parents[1]
SUPPLEMENT = ROOT.parent


class ArtifactPipelineTest(unittest.TestCase):
    def test_structured_crypir_run(self):
        records = load_records(ROOT / "examples" / "minimal_generation.json", target="spdl")
        result = ArtifactPipeline().run(records[0], "spdl")

        self.assertEqual(result.target, "spdl")
        self.assertTrue(result.selected.verification.analyzable)
        self.assertIn("protocol nonce_key_exchange", result.selected.artifact)
        self.assertEqual(result.score, 2.25)

    def test_released_dataset_record_adapter(self):
        path = SUPPLEMENT / "datasets" / "generation" / "spdl_datasets_data_eng_100.json"
        records = load_records(path, target="spdl", task="generation", limit=1)
        result = ArtifactPipeline().run(records[0], "spdl")
        report = result.to_dict()

        self.assertEqual(report["target"], "spdl")
        self.assertTrue(report["selected"]["verification"]["analyzable"])
        self.assertEqual(report["cryp_ir"]["metadata"]["task"], "generation")
        self.assertIn("source_file", report["cryp_ir"]["metadata"])

    def test_report_is_json_serializable(self):
        records = load_records(ROOT / "examples" / "minimal_generation.json", target="pv")
        result = ArtifactPipeline().run(records[0], "pv")
        encoded = json.dumps(result.to_dict(), sort_keys=True)

        self.assertIn("nonce_key_exchange", encoded)


if __name__ == "__main__":
    unittest.main()
