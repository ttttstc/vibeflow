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


def build_inference_prompt(facts_path: Path) -> tuple[str, str]:
    """Build system and user prompts from facts file.

    Args:
        facts_path: Path to spec-facts.json

    Returns:
        Tuple of (system_prompt, user_prompt) where user_prompt has facts injected
    """
    facts_data = read_json(facts_path)
    if facts_data is None:
        raise FileNotFoundError(f"Facts file not found: {facts_path}")

    # Generate condensed context for LLM
    context = generate_inference_context(facts_path)
    facts_json = json.dumps(context, indent=2, ensure_ascii=False)

    system_prompt = LLM_INFERENCE_SYSTEM_PROMPT
    user_prompt = LLM_INFERENCE_USER_PROMPT_TEMPLATE.format(facts_json=facts_json)

    return system_prompt, user_prompt


def generate_inference_context(facts_path: Path) -> dict:
    """Generate condensed context from facts file for LLM injection.

    Args:
        facts_path: Path to spec-facts.json

    Returns:
        Condensed dict with only the information LLM needs
    """
    facts_data = read_json(facts_path)
    if facts_data is None:
        return {}

    # Build condensed context - only what LLM needs
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


def run_inference_phase(
    facts_path: Path,
    output_path: Path,
    prompt_output_path: Path | None = None,
) -> dict:
    """Run inference phase: generate prompts and template structure.

    Note: This function does NOT call any LLM API. It generates:
    1. inference-prompt.md - full prompt for skill layer to use
    2. spec-inferences.json - template structure with placeholders

    Args:
        facts_path: Path to spec-facts.json
        output_path: Path to spec-inferences.json (template)
        prompt_output_path: Path to inference-prompt.md, defaults to same dir as output_path

    Returns:
        Dict containing prompt content and template structure
    """
    if prompt_output_path is None:
        prompt_output_path = output_path.parent / "inference-prompt.md"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load facts to get metadata
    facts_data = read_json(facts_path)
    if facts_data is None:
        raise FileNotFoundError(f"Facts file not found: {facts_path}")

    # Build prompts
    system_prompt, user_prompt = build_inference_prompt(facts_path)

    # Write prompt file for skill layer
    prompt_content = f"""<!-- INFERENCE-PROMPT: LLM prompt for architecture inference -->
<!-- Generated: {datetime.now(timezone.utc).isoformat()} -->
<!-- Facts source: {facts_path} -->

# System Prompt

{LLM_INFERENCE_SYSTEM_PROMPT}

# User Prompt

{user_prompt}
"""
    prompt_output_path.write_text(prompt_content, encoding="utf-8")

    # Build template structure with placeholders
    modules_analyzed = len(facts_data.get("modules", []))
    entities_analyzed = len(facts_data.get("entities", []))

    template = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inference_metadata": {
            "facts_version": facts_data.get("version"),
            "modules_analyzed": modules_analyzed,
            "entities_analyzed": entities_analyzed,
            "confidence_notes": "",
            "llm_model_used": None,
            "prompt_injected": False,
        },
        "module_responsibilities": {
            "__PLACEHOLDER__": "Run the skill with an LLM to populate this field"
        },
        "runtime_flows": [],
        "llm_raw_response": None,
    }

    # Write template
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
        default=Path(".vibeflow/analysis/spec-facts.json"),
        help="Path to spec-facts.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".vibeflow/analysis/spec-inferences.json"),
        help="Output path for spec-inferences.json template",
    )

    args = parser.parse_args()

    # Resolve paths
    facts_path = args.facts_path.resolve()
    output_path = args.output.resolve()

    print(f"Facts path: {facts_path}")
    print(f"Output path: {output_path}")

    if not facts_path.exists():
        print(f"Error: Facts file not found: {facts_path}", file=sys.stderr)
        return 1

    try:
        result = run_inference_phase(
            facts_path=facts_path,
            output_path=output_path,
        )

        print(f"\nInference phase setup complete!")
        print(f"Prompt file: {result['prompt_path']}")
        print(f"Template file: {result['inference_template_path']}")
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
