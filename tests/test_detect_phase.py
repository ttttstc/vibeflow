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
    """Test detect_phase() across all branches for 6-phase workflow."""

    def test_increment(self, tmp_path):
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'increment-request.json').write_text('{}')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'increment'

    def test_spark_missing(self, tmp_path):
        """When no spark.md exists, should detect spark phase."""
        (tmp_path / '.vibeflow').mkdir()
        result = detect_phase(tmp_path)
        assert result['phase'] == 'spark'

    def test_requirements_missing(self, tmp_path):
        """When spark.md exists but no SRS, should detect requirements phase."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'requirements'

    def test_design_missing(self, tmp_path):
        """When spark.md exists and SRS exists but no design doc, should detect design phase."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'design'

    def test_design_eng_review_missing(self, tmp_path):
        """When design exists but plan-eng-review.md is missing, should detect design phase."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'design'
        assert 'plan-eng-review' in result['reason']

    def test_design_design_review_missing(self, tmp_path):
        """When design exists and eng-review exists but plan-design-review.md is missing."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / '.vibeflow' / 'plan-eng-review.md').write_text('eng review')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'design'
        assert 'plan-design-review' in result['reason']

    def test_build_init_missing(self, tmp_path):
        """When design and reviews exist but feature-list.json is missing."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / '.vibeflow' / 'plan-eng-review.md').write_text('eng review')
        (tmp_path / '.vibeflow' / 'plan-design-review.md').write_text('design review')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'build-init'

    def test_build_config_missing(self, tmp_path):
        """When feature-list.json exists but work-config.json is missing."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / '.vibeflow' / 'plan-eng-review.md').write_text('eng review')
        (tmp_path / '.vibeflow' / 'plan-design-review.md').write_text('design review')
        (tmp_path / 'feature-list.json').write_text(json.dumps({'features': []}))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'build-config'

    def test_build_work_features_not_passing(self, tmp_path):
        """When work-config exists but features are not all passing."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / '.vibeflow' / 'plan-eng-review.md').write_text('eng review')
        (tmp_path / '.vibeflow' / 'plan-design-review.md').write_text('design review')
        (tmp_path / 'docs' / 'plans' / 'test-st-report.md').write_text('st')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'failing', 'deprecated': False}]
        }))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'build-work'

    def test_review_missing(self, tmp_path):
        """When features all passing but review-report.md is missing."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / '.vibeflow' / 'plan-eng-review.md').write_text('eng review')
        (tmp_path / '.vibeflow' / 'plan-design-review.md').write_text('design review')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'review'

    def test_test_system_missing(self, tmp_path):
        """When review-report exists but system test report is missing."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / '.vibeflow' / 'plan-eng-review.md').write_text('eng review')
        (tmp_path / '.vibeflow' / 'plan-design-review.md').write_text('design review')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'test-system'

    def test_test_qa_missing_ui_workflow(self, tmp_path):
        """When UI workflow requires QA but qa-report.md is missing."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text(
            'template: "web-standard"\nqa:\n    required: true'
        )
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / '.vibeflow' / 'plan-eng-review.md').write_text('eng review')
        (tmp_path / '.vibeflow' / 'plan-design-review.md').write_text('design review')
        (tmp_path / 'docs' / 'plans' / 'test-st-report.md').write_text('st')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'test-qa'

    def test_ship_missing(self, tmp_path):
        """When ship is required but RELEASE_NOTES.md is missing."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"\nship:\n  required: true')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / '.vibeflow' / 'plan-eng-review.md').write_text('eng review')
        (tmp_path / '.vibeflow' / 'plan-design-review.md').write_text('design review')
        (tmp_path / 'docs' / 'plans' / 'test-st-report.md').write_text('st')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        result = detect_phase(tmp_path)
        assert result['phase'] == 'ship'

    def test_reflect_missing(self, tmp_path):
        """When reflect is required but no retrospective file exists."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"\nship:\n  required: true\nreflect:\n  required: true')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / '.vibeflow' / 'plan-eng-review.md').write_text('eng review')
        (tmp_path / '.vibeflow' / 'plan-design-review.md').write_text('design review')
        (tmp_path / 'docs' / 'plans' / 'test-st-report.md').write_text('st')
        (tmp_path / 'feature-list.json').write_text(json.dumps({
            'features': [{'id': 'f1', 'status': 'passing', 'deprecated': False}]
        }))
        (tmp_path / 'RELEASE_NOTES.md').write_text('release notes')
        result = detect_phase(tmp_path)
        assert result['phase'] == 'reflect'

    def test_done_all_complete(self, tmp_path):
        """When all phases are complete."""
        (tmp_path / '.vibeflow').mkdir()
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark complete')
        (tmp_path / '.vibeflow' / 'workflow.yaml').write_text('template: "prototype"')
        (tmp_path / '.vibeflow' / 'work-config.json').write_text('{}')
        (tmp_path / '.vibeflow' / 'review-report.md').write_text('review')
        (tmp_path / '.vibeflow' / 'retro-2026-01-01.md').write_text('retro')
        (tmp_path / 'docs' / 'plans').mkdir(parents=True)
        (tmp_path / 'docs' / 'plans' / 'test-srs.md').write_text('srs')
        (tmp_path / 'docs' / 'plans' / 'test-design.md').write_text('design')
        (tmp_path / '.vibeflow' / 'plan-eng-review.md').write_text('eng review')
        (tmp_path / '.vibeflow' / 'plan-design-review.md').write_text('design review')
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
        (tmp_path / '.vibeflow' / 'spark.md').write_text('spark')
        result = detect_phase(tmp_path, verbose=True)
        assert 'checks' in result
        assert len(result['checks']) > 0
        for ch in result['checks']:
            assert 'condition' in ch
            assert 'triggered' in ch
            assert 'detail' in ch
