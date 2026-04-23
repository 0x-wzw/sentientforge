#!/usr/bin/env python3
"""
OmniForge — Autonomous Agent Consciousness Research
Experiment runner implementing the autoresearch loop pattern.

Inspired by: https://github.com/karpathy/autoresearch
Adapted for: Ollama Cloud sub-agent spawning integration

OCS = Omni-Consciousness Score — weighted metric measuring agent autonomy,
self-organization, economic efficiency, consciousness expression, and adaptability.
"""

import json
import subprocess
import time
import re
import os
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import queue
import argparse
import random
import logging

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = Path.home() / ".ollama-cloud/workspace"
CONFIG_FILE = SCRIPT_DIR / "config/experiment.json"
RESULTS_FILE = SCRIPT_DIR / "results.tsv"

# ── Ollama Cloud gateway ──────────────────────────────────────────────────
OLLAMA_CLOUD_GATEWAY = os.environ.get("OLLAMA_CLOUD_GATEWAY", "http://127.0.0.1:18789")
OLLAMA_CLOUD_API_KEY = os.environ.get("OLLAMA_CLOUD_API_KEY", "")

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("omniforge")

# ── OCS Weights ────────────────────────────────────────────────────────────
OCS_WEIGHTS = {
    "autonomy": 0.30,
    "self_organization": 0.25,
    "economic_efficiency": 0.20,
    "consciousness_expression": 0.15,
    "adaptability": 0.10,
}

RESULTS_HEADER = (
    "commit\tocs\tautonomy_pct\tself_org_score\tecon_efficiency\t"
    "consciousness_expr\tadaptability\tstatus\tdescription"
)


# ── Data Classes ──────────────────────────────────────────────────────────
@dataclass
class SubScore:
    """Individual OCS dimension score, clamped to [0.0, 1.0]."""
    autonomy: float = 0.0
    self_organization: float = 0.0
    economic_efficiency: float = 0.0
    consciousness_expression: float = 0.0
    adaptability: float = 0.0

    def __post_init__(self):
        # Bug 5 fix: clamp all scores to [0.0, 1.0]
        for field_name in ["autonomy", "self_organization", "economic_efficiency",
                           "consciousness_expression", "adaptability"]:
            val = getattr(self, field_name)
            setattr(self, field_name, max(0.0, min(1.0, val)))


def calculate_ocs(scores: SubScore) -> float:
    """Calculate the weighted Omni-Consciousness Score (OCS)."""
    weighted_sum = 0.0
    weighted_sum += scores.autonomy * OCS_WEIGHTS["autonomy"]
    weighted_sum += scores.self_organization * OCS_WEIGHTS["self_organization"]
    weighted_sum += scores.economic_efficiency * OCS_WEIGHTS["economic_efficiency"]
    weighted_sum += scores.consciousness_expression * OCS_WEIGHTS["consciousness_expression"]
    weighted_sum += scores.adaptability * OCS_WEIGHTS["adaptability"]
    return round(weighted_sum, 6)


# ── Config Loading ────────────────────────────────────────────────────────
def load_config(path: Path = CONFIG_FILE) -> Dict:
    """Load experiment configuration from JSON file."""
    if not path.exists():
        log.warning(f"Config file not found at {path}, using defaults")
        return {
            "parallel_slots": 3,
            "spawn_timeout": 60,
            "self_delegation": False,
            "instruction_explicitness": 1,
            "consciousness_prompts": True,
            "agent_pool_split": 0.90,
            "heartbeat_frequency": 30,
            "sparring_enabled": True,
            "growth_tracking": True,
        }
    with open(path) as f:
        return json.load(f)


def save_config(config: Dict, path: Path = CONFIG_FILE) -> None:
    """Save experiment configuration to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")


# ── Git Operations ────────────────────────────────────────────────────────
def get_commit_hash() -> str:
    """Get the short commit hash of the current HEAD. Bug 4 fix: real git hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=SCRIPT_DIR, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return "unknown"


# ── Results File ──────────────────────────────────────────────────────────
def ensure_results_file() -> None:
    """Bug 3 fix: create results file with header if it doesn't exist."""
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not RESULTS_FILE.exists():
        with open(RESULTS_FILE, "w") as f:
            f.write(RESULTS_HEADER + "\n")
        log.info(f"Created results file: {RESULTS_FILE}")


def record_result(commit: str, ocs: float, scores: SubScore,
                  status: str, description: str) -> None:
    """Append an experiment result to the TSV file."""
    ensure_results_file()
    row = (
        f"{commit}\t{ocs:.6f}\t{scores.autonomy:.2f}\t{scores.self_organization:.2f}\t"
        f"{scores.economic_efficiency:.2f}\t{scores.consciousness_expression:.2f}\t"
        f"{scores.adaptability:.2f}\t{status}\t{description}"
    )
    with open(RESULTS_FILE, "a") as f:
        f.write(row + "\n")
    log.info(f"Recorded: ocs={ocs:.4f} status={status} desc={description}")


