#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLM inference layer for internal architecture analysis generation.

This module generates LLM prompts from internal spec facts and creates
a template spec-inferences.json with placeholders for the skill layer
to populate via actual LLM inference.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from spec_analyzer._utils import read_json, write_json


LLM_INFERENCE_SYSTEM_PROMPT = """You are an architecture analyst. Given the following codebase facts (JSON), produce:
1. Module responsibilities: for each module, a 1-3 sentence description of its responsibility based on its name, public API, and dependencies
2. Runtime flows: 3-5 key runtime sequences as Mermaid sequenceDiagram format

IMPORTANT RULES:
- Only describe what is supported by the provided facts
- If a module's purpose is unclear from facts alone, state "insufficient data"
- Do NOT invent architectural details not present in the facts
- Mark each section with <!-- LLM-INFERRED: section_name -->
- Use the module names and paths exactly as provided - do not rename anything
"""

LLM_INFERENCE_USER_PROMPT_TEMPLATE = """Given the following codebase facts:

{facts_json}

Produce a JSON object with this exact structure:
{{
  "module_responsibilities": {{
    "module_path": "1-3 sentence description of what this module does, based on its name, public API, and dependencies"
  }},
  "runtime_flows": [
    {{
      "name": "flow name",
      "description": "1-2 sentence description of this runtime flow",
      "mermaid": "```mermaid\\nsequenceDiagram\\n    participant X\\n    participant Y\\n    X->>Y: message\\n```"
    }}
  ],
  "inference_metadata": {{
    "facts_version": "version from facts file",
    "modules_analyzed": N,
    "entities_analyzed": N,
    "confidence_notes": "any areas where inference was uncertain"
  }}
}}

Only output valid JSON. If you cannot determine a module's responsibility, use "Insufficient data to determine responsibility."
"""


def build_inference_prompt_from_facts_data(facts_data: dict) -> tuple[str, str]:
    """Build system and user prompts from an in-memory facts dict."""
    context = generate_inference_context_from_facts_data(facts_data)
    facts_json = json.dumps(context, indent=2, ensure_ascii=False)

    system_prompt = LLM_INFERENCE_SYSTEM_PROMPT
    user_prompt = LLM_INFERENCE_USER_PROMPT_TEMPLATE.format(facts_json=facts_json)

    return system_prompt, user_prompt


def build_inference_prompt(facts_path: Path) -> tuple[str, str]:
    """Build system and user prompts from facts file."""
    facts_data = read_json(facts_path)
    if facts_data is None:
        raise FileNotFoundError(f"Facts file not found: {facts_path}")
    return build_inference_prompt_from_facts_data(facts_data)


def generate_inference_context_from_facts_data(facts_data: dict | None) -> dict:
    """Generate condensed LLM context from an in-memory facts dict."""
    if facts_data is None:
        return {}

    modules_summary = []
    for module in facts_data.get("modules", []):
        modules_summary.append({
            "name": module.get("name"),
            "path": module.get("path"),
            "kind": module.get("kind"),
        })

    api_summary = {}
    for module_name, apis in facts_data.get("api_surface", {}).items():
        api_summary[module_name] = apis

    context = {
        "version": facts_data.get("version"),
        "generated_at": facts_data.get("generated_at"),
        "scan_scope": facts_data.get("scan_scope"),
        "source_files_count": facts_data.get("source_files_count"),
        "modules": modules_summary,
        "api_surface": api_summary,
        "entities": facts_data.get("entities", []),
        "tech_stack": facts_data.get("tech_stack", []),
    }

    return context


def generate_inference_context(facts_path: Path) -> dict:
    """Generate condensed context from facts file for LLM injection."""
    facts_data = read_json(facts_path)
    return generate_inference_context_from_facts_data(facts_data)


def parse_inference_response(response_text: str) -> dict:
    """Parse LLM inference response JSON.

    Args:
        response_text: Raw text response from LLM

    Returns:
        Parsed JSON dict or empty structure if parsing fails
    """
    try:
        # Try to extract JSON from markdown code blocks
        text = response_text.strip()
        if text.startswith("```"):
            # Remove markdown code block markers
            lines = text.split("\n")
            # Remove first and last line (```json and ```)
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        return json.loads(text)
    except json.JSONDecodeError as e:
        warnings.warn(f"Failed to parse LLM response as JSON: {e}")
        return {}


