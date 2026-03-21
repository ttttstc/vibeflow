import pathlib
import sys
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sample_priority_api.workflow import normalize_priority, summarize_work_items


class NormalizePriorityTests(unittest.TestCase):
    def test_known_priority_aliases_are_normalized(self):
        self.assertEqual(normalize_priority("urgent"), "high")
        self.assertEqual(normalize_priority("Normal"), "medium")
        self.assertEqual(normalize_priority("lowest"), "low")

    def test_unknown_priority_falls_back_to_medium(self):
        self.assertEqual(normalize_priority("someday"), "medium")

    def test_empty_priority_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_priority("  ")


class SummarizeWorkItemsTests(unittest.TestCase):
    def test_summary_counts_normalized_priorities(self):
        result = summarize_work_items(
            [
                {"id": 1, "title": "Ship release", "priority": "urgent"},
                {"id": 2, "title": "Tidy docs", "priority": "normal"},
                {"id": 3, "title": "Archive notes", "priority": "lowest"},
            ]
        )
        self.assertEqual(result["summary"], {"total": 3, "high": 1, "medium": 1, "low": 1})
        self.assertEqual(result["items"][0]["priority"], "high")

    def test_missing_title_is_rejected(self):
        with self.assertRaises(ValueError):
            summarize_work_items([{"priority": "high"}])


if __name__ == "__main__":
    unittest.main()
