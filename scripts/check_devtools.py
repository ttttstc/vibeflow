#!/usr/bin/env python3
"""
Check Chrome DevTools MCP availability for UI feature testing.

Reads feature-list.json to determine if the project has UI features
(any feature with "ui": true). If so, verifies that the Chrome DevTools
MCP server is likely available by checking for a running Chrome/Chromium
process with remote debugging enabled.

This is a pre-flight check — it cannot guarantee MCP connectivity, but it
catches the most common failure mode (no browser with debugging port).

Usage:
    python check_devtools.py <path/to/feature-list.json>
    python check_devtools.py <path/to/feature-list.json> --feature <id>

Exit codes:
    0 — no UI features, or Chrome DevTools appears available
    1 — UI features exist but Chrome DevTools is not detected
"""

import argparse
import json
import os
import platform
import subprocess
import sys


def has_ui_features(path: str, feature_id: int = None) -> list[dict]:
    """
    Return list of UI features from feature-list.json.

    Args:
        path: Path to feature-list.json
        feature_id: If given, only check this specific feature

    Returns:
        List of feature dicts where ui=true
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    ui_features = [
        feat for feat in features
        if isinstance(feat, dict) and feat.get("ui") is True
    ]

    if feature_id is not None:
        ui_features = [f for f in ui_features if f.get("id") == feature_id]

    return ui_features


def detect_chrome_debug_port() -> dict:
    """
    Detect whether a Chrome/Chromium process with remote debugging is running.

    Returns:
        dict with keys:
        - "available": bool
        - "method": str describing how it was detected
        - "detail": str with additional info
    """
    system = platform.system()

    # Strategy 1: Check for CHROME_DEVTOOLS_MCP_PORT or similar env hints
    for env_key in ("CHROME_DEVTOOLS_MCP_PORT", "CHROME_REMOTE_DEBUGGING_PORT"):
        port = os.environ.get(env_key)
        if port:
            return {
                "available": True,
                "method": "env",
                "detail": f"{env_key}={port}",
            }

    # Strategy 2: Check for running Chrome/Chromium with --remote-debugging-port
    try:
        if system == "Windows":
            # Use tasklist + findstr — avoids needing wmic
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/FO", "LIST"],
                capture_output=True, text=True, timeout=5,
            )
            if "chrome.exe" in result.stdout.lower():
                return {
                    "available": True,
                    "method": "process",
                    "detail": "chrome.exe process found",
                }
        else:
            # Unix: ps + grep
            result = subprocess.run(
                ["sh", "-c", "ps aux | grep -i 'chrome\\|chromium' | grep -v grep"],
                capture_output=True, text=True, timeout=5,
            )
            if result.stdout.strip():
                return {
                    "available": True,
                    "method": "process",
                    "detail": "Chrome/Chromium process found",
                }
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return {
        "available": False,
        "method": "none",
        "detail": "No Chrome/Chromium with remote debugging detected",
    }


def check_devtools(path: str, feature_id: int = None) -> tuple[list[dict], dict]:
    """
    Check Chrome DevTools MCP availability for UI features.

    Args:
        path: Path to feature-list.json
        feature_id: If given, only check for this specific feature

    Returns:
        (ui_features, detection_result)
    """
    ui_features = has_ui_features(path, feature_id)

    if not ui_features:
        return ui_features, {"available": True, "method": "skip", "detail": "No UI features"}

    detection = detect_chrome_debug_port()
    return ui_features, detection


def main():
    parser = argparse.ArgumentParser(
        description="Check Chrome DevTools MCP availability for UI features"
    )
    parser.add_argument("path", help="Path to feature-list.json")
    parser.add_argument("--feature", type=int, default=None,
                        help="Only check for this specific feature ID")
    args = parser.parse_args()

    try:
        ui_features, result = check_devtools(args.path, args.feature)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: Cannot read feature-list.json: {e}")
        sys.exit(1)

    scope = f" for feature {args.feature}" if args.feature else ""

    if not ui_features:
        print(f"No UI features{scope} — Chrome DevTools MCP check skipped.")
        sys.exit(0)

    ui_titles = [f"  - #{f.get('id')}: {f.get('title', '?')}" for f in ui_features]
    print(f"UI features requiring Chrome DevTools MCP{scope}:")
    for t in ui_titles:
        print(t)

    if result["available"]:
        print(f"\nCHROME DEVTOOLS: AVAILABLE (detected via {result['method']}: {result['detail']})")
        sys.exit(0)
    else:
        print(f"\nCHROME DEVTOOLS: NOT DETECTED")
        print(f"  {result['detail']}")
        print()
        print("To resolve:")
        print("  1. Launch Chrome/Chromium with: --remote-debugging-port=9222")
        print("  2. Or set env: CHROME_DEVTOOLS_MCP_PORT=9222")
        print("  3. Ensure the Chrome DevTools MCP server is configured in your IDE/agent")
        print()
        print("UI features cannot be functionally tested without Chrome DevTools MCP.")
        sys.exit(1)


if __name__ == "__main__":
    main()
