import pathlib
import sys
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sample_priority_api.workflow import summarize_work_items


class SystemFlowTests(unittest.TestCase):
    def test_end_to_end_summary_flow(self):
        payload = [
            {"id": "A-1", "title": "Handle incident", "priority": "highest"},
            {"id": "A-2", "title": "Refine backlog", "priority": "med"},
            {"id": "A-3", "title": "Clean archive", "priority": "low"},
            {"id": "A-4", "title": "Unknown input", "priority": "someday"},
        ]

        result = summarize_work_items(payload)

        self.assertEqual(result["summary"]["total"], 4)
        self.assertEqual(result["summary"]["high"], 1)
        self.assertEqual(result["summary"]["medium"], 2)
        self.assertEqual(result["summary"]["low"], 1)
        self.assertEqual(result["items"][3]["priority"], "medium")


if __name__ == "__main__":
    unittest.main()
