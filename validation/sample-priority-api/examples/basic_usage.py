import pathlib
import sys
from pprint import pprint

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sample_priority_api.workflow import summarize_work_items

payload = [
    {"id": 1, "title": "Ship release", "priority": "urgent"},
    {"id": 2, "title": "Review docs", "priority": "normal"},
    {"id": 3, "title": "Archive screenshots", "priority": "low"},
]

pprint(summarize_work_items(payload))
