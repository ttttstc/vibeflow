"""Priority normalization workflow used to validate the VibeFlow delivery path."""

from __future__ import annotations

from collections import Counter

_PRIORITY_MAP = {
    "urgent": "high",
    "highest": "high",
    "high": "high",
    "h": "high",
    "medium": "medium",
    "med": "medium",
    "normal": "medium",
    "m": "medium",
    "low": "low",
    "lowest": "low",
    "l": "low",
}


def normalize_priority(label: str) -> str:
    if not isinstance(label, str) or not label.strip():
        raise ValueError("priority label must be a non-empty string")
    return _PRIORITY_MAP.get(label.strip().lower(), "medium")


def summarize_work_items(items: list[dict]) -> dict:
    if not isinstance(items, list) or not items:
        raise ValueError("items must be a non-empty list")

    normalized_items = []
    counts = Counter()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("each item must be a mapping")
        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("each item requires a non-empty title")
        raw_priority = item.get("priority", "medium")
        priority = normalize_priority(raw_priority)
        normalized_item = {
            "title": title.strip(),
            "priority": priority,
        }
        if "id" in item:
            normalized_item["id"] = item["id"]
        normalized_items.append(normalized_item)
        counts[priority] += 1

    return {
        "items": normalized_items,
        "summary": {
            "total": len(normalized_items),
            "high": counts.get("high", 0),
            "medium": counts.get("medium", 0),
            "low": counts.get("low", 0),
        },
    }
