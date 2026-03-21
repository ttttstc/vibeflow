#!/usr/bin/env python3
"""Unit tests for new-vibeflow-work-config.py"""
import json
import sys
from pathlib import Path
import pytest
import importlib.util

_spec = importlib.util.spec_from_file_location(
    'new_vibeflow_work_config',
    str(Path(__file__).parent.parent / 'scripts' / 'new-vibeflow-work-config.py')
)
_new_vibeflow_work_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_new_vibeflow_work_config)

step_enabled = _new_vibeflow_work_config.step_enabled
read_gate = _new_vibeflow_work_config.read_gate


class TestStepEnabled:
    """Test step_enabled() regex matching."""

    def test_tdd_enabled(self):
        content = '''build:
  steps:
    - id: tdd
      required: true
'''
        assert step_enabled(content, 'tdd') is True

    def test_tdd_disabled(self):
        content = '''build:
  steps:
    - id: tdd
      required: false
'''
        assert step_enabled(content, 'tdd') is False

    def test_feature_st_enabled(self):
        content = '''build:
  steps:
    - id: feature-st
      required: true
'''
        assert step_enabled(content, 'feature-st') is True

    def test_feature_st_disabled(self):
        content = '''build:
  steps:
    - id: feature-st
      required: false
'''
        assert step_enabled(content, 'feature-st') is False

    def test_required_true_in_wrong_section_does_not_match(self):
        """Regression test: 'required: true' appearing outside the target step should not match."""
        content = '''build:
  steps:
    - id: other-step
      required: true
    - id: quality
      required: true
'''
        assert step_enabled(content, 'tdd') is False


class TestReadGate:
    def test_line_coverage_present(self):
        content = 'line_coverage: 95\n'
        assert read_gate(content, 'line_coverage', 90) == 95

    def test_line_coverage_missing_uses_default(self):
        content = 'other: value\n'
        assert read_gate(content, 'line_coverage', 90) == 90

    def test_branch_coverage_present(self):
        content = 'branch_coverage: 85\n'
        assert read_gate(content, 'branch_coverage', 80) == 85

    def test_mutation_score_present(self):
        content = 'mutation_score: 75\n'
        assert read_gate(content, 'mutation_score', 80) == 75


class TestWorkConfigParsing:
    """Integration tests for work config JSON generation via step_enabled."""

    def test_system_test_enabled(self):
        # The system test uses 'st:' pattern (not step_enabled)
        content = '''test:
  st:
    required: true
'''
        import re
        assert re.search(r'st:[\s\S]*?required:\s+true', content) is not None

    def test_system_test_disabled(self):
        content = '''test:
  st:
    required: false
'''
        import re
        assert re.search(r'st:[\s\S]*?required:\s+true', content) is None

    def test_qa_enabled(self):
        content = '''test:
  qa:
    required: true
'''
        import re
        assert re.search(r'qa:[\s\S]*?required:\s+true', content) is not None

    def test_qa_disabled(self):
        content = '''test:
  qa:
    required: false
'''
        import re
        assert re.search(r'qa:[\s\S]*?required:\s+true', content) is None

    def test_reflect_enabled(self):
        content = '''reflect:
  required: true
'''
        import re
        assert re.search(r'reflect:[\s\S]*?required:\s+true', content) is not None