def write_inference_output(output_path: Path, inferences: dict) -> None:
    """Write inference results to output JSON file.

    Args:
        output_path: Path to spec-inferences.json
        inferences: Inference data dict
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_path, inferences)


def build_inference_template_from_facts(facts_data: dict) -> dict:
    """Build a conservative inference template with heuristic fallbacks.

    Real LLM output can overwrite these values later, but overview generation
    should still surface a useful architecture narrative when no extra process
    file exists.
    """
    modules = facts_data.get("modules", [])
    entities = facts_data.get("entities", [])
    responsibilities = {
        str(module.get("name") or "unknown"): infer_module_responsibility(module, facts_data)
        for module in modules
    }
    flows = infer_runtime_flows(facts_data)
    confidence_notes = (
        "基于模块名、公开 API、依赖边和实体信息做静态推断；如果 reverse-spec skill 注入真实 LLM 结果，"
        "应优先采用外部推断覆盖此模板。"
    )

    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inference_metadata": {
            "facts_version": facts_data.get("version"),
            "modules_analyzed": len(modules),
            "entities_analyzed": len(entities),
            "confidence_notes": confidence_notes,
            "llm_model_used": None,
            "prompt_injected": False,
            "source": "heuristic-fallback",
        },
        "module_responsibilities": responsibilities or {
            "__PLACEHOLDER__": "Run the skill with an LLM to populate this field"
        },
        "runtime_flows": flows,
        "llm_raw_response": None,
    }


def infer_module_responsibility(module: dict, facts_data: dict) -> str:
    """Infer a conservative module responsibility from static facts."""
    name = str(module.get("name") or "unknown")
    path = str(module.get("path") or "")
    kind = str(module.get("kind") or "module")
    exports = list((facts_data.get("api_surface") or {}).get(name, []))
    lowered = f"{name} {path}".lower()

    hints = []
    if any(token in lowered for token in ("test", "spec")):
        hints.append("负责测试或验证相关行为")
    if any(token in lowered for token in ("main", "cli", "entry", "app")):
        hints.append("充当程序入口或编排启动流程")
    if any(token in lowered for token in ("api", "route", "router", "controller")):
        hints.append("承接接口或路由暴露")
    if any(token in lowered for token in ("service", "workflow", "task", "job")):
        hints.append("封装核心流程或服务编排")
    if any(token in lowered for token in ("model", "schema", "entity", "dto")):
        hints.append("定义数据模型或结构化契约")
    if any(token in lowered for token in ("config", "setting")):
        hints.append("集中管理配置和运行参数")
    if any(token in lowered for token in ("util", "helper", "common")):
        hints.append("提供通用工具能力")
    if any(token in lowered for token in ("repo", "repository", "store", "db")):
        hints.append("处理持久化或数据访问")

    if exports:
        preview = "、".join(exports[:4])
        hints.append(f"对外主要暴露 `{preview}` 等接口")

    if not hints:
        normalized_path = (path or name).replace("\\", "/")
        hints.append(f"当前识别为 `{kind}`，但仅能从静态结构确认其位于 `{normalized_path}`")

    return "；".join(hints[:3]) + "。"


def infer_runtime_flows(facts_data: dict) -> list[dict]:
    """Infer a few runtime flows from dependency structure."""
    modules = facts_data.get("modules", [])
    if not modules:
        return []

    by_name = {str(module.get("name") or ""): module for module in modules if module.get("name")}
    incoming: dict[str, int] = {name: 0 for name in by_name}
    for module in modules:
        for dep in module.get("deps", []):
            if dep in incoming:
                incoming[dep] += 1

    preferred = sorted(
        by_name.values(),
        key=lambda item: (
            -int(_looks_like_entry(item)),
            _module_priority(item),
            int(_looks_like_test(item)),
            incoming.get(str(item.get("name") or ""), 0),
            -len(item.get("deps", [])),
        ),
    )
    flows = []
    for module in preferred[:3]:
        chain = [str(module.get("name") or "unknown")]
        visited = set(chain)
        current = module
        while current.get("deps"):
            next_candidates = [dep for dep in current.get("deps", []) if dep in by_name and dep not in visited]
            if not next_candidates:
                break
            next_name = sorted(next_candidates, key=lambda dep: len(by_name[dep].get("deps", [])), reverse=True)[0]
            chain.append(next_name)
            visited.add(next_name)
            current = by_name[next_name]
            if len(chain) >= 4:
                break

        mermaid_lines = ["```mermaid", "sequenceDiagram"]
        mermaid_lines.append('    participant Caller as "调用方"')
        for index, name in enumerate(chain, 1):
            mermaid_lines.append(f'    participant M{index} as "{name}"')
        mermaid_lines.append('    Caller->>M1: 触发入口 / 调用公开接口')
        for index in range(len(chain) - 1):
            mermaid_lines.append(f"    M{index + 1}->>M{index + 2}: 委托下游能力")
        mermaid_lines.append(f'    M{len(chain)}-->>Caller: 返回结果 / 状态')
        mermaid_lines.append("```")
        flows.append(
            {
                "name": f"{chain[0]} 驱动链路",
                "description": " -> ".join(chain),
                "mermaid": "\n".join(mermaid_lines),
                "steps": [],
            }
        )
    return flows


def _looks_like_entry(module: dict) -> bool:
    marker = f"{module.get('name', '')} {module.get('path', '')}".lower()
    return any(token in marker for token in ("main", "cli", "app", "index", "server", "entry"))


def _looks_like_test(module: dict) -> bool:
    marker = f"{module.get('name', '')} {module.get('path', '')}".lower()
    return "test" in marker or "spec" in marker


def _module_priority(module: dict) -> int:
    path = str(module.get("path") or "").replace("\\", "/").lower()
    if path.startswith("src/"):
        return 0
    if path.startswith("app/"):
        return 1
    if path.startswith("examples/"):
        return 2
    if path.startswith("tests/"):
        return 3
    return 4


def run_inference_phase(
    facts_path: Path | None = None,
    output_path: Path | None = None,
    prompt_output_path: Path | None = None,
    facts_data: dict | None = None,
) -> dict:
    """Run inference phase: generate prompts and template structure.

    Note: This function does NOT call any LLM API. It prepares:
    1. prompt content for the skill layer
    2. an inference template / heuristic fallback structure

    Args:
        facts_path: Path to spec-facts.json
        output_path: Optional path to spec-inferences.json (template)
        prompt_output_path: Optional path to inference-prompt.md
        facts_data: Optional in-memory facts dict

    Returns:
        Dict containing prompt content and template structure
    """
    if facts_data is None:
        if facts_path is None:
            raise ValueError("Either facts_path or facts_data must be provided")
        facts_data = read_json(facts_path)
    if facts_data is None:
        raise FileNotFoundError(f"Facts file not found: {facts_path}")

    if prompt_output_path is None and output_path is not None:
        prompt_output_path = output_path.parent / "inference-prompt.md"

    # Build prompts
    system_prompt, user_prompt = build_inference_prompt_from_facts_data(facts_data)

    prompt_content = f"""<!-- INFERENCE-PROMPT: LLM prompt for architecture inference -->
