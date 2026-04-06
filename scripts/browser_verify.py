#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_viewport(value: str) -> tuple[int, int]:
    width_str, height_str = value.lower().split("x", 1)
    return int(width_str), int(height_str)


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal real-browser verification using Playwright.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--out-dir", default=".tmp/browser-verify")
    parser.add_argument("--viewport", default="1440x900")
    parser.add_argument("--timeout-ms", type=int, default=15000)
    parser.add_argument("--wait-until", default="networkidle", choices=["load", "domcontentloaded", "networkidle"])
    parser.add_argument("--expect-title-contains")
    parser.add_argument("--expect-text")
    parser.add_argument("--wait-for-selector")
    parser.add_argument("--headed", action="store_true", help="Run with a visible browser window.")
    args = parser.parse_args()

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover - environment dependent
        print(json.dumps({"ok": False, "error": f"playwright import failed: {exc}"}))
        return 2

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = out_dir / "screenshot.png"
    report_path = out_dir / "report.json"
    width, height = parse_viewport(args.viewport)

    console_messages: list[dict[str, Any]] = []
    request_failures: list[dict[str, Any]] = []
    bad_responses: list[dict[str, Any]] = []
    a11y_snapshot: Any = None
    title = ""
    final_url = args.url
    ok = True
    errors: list[str] = []
    notes: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()

        page.on(
            "console",
            lambda msg: console_messages.append(
                {
                    "type": msg.type,
                    "text": msg.text,
                    "location": msg.location,
                }
            ),
        )
        page.on(
            "requestfailed",
            lambda req: request_failures.append(
                {
                    "url": req.url,
                    "method": req.method,
                    "failure": req.failure,
                }
            ),
        )
        page.on(
            "response",
            lambda resp: bad_responses.append(
                {
                    "url": resp.url,
                    "status": resp.status,
                    "status_text": resp.status_text,
                }
            )
            if resp.status >= 400
            else None,
        )

        try:
            try:
                page.goto(args.url, wait_until=args.wait_until, timeout=args.timeout_ms)
            except PlaywrightError as exc:
                if args.wait_until == "networkidle":
                    notes.append("networkidle timed out; retried with load")
                    page.goto(args.url, wait_until="load", timeout=args.timeout_ms)
                else:
                    raise exc
            if args.wait_for_selector:
                page.wait_for_selector(args.wait_for_selector, timeout=args.timeout_ms)
            if args.expect_text:
                page.get_by_text(args.expect_text).wait_for(timeout=args.timeout_ms)
            title = page.title()
            final_url = page.url
            try:
                a11y_snapshot = page.accessibility.snapshot()
            except Exception:
                a11y_snapshot = {"available": False}

            if args.expect_title_contains and args.expect_title_contains not in title:
                ok = False
                errors.append(
                    f"title '{title}' does not contain expected substring '{args.expect_title_contains}'"
                )
        except PlaywrightError as exc:
            ok = False
            errors.append(str(exc))
        finally:
            try:
                title = title or page.title()
                final_url = page.url or final_url
                page.screenshot(path=str(screenshot_path), full_page=True)
            except Exception:
                pass
            browser.close()

    console_errors = [msg for msg in console_messages if msg["type"] == "error"]
    significant_request_failures = [
        failure for failure in request_failures if failure.get("failure") != "net::ERR_ABORTED"
    ]
    ignored_request_failures = [
        failure for failure in request_failures if failure.get("failure") == "net::ERR_ABORTED"
    ]
    if console_errors:
        ok = False
        errors.append(f"{len(console_errors)} console error(s) detected")
    if significant_request_failures:
        ok = False
        errors.append(f"{len(significant_request_failures)} request failure(s) detected")
    if ignored_request_failures:
        notes.append(f"ignored {len(ignored_request_failures)} aborted request(s)")
    if bad_responses:
        ok = False
        errors.append(f"{len(bad_responses)} bad response(s) detected")

    report = {
        "ok": ok,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": args.url,
        "final_url": final_url,
        "title": title,
        "viewport": {"width": width, "height": height},
        "screenshot": str(screenshot_path),
        "errors": errors,
        "notes": notes,
        "console": {
            "total": len(console_messages),
            "errors": len(console_errors),
            "messages": console_messages,
        },
        "network": {
            "request_failures": request_failures,
            "significant_request_failures": significant_request_failures,
            "ignored_request_failures": ignored_request_failures,
            "bad_responses": bad_responses,
        },
        "a11y_snapshot": a11y_snapshot,
    }

    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
