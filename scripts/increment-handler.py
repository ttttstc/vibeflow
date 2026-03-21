#!/usr/bin/env python3
"""
VibeFlow Increment Handler — 处理增量请求协议。

增量处理流程：
1. 读取 .vibeflow/increment-queue.txt 获取待处理增量列表
2. 对每个增量：
   a. 读取 .vibeflow/increment-request-{id}.json 获取增量详情
   b. 验证增量目标（哪个功能/阶段）
   c. 将增量应用到适当的产物（SRS/Design/UCD/feature-list）
   d. 更新 feature-list.json 以反映更改的范围
   e. 将增量记录到 .vibeflow/phase-history.json
3. 完成后清空 increment-queue.txt 或标记已处理

增量类型：
- add_feature:     在 feature-list.json 中追加新功能
- modify_feature:  修改现有功能的描述/优先级/依赖
- deprecate_feature: 将功能标记为 deprecated
- update_doc:      更新 SRS/Design/UCD 文档中的需求

Usage:
    python scripts/increment-handler.py [--project-root <path>]

Exit codes:
    0 — 所有增量处理成功
    1 — 处理失败（见错误信息）
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


INCREMENT_QUEUE_FILE = ".vibeflow/increment-queue.txt"
PHASE_HISTORY_FILE = ".vibeflow/phase-history.json"
FEATURE_LIST_FILE = "feature-list.json"


def read_queue(project_root: Path) -> list[str]:
    """读取增量队列，返回增量 ID 列表。"""
    queue_path = project_root / INCREMENT_QUEUE_FILE
    if not queue_path.exists():
        return []
    with open(queue_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    return lines


def write_queue(project_root: Path, ids: list[str]) -> None:
    """写回增量队列（处理完成后调用，清除已处理的 ID）。"""
    queue_path = project_root / INCREMENT_QUEUE_FILE
    with open(queue_path, "w", encoding="utf-8") as f:
        f.write("# VibeFlow Increment Queue\n")
        for rid in ids:
            f.write(f"{rid}\n")


def load_increment_request(project_root: Path, inc_id: str) -> dict:
    """加载单个增量请求文件。"""
    # 尝试多种命名格式
    for basename in [
        f"increment-request-{inc_id}.json",
        f"increment-{inc_id}.json",
        f"increment_request_{inc_id}.json",
    ]:
        path = project_root / ".vibeflow" / basename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(f"Increment request file not found for id: {inc_id}")


def load_phase_history(project_root: Path) -> list[dict]:
    """加载 phase history 列表。"""
    hist_path = project_root / PHASE_HISTORY_FILE
    if not hist_path.exists():
        return []
    with open(hist_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_phase_history(project_root: Path, history: list[dict]) -> None:
    """保存 phase history。"""
    hist_path = project_root / PHASE_HISTORY_FILE
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_feature_list(project_root: Path) -> dict:
    """加载 feature-list.json。"""
    fl_path = project_root / FEATURE_LIST_FILE
    if not fl_path.exists():
        raise FileNotFoundError(f"feature-list.json not found at {fl_path}")
    with open(fl_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_feature_list(project_root: Path, data: dict) -> None:
    """保存 feature-list.json。"""
    fl_path = project_root / FEATURE_LIST_FILE
    with open(fl_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def process_add_feature(inc: dict, fl: dict) -> str:
    """处理 add_feature 增量：追加新功能到 feature-list.json。"""
    new_id = max([f["id"] for f in fl.get("features", [])], default=0) + 1
    new_feature = {
        "id": new_id,
        "title": inc.get("title", f"New feature {new_id}"),
        "description": inc.get("description", ""),
        "priority": inc.get("priority", "medium"),
        "status": "failing",
        "dependencies": inc.get("dependencies", []),
        "verification_steps": inc.get("verification_steps", []),
    }
    if inc.get("ui"):
        new_feature["ui"] = inc["ui"]
    if inc.get("wave"):
        new_feature["wave"] = inc["wave"]

    fl.setdefault("features", []).append(new_feature)
    return f"Added feature #{new_id}: {new_feature['title']}"


def process_modify_feature(inc: dict, fl: dict) -> str:
    """处理 modify_feature 增量：修改现有功能。"""
    target_id = inc.get("feature_id")
    for feat in fl.get("features", []):
        if feat.get("id") == target_id:
            for key in ["title", "description", "priority", "dependencies", "verification_steps"]:
                if key in inc:
                    feat[key] = inc[key]
            return f"Modified feature #{target_id}"
    return f"WARNING: feature #{target_id} not found, nothing modified"


def process_deprecate_feature(inc: dict, fl: dict) -> str:
    """处理 deprecate_feature 增量：标记功能为 deprecated。"""
    target_id = inc.get("feature_id")
    for feat in fl.get("features", []):
        if feat.get("id") == target_id:
            feat["deprecated"] = True
            feat["deprecated_reason"] = inc.get("reason", "superseded by increment")
            return f"Deprecated feature #{target_id}"
    return f"WARNING: feature #{target_id} not found"


def process_update_doc(inc: dict, project_root: Path) -> str:
    """处理 update_doc 增量：更新 SRS/Design/UCD 文档。"""
    doc_type = inc.get("doc_type")  # "srs", "design", "ucd"
    doc_path = project_root / "docs" / "plans"

    if doc_type == "srs":
        matches = list(doc_path.glob("*-srs.md"))
    elif doc_type == "design":
        matches = list(doc_path.glob("*-design.md"))
    elif doc_type == "ucd":
        matches = list(doc_path.glob("*-ucd.md"))
    else:
        return f"Unknown doc_type: {doc_type}"

    if not matches:
        return f"No {doc_type} document found in docs/plans/"
    # 更新最新的文档
    target = sorted(matches)[-1]
    original_content = target.read_text(encoding="utf-8")
    patch = inc.get("patch", "")
    new_content = original_content + f"\n\n## 增量更新 ({datetime.now().strftime('%Y-%m-%d')})\n\n{patch}\n"
    target.write_text(new_content, encoding="utf-8")
    return f"Updated {target.name}"


def record_increment(project_root: Path, inc_id: str, inc: dict, result: str) -> None:
    """将增量记录到 phase-history.json。"""
    history = load_phase_history(project_root)
    history.append({
        "timestamp": datetime.now().isoformat(),
        "increment_id": inc_id,
        "type": inc.get("type"),
        "scope": inc.get("scope"),
        "reason": inc.get("reason"),
        "result": result,
    })
    save_phase_history(project_root, history)


def process_increment(project_root: Path, inc_id: str) -> tuple[bool, str]:
    """
    处理单个增量请求。

    Returns:
        (success, message)
    """
    try:
        inc = load_increment_request(project_root, inc_id)
    except FileNotFoundError as e:
        return False, str(e)

    inc_type = inc.get("type")
    scope = inc.get("scope", "")

    # 加载 feature-list（如果需要修改）
    fl = None
    if inc_type in ("add_feature", "modify_feature", "deprecate_feature"):
        try:
            fl = load_feature_list(project_root)
        except FileNotFoundError:
            return False, "feature-list.json not found"

    # 执行增量
    if inc_type == "add_feature":
        result = process_add_feature(inc, fl)
    elif inc_type == "modify_feature":
        result = process_modify_feature(inc, fl)
    elif inc_type == "deprecate_feature":
        result = process_deprecate_feature(inc, fl)
    elif inc_type == "update_doc":
        result = process_update_doc(inc, project_root)
    else:
        result = f"Unknown increment type: {inc_type}"

    # 保存 feature-list
    if fl is not None:
        save_feature_list(project_root, fl)

    # 记录到历史
    record_increment(project_root, inc_id, inc, result)

    return True, result


def main():
    parser = argparse.ArgumentParser(description="VibeFlow Increment Handler")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Path to project root (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    # 读取队列
    queue_ids = read_queue(project_root)
    if not queue_ids:
        print("Increment queue is empty — nothing to process.")
        sys.exit(0)

    print(f"Processing {len(queue_ids)} increment(s)...")

    processed = []
    failed = []

    for inc_id in queue_ids:
        print(f"\n[{inc_id}] Processing...")
        success, msg = process_increment(project_root, inc_id)
        print(f"  -> {msg}")
        if success:
            processed.append(inc_id)
        else:
            failed.append((inc_id, msg))

    # 清除已处理的 ID（保留失败的用于重试）
    remaining = [i for i in queue_ids if i not in processed]
    write_queue(project_root, remaining)

    # 摘要
    print(f"\nDone: {len(processed)} succeeded, {len(failed)} failed.")
    if failed:
        print("\nFailed:")
        for inc_id, msg in failed:
            print(f"  [{inc_id}] {msg}")
        sys.exit(1)
    else:
        print("All increments processed successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