<!-- Generated: {datetime.now(timezone.utc).isoformat()} -->
<!-- Facts source: {facts_path or '[in-memory]'} -->

# System Prompt

{LLM_INFERENCE_SYSTEM_PROMPT}

# User Prompt

{user_prompt}
"""
    if prompt_output_path is not None:
        prompt_output_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_output_path.write_text(prompt_content, encoding="utf-8")

    template = build_inference_template_from_facts(facts_data)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_inference_output(output_path, template)

    return {
        "prompt_path": prompt_output_path,
        "inference_template_path": output_path,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "template": template,
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate LLM inference prompts from internal spec facts"
    )
    parser.add_argument(
        "--facts-path",
        type=Path,
        default=None,
        help="Path to spec-facts.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for spec-inferences.json template",
    )

    args = parser.parse_args()

    # Resolve paths
    facts_path = args.facts_path.resolve() if args.facts_path else None
    output_path = args.output.resolve() if args.output else None

    print(f"Facts path: {facts_path or '[required via --facts-path]'}")
    print(f"Output path: {output_path or '[in-memory only]'}")

    if facts_path is None or not facts_path.exists():
        print("Error: --facts-path is required and must exist", file=sys.stderr)
        return 1

    try:
        result = run_inference_phase(
            facts_path=facts_path,
            output_path=output_path,
        )

        print(f"\nInference phase setup complete!")
        print(f"Prompt file: {result['prompt_path'] or '[in-memory only]'}")
        print(f"Template file: {result['inference_template_path'] or '[in-memory only]'}")
        print(f"Modules in template: {result['template']['inference_metadata']['modules_analyzed']}")
        print(f"Entities in template: {result['template']['inference_metadata']['entities_analyzed']}")
        print("\nNOTE: This script generates prompts and templates only.")
        print("      The actual LLM inference is performed by the skill layer.")

        return 0
    except Exception as e:
        print(f"Error during inference phase setup: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
