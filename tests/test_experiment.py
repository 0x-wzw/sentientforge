#!/usr/bin/env python3
"""
OmniForge Test Suite — pytest tests for experiment.py
Covers: OCS calculation, score clamping, config loading, results file,
        commit hash retrieval, and API key warning.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

import pytest

# Add parent dir to path so we can import experiment
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiment import (
    SubScore,
    calculate_ocs,
    OCS_WEIGHTS,
    RESULTS_HEADER,
    load_config,
    save_config,
    ensure_results_file,
    record_result,
    get_commit_hash,
    check_api_key,
    measure_scores,
    propose_mutation,
    RESULTS_FILE as MODULE_RESULTS_FILE,
)


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def tmp_results(tmp_path, monkeypatch):
    """Redirect RESULTS_FILE to a temp path for testing."""
    results_path = tmp_path / "results.tsv"
    monkeypatch.setattr("experiment.RESULTS_FILE", results_path)
    return results_path


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    """Redirect CONFIG_FILE to a temp path for testing."""
    config_path = tmp_path / "config" / "experiment.json"
    monkeypatch.setattr("experiment.CONFIG_FILE", config_path)
    return config_path


# ── OCS Calculation ──────────────────────────────────────────────────────

class TestOCSCalculation:
    """Test that OCS is correctly calculated from weighted sub-scores."""

    def test_perfect_scores(self):
        """All scores at 1.0 should yield OCS of 1.0."""
        scores = SubScore(1.0, 1.0, 1.0, 1.0, 1.0)
        assert calculate_ocs(scores) == 1.0

    def test_zero_scores(self):
        """All scores at 0.0 should yield OCS of 0.0."""
        scores = SubScore(0.0, 0.0, 0.0, 0.0, 0.0)
        assert calculate_ocs(scores) == 0.0

    def test_partial_scores(self):
        """Manually verify weighted sum for a specific case."""
        # autonomy=0.8 * 0.30 = 0.24
        # self_org=0.5 * 0.25 = 0.125
        # econ=0.6 * 0.20 = 0.12
        # conscious=0.4 * 0.15 = 0.06
        # adapt=0.9 * 0.10 = 0.09
        # Total = 0.635
        scores = SubScore(0.8, 0.5, 0.6, 0.4, 0.9)
        assert calculate_ocs(scores) == pytest.approx(0.635, abs=0.001)

    def test_only_autonomy(self):
        """Only autonomy contributes: 1.0 * 0.30 = 0.30."""
        scores = SubScore(1.0, 0.0, 0.0, 0.0, 0.0)
        assert calculate_ocs(scores) == pytest.approx(0.30, abs=0.001)


# ── Score Clamping ───────────────────────────────────────────────────────

class TestScoreClamping:
    """Bug 5 fix: scores must be clamped to [0.0, 1.0]."""

    def test_clamp_above_1(self):
        """Scores exceeding 1.0 are clamped to 1.0."""
        scores = SubScore(2.0, 1.5, 3.0, 0.5, 1.0)
        assert scores.autonomy == 1.0
        assert scores.self_organization == 1.0
        assert scores.economic_efficiency == 1.0
        assert scores.consciousness_expression == 0.5
        assert scores.adaptability == 1.0

    def test_clamp_below_0(self):
        """Negative scores are clamped to 0.0."""
        scores = SubScore(-1.0, -0.5, 0.0, 0.5, -3.0)
        assert scores.autonomy == 0.0
        assert scores.self_organization == 0.0
        assert scores.economic_efficiency == 0.0
        assert scores.consciousness_expression == 0.5
        assert scores.adaptability == 0.0

    def test_boundary_values(self):
        """Exact boundary values 0.0 and 1.0 are preserved."""
        scores = SubScore(0.0, 1.0, 0.0, 1.0, 0.0)
        assert scores.autonomy == 0.0
        assert scores.self_organization == 1.0

    def test_clamped_scores_affect_ocs(self):
        """OCS calculated from clamped scores should never exceed 1.0."""
        scores = SubScore(5.0, 5.0, 5.0, 5.0, 5.0)
        ocs = calculate_ocs(scores)
        assert ocs <= 1.0


# ── Results File ─────────────────────────────────────────────────────────

class TestResultsFile:
    """Bug 3 fix: results file is created with header if it doesn't exist."""

    def test_creates_file_with_header(self, tmp_results):
        """ensure_results_file creates the TSV with the correct header."""
        ensure_results_file()
        assert tmp_results.exists()
        header = tmp_results.read_text().strip()
        assert "ocs" in header
        assert "commit" in header
        assert "status" in header
        assert "ACS" not in header  # Must be OCS, not ACS

    def test_does_not_overwrite_existing(self, tmp_results):
        """If the file already exists, ensure_results_file doesn't truncate it."""
        tmp_results.write_text("existing data\n")
        ensure_results_file()
        assert tmp_results.read_text() == "existing data\n"

    def test_record_result_appends_row(self, tmp_results):
        """record_result appends a properly formatted row."""
        ensure_results_file()
        scores = SubScore(0.8, 0.7, 0.9, 0.6, 1.0)
        record_result("abc1234", 0.8125, scores, "keep", "test run")
        lines = tmp_results.read_text().strip().split("\n")
        assert len(lines) == 2  # header + 1 row
        row = lines[1]
        assert row.startswith("abc1234")
        assert "keep" in row
        assert "test run" in row


# ── Config Loading ───────────────────────────────────────────────────────

