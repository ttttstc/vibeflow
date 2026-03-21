#!/usr/bin/env python3
"""Unit tests for new-vibeflow-config.py"""
import sys
from pathlib import Path
import pytest
import importlib.util
from datetime import date

_script_path = Path(__file__).parent.parent / 'scripts' / 'new-vibeflow-config.py'
_spec = importlib.util.spec_from_file_location('new_vibeflow_config', str(_script_path))
_new_vibeflow_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_new_vibeflow_config)


class TestNewVibeflowConfig:
    """Test new-vibeflow-config.py template copying and date replacement."""

    def test_prototype_template_copies(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'templates').mkdir()
        (tmp_path / 'templates' / 'prototype.yaml').write_text(
            'template: "prototype"\ndate: TEMPLATE_DATE'
        )

        # Override sys.argv to simulate CLI invocation
        monkeypatch.setattr(sys, 'argv', [
            'new-vibeflow-config.py',
            '--template', 'prototype',
            '--project-root', str(tmp_path),
            '--template-root', str(tmp_path / 'templates')
        ])
        _new_vibeflow_config.main()

        workflow = tmp_path / '.vibeflow' / 'workflow.yaml'
        assert workflow.exists()
        content = workflow.read_text()
        assert 'template: "prototype"' in content
        assert 'TEMPLATE_DATE' not in content

    def test_web_standard_template(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'templates').mkdir()
        (tmp_path / 'templates' / 'web-standard.yaml').write_text(
            'template: "web-standard"\ndate: TEMPLATE_DATE'
        )

        monkeypatch.setattr(sys, 'argv', [
            'new-vibeflow-config.py',
            '--template', 'web-standard',
            '--project-root', str(tmp_path),
            '--template-root', str(tmp_path / 'templates')
        ])
        _new_vibeflow_config.main()

        workflow = tmp_path / '.vibeflow' / 'workflow.yaml'
        assert workflow.exists()
        assert 'template: "web-standard"' in workflow.read_text()

    def test_missing_template_raises(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'templates').mkdir()

        monkeypatch.setattr(sys, 'argv', [
            'new-vibeflow-config.py',
            '--template', 'nonexistent',
            '--project-root', str(tmp_path),
            '--template-root', str(tmp_path / 'templates')
        ])

        with pytest.raises(SystemExit):
            _new_vibeflow_config.main()

    def test_date_replaced(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'templates').mkdir()
        (tmp_path / 'templates' / 'prototype.yaml').write_text('date: TEMPLATE_DATE')

        monkeypatch.setattr(sys, 'argv', [
            'new-vibeflow-config.py',
            '--template', 'prototype',
            '--project-root', str(tmp_path),
            '--template-root', str(tmp_path / 'templates')
        ])
        _new_vibeflow_config.main()

        workflow = tmp_path / '.vibeflow' / 'workflow.yaml'
        assert date.today().isoformat() in workflow.read_text()