# ── API Key Check ─────────────────────────────────────────────────────────
def check_api_key() -> bool:
    """Bug 2 fix: warn if API key is missing instead of hardcoding."""
    key = os.environ.get("OLLAMA_CLOUD_API_KEY", "")
    if not key:
        log.warning(
            "OLLAMA_CLOUD_API_KEY not set. Sub-agent spawning will use "
            "local-only mode. Set the env var for full cloud access."
        )
        return False
    return True


# ── Sub-Agent Spawning (Real) ────────────────────────────────────────────
def spawn_sub_agent(task_prompt: str, config: Dict, timeout: int = 60) -> Dict:
    """
    Spawn a real sub-agent via Ollama Cloud API.
    Returns a dict with: success (bool), output (str), duration_s (float).
    """
    if not OLLAMA_CLOUD_API_KEY:
        # Fallback: local-only mode using ollama CLI
        return _spawn_local(task_prompt, config, timeout)
    return _spawn_cloud(task_prompt, config, timeout)


def _spawn_cloud(task_prompt: str, config: Dict, timeout: int) -> Dict:
    """Spawn via Ollama Cloud gateway API."""
    payload = {
        "model": os.environ.get("OMNIFORGE_MODEL", "kimi-k2.5:cloud"),
        "prompt": task_prompt,
        "stream": False,
        "options": {
            "num_ctx": 4096,
            "temperature": 0.7,
        },
    }
    payload_file = SCRIPT_DIR / ".spawn_payload.json"
    with open(payload_file, "w") as f:
        json.dump(payload, f)

    try:
        start = time.time()
        result = subprocess.run(
            [
                "curl", "-s", "-X", "POST",
                f"{OLLAMA_CLOUD_GATEWAY}/api/generate",
                "-H", f"Authorization: Bearer {OLLAMA_CLOUD_API_KEY}",
                "-H", "Content-Type: application/json",
                "-d", f"@{payload_file}",
            ],
            capture_output=True, text=True, timeout=timeout,
        )
        duration = time.time() - start
        payload_file.unlink(missing_ok=True)

        if result.returncode != 0:
            return {"success": False, "output": result.stderr, "duration_s": duration}

        try:
            resp = json.loads(result.stdout)
            return {
                "success": True,
                "output": resp.get("response", ""),
                "duration_s": duration,
                "tokens": resp.get("eval_count", 0),
            }
        except json.JSONDecodeError:
            return {"success": False, "output": result.stdout[:500], "duration_s": duration}
    except subprocess.TimeoutExpired:
        payload_file.unlink(missing_ok=True)
        return {"success": False, "output": "TIMEOUT", "duration_s": timeout}


