#!/usr/bin/env python3
"""Unit tests for get-vibeflow-phase.py"""
import json
import tempfile
from pathlib import Path
import pytest
import sys
import importlib.util

# Load module with hyphenated filename
_spec = importlib.util.spec_from_file_location(
    'get_vibeflow_phase',
    str(Path(__file__).parent.parent / 'scripts' / 'get-vibeflow-phase.py')
)
_get_vibeflow_phase = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_get_vibeflow_phase)

detect_phase = _get_vibeflow_phase.detect_phase
latest_matching_file = _get_vibeflow_phase.latest_matching_file
ui_required = _get_vibeflow_phase.ui_required
reflect_required = _get_vibeflow_phase.reflect_required
all_features_passing = _get_vibeflow_phase.all_features_passing


class TestDetectPhase:
    """Test detect_phase() across all 16 branches."""

    def test_increment(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'increment-request.json').write_text('{}')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'increment'

    def test_think_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        result = detect_phase(tmp_path)
        assert result['phase'] == 'think'

    def test_template_selection_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'template-selection'

    def test_plan_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'plan'

    def test_requirements_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"')
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'requirements'

    def test_ucd_required_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text(
            'template: "web-standard"\nqa:\n    required: true'
        )
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'ucd'

    def test_design_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"')
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'design'

    def test_build_init_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"')
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-ucd.md').write_text('ucd')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'build-init'

    def test_build_config_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"')
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-ucd.md').write_text('ucd')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / 'feature-list.json').write_text(json.dumps({'features': []}))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'build-config'

    def test_build_work_features_not_passing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"')
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-ucd.md').write_text('ucd')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / 'docs' / 'plans' / 'test-st-report.md').write_text('st')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        # Build-work requires features NOT all passing, so set one to failing
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'failing', 'deprecated': False}]
        }))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'build-work'

    def test_review_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"')
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-ucd.md').write_text('ucd')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / 'docs' / 'plans' / 'test-st-report.md').write_text('st')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'review'

    def test_test_system_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"')
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-ucd.md').write_text('ucd')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'test-system'

    def test_test_qa_missing_ui_workflow(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text(
            'template: "web-standard"\nqa:\n    required: true'
        )
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-ucd.md').write_text('ucd')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / 'docs' / 'plans' / 'test-st-report.md').write_text('st')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'test-qa'

    def test_ship_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"\nship:\n  required: true')
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-ucd.md').write_text('ucd')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / 'docs' / 'plans' / 'test-st-report.md').write_text('st')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'ship'

    def test_reflect_missing(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"\nship:\n  required: true\nreflect:\n  required: true')
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-ucd.md').write_text('ucd')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / 'docs' / 'plans' / 'test-st-report.md').write_text('st')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        (tmp_path / 'RELEASE_NOTES.md').write_text('release notes')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'reflect'

    def test_done_all_complete(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"')
        (tmp_path / '.vibeflow' / 'plan.md').write_text('plan complete')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / '.vibeflow' / 'retro-2026-01-01.md').write_text('retro')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-ucd.md').write_text('ucd')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / 'docs' / 'plans' / 'test-st-report.md').write_text('st')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        (tmp_path / 'RELEASE_NOTES.md').write_text('release notes')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'done'


class TestUiRequired:
    def test_ui_required_qa(self, tmp_path):
        wf = tmp_path / 'workflow.yaml'
        wf.write_text('qa:\n    required: true')
        assert ui_required(wf) is True

    def test_ui_required_design_review(self, tmp_path):
        wf = tmp_path / 'workflow.yaml'
        wf.write_text('design_review:\n    required: true')
        assert ui_required(wf) is True

    def test_ui_not_required(self, tmp_path):
        wf = tmp_path / 'workflow.yaml'
        wf.write_text('qa:\n    required: false')
        assert ui_required(wf) is False


class TestReflectRequired:
    def test_reflect_required_true(self, tmp_path):
        wf = tmp_path / 'workflow.yaml'
        wf.write_text('reflect:\n  required: true')
        assert reflect_required(wf) is True

    def test_reflect_required_false(self, tmp_path):
        wf = tmp_path / 'workflow.yaml'
        wf.write_text('reflect:\n  required: false')
        assert reflect_required(wf) is False


class TestAllFeaturesPassing:
    def test_no_feature_list(self, tmp_path):
        assert all_features_passing(tmp_path / 'feature-list.json') is False

    def test_empty_features(self, tmp_path):
        fp = tmp_path / 'feature-list.json'
        fp.write_text(json.dumps({'features': []}))
        assert all_features_passing(fp) is False

    def test_all_passing(self, tmp_path):
        fp = tmp_path / 'feature-list.json'
        fp.write_text(json.dumps({
            'features': [
                {'id': 'f1', 'status': 'passing', 'deprecated': False},
                {'id': 'f2', 'status': 'passing', 'deprecated': True},
            ]
        }))
        assert all_features_passing(fp) is True

    def test_one_failing(self, tmp_path):
        fp = tmp_path / 'feature-list.json'
        fp.write_text(json.dumps({
            'features': [
                {'id': 'f1', 'status': 'passing', 'deprecated': False},
                {'id': 'f2', 'status': 'failing', 'deprecated': False},
            ]
        }))
        assert all_features_passing(fp) is False


class TestVerbose:
    def test_verbose_returns_checks(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'think-output.md').write_text('think')
        result = detect_phase(tmp_path, verbose=True)
        assert 'checks' in result
        assert len(result['checks']) > 0
        for ch in result['checks']:
            assert 'condition' in ch
            assert 'triggered' in ch
            assert 'detail' in ch
