---
name: vibeflow-reverse-spec
description: Reverse-generates Arc42 architecture spec from existing codebase (Python + TypeScript)
---

# Reverse-Generated Architecture Spec

[VibeFlow skill for automatic architecture documentation generation]

## Goal
Generate a complete Arc42-structured architecture specification from an existing codebase, including:
- Module dependency topology (Mermaid flowchart)
- Data model (Mermaid erDiagram)
- Tech stack清单
- Module responsibilities (LLM-inferred, marked <!-- LLM-INFERRED -->)
- Runtime behavior descriptions (LLM-inferred, marked <!-- LLM-INFERRED -->)

## Trigger
- Explicit: `/vibeflow-reverse-spec`
- Auto-trigger: VibeFlow detects non-empty project with no existing `docs/architecture/full-spec.md`

## Prerequisites
- Project must contain Python (.py) or TypeScript (.ts/.tsx/.js/.jsx) source files
- Non-empty project (at least 1 module detected)

## Execution Flow

### Step 1: Run Static Analysis (Layer 1)
```
Run: python scripts/spec_analyzer/runner.py --project-root {project_root}
Output: docs/architecture/.spec-facts.json
```

### Step 2: Generate LLM Prompt (Layer 2)
```
Run: python scripts/spec_analyzer/inference.py --facts-path docs/architecture/.spec-facts.json --output docs/architecture/.spec-inferences.json
Output: docs/architecture/.inference-prompt.md (prompt file for LLM)
```

### Step 3: Invoke LLM for Inference
- Read `docs/architecture/.inference-prompt.md`
- Use the prompt to call LLM with the facts JSON
- Write LLM's JSON response to `docs/architecture/.spec-inferences.json`
- Update `llm_model_used` and `llm_raw_response` fields
- Set `inference_metadata.prompt_injected: true`

### Step 4: Assemble Full Spec (Layer 3)
```
Run: python scripts/spec_analyzer/assembler.py --project-root {project_root}
Output: docs/architecture/full-spec.md
```

### Step 5: Verify Output
- Check `docs/architecture/full-spec.md` exists
- Check it contains all 12 Arc42 sections
- Module count in spec should match facts

## Output
- `docs/architecture/.spec-facts.json` — Static analysis facts
- `docs/architecture/.spec-inferences.json` — LLM inferences
- `docs/architecture/.inference-prompt.md` — LLM prompt (intermediate)
- `docs/architecture/full-spec.md` — Full Arc42 spec document

## Quality Gate
- Module graph must have > 0 nodes
- If 0 modules detected → exit with error: "No source modules detected. Ensure this is a non-empty project with Python or TypeScript source files."

## Integration
- This skill is a pre-Design step
- If `docs/architecture/full-spec.md` already exists → silently succeed (no regeneration)
- Design phase will auto-inject `full-spec.md` as context input
