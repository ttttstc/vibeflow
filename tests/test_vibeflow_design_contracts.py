#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_module(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, str(ROOT / "scripts" / filename))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


paths_module = load_module("vibeflow_paths.py", "vibeflow_paths_design_contract_tests")
contracts_module = load_module("vibeflow_design_contracts.py", "vibeflow_design_contracts_tests")


default_state = paths_module.default_state
save_state = paths_module.save_state
path_contract = paths_module.path_contract
load_design_execution_contracts = contracts_module.load_design_execution_contracts


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestDesignExecutionContracts:
    def test_load_design_execution_contracts_parses_build_and_feature_contracts(self, tmp_path):
        state = default_state(tmp_path, topic="contract-parser")
        save_state(tmp_path, state)
        contract = path_contract(tmp_path, state)

        write_text(
            contract["artifacts"]["design"],
            """# Parser Fixture

## 3. Build Contract
```toml
project = "contract-parser"
language = "python"
test_framework = "pytest"
coverage_tool = "pytest-cov"
mutation_tool = "mutmut"
constraints = ["Use design contracts as the build handoff."]
assumptions = ["Sections map cleanly to feature work packets."]
```

## 4. Key Feature Designs

### 4.1 Feature: Deliver login flow (fr-001)

#### 4.1.6 Implementation Contract
```toml
feature_id = 1
title = "Deliver login flow"
category = "delivery"
description = "Implement the login path."
priority = "high"
dependencies = []
file_scope = ["src/login.py", "tests/test_login.py"]
verification_commands = ["python -m pytest tests/test_login.py -q"]
verification_steps = ["Run the login test and verify it passes."]
done_criteria = ["The login path is implemented and verified."]
requirements_refs = ["fr-001"]
integration_points = ["src/login.py:submit_login"]
autopilot_commands = ["python -m pytest tests/test_login.py -q"]
```

### 4.2 Feature: Record audit events (FR-002)

#### 4.2.6 Implementation Contract
```toml
feature_id = 2
title = "Record audit events"
category = "delivery"
description = "Implement the audit path."
priority = "medium"
dependencies = [1]
file_scope = ["src/audit.py", "tests/test_audit.py"]
verification_commands = ["python -m pytest tests/test_audit.py -q"]
verification_steps = ["Run the audit test and verify it passes."]
done_criteria = ["Audit events are recorded and verified."]
integration_points = ["src/audit.py:record_event"]
autopilot_commands = ["python -m pytest tests/test_audit.py -q"]
```
""",
        )

        result = load_design_execution_contracts(tmp_path, state)

        assert result["detected"] is True
        assert result["enabled"] is True
        assert result["issues"] == []
        assert result["build_contract"]["project"] == "contract-parser"
        assert result["build_contract"]["tech_stack"]["language"] == "python"
        assert len(result["features"]) == 2
        assert result["features"][0]["design_section"] == "4.1"
        assert result["features"][0]["requirements_refs"] == ["FR-001"]
        assert result["features"][0]["build_contract_ref"].endswith("design.md#build-contract")
        assert result["features"][1]["requirements_refs"] == ["FR-002"]

    def test_load_design_execution_contracts_requires_build_contract_when_detected(self, tmp_path):
        state = default_state(tmp_path, topic="missing-build-contract")
        save_state(tmp_path, state)
        contract = path_contract(tmp_path, state)

        write_text(
            contract["artifacts"]["design"],
            """# Missing Build Contract Fixture

## 4. Key Feature Designs

### 4.1 Feature: Broken feature (FR-001)

#### 4.1.6 Implementation Contract
```toml
feature_id = 1
title = "Broken feature"
priority = "high"
dependencies = []
file_scope = ["src/broken.py"]
verification_commands = ["python -c \\"print('ok')\\""]
```
""",
        )

        result = load_design_execution_contracts(tmp_path, state)

        assert result["detected"] is True
        assert result["enabled"] is False
        assert "Design execution contracts require exactly one Build Contract TOML block." in result["issues"]
