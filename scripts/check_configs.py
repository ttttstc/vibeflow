#!/usr/bin/env python3
"""
Check required configurations declared in feature-list.json.

Reads the 'required_configs' array and verifies:
- env: environment variable is set and non-empty
- file: file exists at the specified path and is non-empty

Supports loading a .env file before checking (--dotenv flag).

Usage:
    python check_configs.py <path/to/feature-list.json> [--feature <id>] [--dotenv <path>]

Exit codes:
    0 — all required configs present (or none declared)
    1 — one or more configs missing
"""

import argparse
import json
import os
import sys


VALID_CONFIG_TYPES = {"env", "file"}


def load_dotenv(dotenv_path: str) -> dict[str, str]:
    """
    Load a .env file and set variables into os.environ.

    Supports:
    - KEY=VALUE (unquoted)
    - KEY="VALUE" (double-quoted, strips quotes)
    - KEY='VALUE' (single-quoted, strips quotes)
    - # comments and blank lines (skipped)
    - Inline comments after unquoted values (stripped)

    Returns a dict of loaded key-value pairs.
    """
    loaded = {}
    if not os.path.isfile(dotenv_path):
        return loaded

    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Must contain '='
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if not key:
                continue
            value = value.strip()
            # Strip surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            else:
                # Strip inline comments for unquoted values
                for i, ch in enumerate(value):
                    if ch == "#" and (i == 0 or value[i - 1] == " "):
                        value = value[:i].rstrip()
                        break
            loaded[key] = value
            os.environ[key] = value

    return loaded


def check_configs(path: str, feature_id: int = None) -> tuple[list[dict], list[dict]]:
    """
    Check required configs from feature-list.json.

    Args:
        path: Path to feature-list.json
        feature_id: If given, only check configs whose required_by includes this ID

    Returns:
        (missing_configs, present_configs) — each is a list of config dicts;
        missing ones have an added 'reason' key
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    configs = data.get("required_configs", [])

    # Resolve file paths relative to the feature-list.json directory
    base_dir = os.path.dirname(os.path.abspath(path))

    # Filter by feature if specified
    if feature_id is not None:
        configs = [c for c in configs if feature_id in c.get("required_by", [])]

    missing = []
    present = []

    for config in configs:
        config_type = config.get("type", "")
        name = config.get("name", "unnamed")

        if config_type == "env":
            key = config.get("key", "")
            val = os.environ.get(key, "")
            if val:
                present.append(config)
            else:
                entry = dict(config)
                entry["reason"] = f"Environment variable '{key}' is not set or empty"
                missing.append(entry)

        elif config_type == "file":
            file_path = config.get("path", "")
            # Resolve relative paths against the feature-list.json directory
            if not os.path.isabs(file_path):
                file_path = os.path.join(base_dir, file_path)
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                present.append(config)
            else:
                entry = dict(config)
                if not os.path.exists(file_path):
                    entry["reason"] = f"File '{config.get('path', '')}' does not exist"
                elif not os.path.isfile(file_path):
                    entry["reason"] = f"Path '{config.get('path', '')}' is not a file"
                else:
                    entry["reason"] = f"File '{config.get('path', '')}' is empty"
                missing.append(entry)

        else:
            entry = dict(config)
            entry["reason"] = f"Unknown config type '{config_type}'"
            missing.append(entry)

    return missing, present


def main():
    parser = argparse.ArgumentParser(description="Check required configurations")
    parser.add_argument("path", help="Path to feature-list.json")
    parser.add_argument("--feature", type=int, default=None,
                        help="Only check configs required by this feature ID")
    parser.add_argument("--dotenv", default=None, metavar="PATH",
                        help="Load a .env file before checking (e.g., --dotenv .env)")
    args = parser.parse_args()

    # Load .env file if specified
    if args.dotenv:
        loaded = load_dotenv(args.dotenv)
        if loaded:
            print(f"Loaded {len(loaded)} variable(s) from {args.dotenv}")

    try:
        missing, present = check_configs(args.path, args.feature)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: Cannot read feature-list.json: {e}")
        sys.exit(1)

    if not missing and not present:
        scope = f" for feature {args.feature}" if args.feature else ""
        print(f"No required configs declared{scope}.")
        sys.exit(0)

    if present:
        print(f"PRESENT ({len(present)}):")
        for c in present:
            print(f"  OK: {c['name']}")

    if missing:
        print(f"\nMISSING ({len(missing)}):")
        for c in missing:
            print(f"  MISSING: {c['name']}")
            print(f"    Reason: {c['reason']}")
            if c.get("description"):
                print(f"    Description: {c['description']}")
            if c.get("check_hint"):
                print(f"    Hint: {c['check_hint']}")
            if c.get("type") == "env" and c.get("key"):
                print(f"    .env key: {c['key']}")
        sys.exit(1)

    print(f"\nAll {len(present)} required configs present.")
    sys.exit(0)


if __name__ == "__main__":
    main()