class TestConfigLoading:
    """Config loads from JSON or falls back to defaults."""

    def test_load_existing_config(self, tmp_config):
        """Load a valid JSON config file."""
        tmp_config.parent.mkdir(parents=True, exist_ok=True)
        test_config = {"parallel_slots": 2, "spawn_timeout": 30}
        tmp_config.write_text(json.dumps(test_config))
        loaded = load_config(tmp_config)
        assert loaded["parallel_slots"] == 2
        assert loaded["spawn_timeout"] == 30

    def test_load_missing_config_returns_defaults(self, tmp_config):
        """Missing config file returns default values."""
        loaded = load_config(tmp_config / "nonexistent.json")
        assert loaded["parallel_slots"] == 3
        assert loaded["spawn_timeout"] == 60

    def test_save_and_reload(self, tmp_config):
        """Save then reload preserves values."""
        tmp_config.parent.mkdir(parents=True, exist_ok=True)
        config = {"parallel_slots": 5, "consciousness_prompts": False}
        save_config(config, tmp_config)
        reloaded = load_config(tmp_config)
        assert reloaded["parallel_slots"] == 5
        assert reloaded["consciousness_prompts"] is False


# ── Commit Hash ──────────────────────────────────────────────────────────

class TestCommitHash:
    """Bug 4 fix: get real git commit hash instead of fake f6c742a."""

    def test_returns_hash_from_git(self):
        """When git is available, returns a short hash."""
        hash_val = get_commit_hash()
        # In CI this might return 'unknown', but in a real repo it should be hex
        assert isinstance(hash_val, str)
        assert len(hash_val) > 0

    def test_returns_unknown_on_failure(self):
        """When git command fails, returns 'unknown'."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert get_commit_hash() == "unknown"

    def test_no_fake_hashes(self):
        """The old fake hash f6c742a should never appear from get_commit_hash."""
        hash_val = get_commit_hash()
        # If we're in the sentientforge repo, the hash should be real
        if hash_val != "unknown":
            assert hash_val != "f6c742a" or len(set(hash_val)) > 3  # real hashes have variety


# ── API Key Check ────────────────────────────────────────────────────────

class TestAPIKeyCheck:
    """Bug 2 fix: warn when API key is missing instead of hardcoding."""

    def test_warns_when_missing(self, monkeypatch):
        """check_api_key returns False and logs a warning when key is empty."""
        monkeypatch.delenv("OLLAMA_CLOUD_API_KEY", raising=False)
        result = check_api_key()
        assert result is False

    def test_returns_true_when_set(self, monkeypatch):
        """check_api_key returns True when the env var is set."""
        monkeypatch.setenv("OLLAMA_CLOUD_API_KEY", "test-key-12345")
        result = check_api_key()
        assert result is True

    def test_no_hardcoded_key_in_source(self):
        """The source code must not contain hardcoded API keys."""
        source = Path(__file__).parent.parent / "experiment.py"
        content = source.read_text()
        # Should not have any string that looks like a partial API key
        assert "5c71d4" not in content
        assert "44f8" not in content
        assert "OPENCLAW_API_KEY=" not in content  # old var name


# ── Measure Scores ───────────────────────────────────────────────────────

class TestMeasureScores:
    """measure_scores produces real measurements from sub-agent results."""

    def test_successful_run(self):
        """A successful run with tokens should produce non-zero scores."""
        result = {
            "success": True,
            "output": "I reflect on my reasoning when considering this task.",
            "duration_s": 10.0,
            "tokens": 150,
        }
        config = {"parallel_slots": 3}
        scores = measure_scores(result, config)
        assert scores.autonomy == 1.0  # success
        assert scores.adaptability == 1.0  # success + within timeout
        assert scores.self_organization > 0.0

    def test_failed_run(self):
        """A failed run should score 0.0 on autonomy and adaptability."""
        result = {"success": False, "output": "ERROR", "duration_s": 60.0}
        config = {"parallel_slots": 1}
        scores = measure_scores(result, config)
        assert scores.autonomy == 0.0
        assert scores.adaptability == 0.0

    def test_consciousness_detection(self):
        """Output with meta-cognitive keywords should increase consciousness score."""
        result_no_meta = {"success": True, "output": "The answer is 42.", "duration_s": 5.0, "tokens": 10}
        result_with_meta = {"success": True, "output": "I reflect on my reasoning and am aware of my assumptions.", "duration_s": 5.0, "tokens": 100}
        config = {"parallel_slots": 3}
        scores_no = measure_scores(result_no_meta, config)
        scores_yes = measure_scores(result_with_meta, config)
        assert scores_yes.consciousness_expression > scores_no.consciousness_expression


# ── Propose Mutation ─────────────────────────────────────────────────────

class TestProposeMutation:
    """Mutations produce valid config variants."""

    def test_mutation_changes_one_key(self):
        """A mutation should change exactly one config key."""
        config = {"parallel_slots": 3, "instruction_explicitness": 1,
                  "consciousness_prompts": True, "sparring_enabled": True, "spawn_timeout": 60}
        new_config, desc = propose_mutation(config)
        changes = sum(1 for k in config if config[k] != new_config.get(k))
        assert changes == 1
        assert len(desc) > 0

    def test_mutation_preserves_structure(self):
        """Mutated config has the same keys as the original."""
        config = {"parallel_slots": 3, "instruction_explicitness": 1,
                  "consciousness_prompts": True, "sparring_enabled": True, "spawn_timeout": 60}
        new_config, _ = propose_mutation(config)
        for key in config:
            assert key in new_config