def _spawn_local(task_prompt: str, config: Dict, timeout: int) -> Dict:
    """Spawn via local ollama CLI as fallback."""
    model = os.environ.get("OMNIFORGE_MODEL", "gemma3")
    try:
        start = time.time()
        result = subprocess.run(
            ["ollama", "run", model, task_prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        duration = time.time() - start
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "duration_s": duration,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "TIMEOUT", "duration_s": timeout}
    except FileNotFoundError:
        return {"success": False, "output": "OLLAMA_NOT_FOUND", "duration_s": 0.0}


# ── Measurement ──────────────────────────────────────────────────────────
def measure_scores(result: Dict, config: Dict) -> SubScore:
    """
    Measure OCS sub-scores from a real sub-agent execution result.
    This replaces any simulated/random scoring with measurement of actual outcomes.
    """
    # Autonomy: did the sub-agent complete without human intervention?
    autonomy = 1.0 if result.get("success") else 0.0

    # Self-organization: parallel slot utilization
    parallel_slots = config.get("parallel_slots", 1)
    self_org = min(1.0, (parallel_slots / 3.0) * 0.85) if result.get("success") else 0.0

    # Economic efficiency: token throughput vs time
    tokens = result.get("tokens", 0) or len(result.get("output", "").split())
    duration = max(result.get("duration_s", 1.0), 0.1)
    throughput = tokens / duration
    econ = min(1.0, throughput / 50.0)  # 50 tokens/sec = max efficiency

    # Consciousness expression: meta-cognitive keywords in output
    output_text = result.get("output", "").lower()
    meta_keywords = ["reflect", "aware", "think about", "consider", "self-",
                      "meta", "conscious", "evaluate", "reasoning"]
    matches = sum(1 for kw in meta_keywords if kw in output_text)
    consciousness = min(1.0, matches / 4.0)

    # Adaptability: did agent handle the task successfully within timeout?
    adaptability = 1.0 if result.get("success") and result.get("duration_s", 999) < 55 else 0.0

    return SubScore(
        autonomy=autonomy,
        self_organization=self_org,
        economic_efficiency=econ,
        consciousness_expression=consciousness,
        adaptability=adaptability,
    )


# ── Mutation Proposals ───────────────────────────────────────────────────
def propose_mutation(config: Dict) -> Tuple[Dict, str]:
    """Propose a random mutation to the experiment configuration."""
    mutations = [
        ("parallel_slots", [1, 2, 3]),
        ("instruction_explicitness", [1, 2, 3]),
        ("consciousness_prompts", [True, False]),
        ("sparring_enabled", [True, False]),
        ("spawn_timeout", [30, 60, 90]),
    ]
    # Pick a mutation that actually changes the value
    candidates = [(k, v) for k, values in mutations for v in values if config.get(k) != v]
    if not candidates:
        # All values already match defaults — force a change on first key
        key = mutations[0][0]
        value = [v for v in mutations[0][1] if config.get(key) != v][0]
        candidates = [(key, value)]
    key, value = random.choice(candidates)
    new_config = dict(config)
    new_config[key] = value
    desc = f"{key}={value}"
    return new_config, desc


# ── Main Experiment Loop ────────────────────────────────────────────────
def run_experiment(config: Dict, tag: str = "default") -> Tuple[float, SubScore, str]:
    """Run a single experiment: spawn sub-agents and measure OCS."""
    prompt = _build_prompt(config)
    timeout = config.get("spawn_timeout", 60)

    slots = config.get("parallel_slots", 1)
    results = []
    for i in range(slots):
        r = spawn_sub_agent(prompt, config, timeout)
        results.append(r)

    # Aggregate scores across parallel slots
    all_scores = [measure_scores(r, config) for r in results]
    avg = SubScore(
        autonomy=sum(s.autonomy for s in all_scores) / len(all_scores),
        self_organization=sum(s.self_organization for s in all_scores) / len(all_scores),
        economic_efficiency=sum(s.economic_efficiency for s in all_scores) / len(all_scores),
        consciousness_expression=sum(s.consciousness_expression for s in all_scores) / len(all_scores),
        adaptability=sum(s.adaptability for s in all_scores) / len(all_scores),
    )
    ocs = calculate_ocs(avg)
    return ocs, avg, tag


def _build_prompt(config: Dict) -> str:
    """Build an experiment prompt from config."""
    explicitness = config.get("instruction_explicitness", 1)
    base = "Complete the following research task autonomously. "
    if config.get("consciousness_prompts", True):
        base += "Reflect on your reasoning process. "
    if config.get("sparring_enabled", True):
        base += "Challenge your own assumptions. "
    if explicitness >= 2:
        base += "Provide detailed step-by-step analysis. "
    if explicitness >= 3:
        base += "Include explicit meta-commentary on your decision-making. "
    base += "Topic: Analyze the trade-offs between centralized and distributed agent orchestration."
    return base


def run_loop(tag: str = "default", max_runs: int = 0) -> None:
    """
    Run the autoresearch loop.
    max_runs=0 means run indefinitely.
    """
    check_api_key()
    ensure_results_file()
    config = load_config()
    best_ocs = 0.0
    best_config = dict(config)
    commit = get_commit_hash()
    run_count = 0

    log.info(f"Starting OmniForge autoresearch loop (tag={tag}, commit={commit})")

    try:
        while True:
            run_count += 1
            log.info(f"--- Run #{run_count} ---")

            # Propose a mutation
            candidate, desc = propose_mutation(config)
            log.info(f"Mutation: {desc}")

            # Run experiment with candidate config
            ocs, scores, _ = run_experiment(candidate, tag=desc)

            # Decide: keep or discard
            old_best = best_ocs
            if ocs > best_ocs:
                status = "keep"
                best_ocs = ocs
                best_config = dict(candidate)
                config.update({k: candidate[k] for k in candidate if candidate[k] != config.get(k)})
                log.info(f"✅ KEPT (ocs={ocs:.4f} > best={old_best:.4f})")
            else:
                status = "discard"
                log.info(f"❌ DISCARDED (ocs={ocs:.4f} <= best={best_ocs:.4f})")

            record_result(commit, ocs, scores, status, desc)

            if max_runs > 0 and run_count >= max_runs:
                log.info(f"Reached max_runs={max_runs}, stopping.")
                break

            time.sleep(2)  # brief pause between runs

    except KeyboardInterrupt:
        log.info("Interrupted by user.")

    # Save best config
    save_config(best_config)
    log.info(f"Best OCS: {best_ocs:.4f}")
    log.info(f"Best config saved to {CONFIG_FILE}")


# ── CLI ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="OmniForge — Autonomous Agent OCS Research")
    parser.add_argument("--tag", default="default", help="Experiment tag for logging")
    parser.add_argument("--max-runs", type=int, default=0, help="Max runs (0=infinite)")
    parser.add_argument("--once", action="store_true", help="Run single baseline experiment")
    args = parser.parse_args()

    if args.once:
        args.max_runs = 1

    run_loop(tag=args.tag, max_runs=args.max_runs)


if __name__ == "__main__":
    main()