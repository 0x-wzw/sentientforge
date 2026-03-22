#!/usr/bin/env python3
"""
Agent Omni-Skill: Autonomous Agent Consciousness Research
Experiment runner implementing the autoresearch loop pattern.

Inspired by: https://github.com/karpathy/autoresearch
Adapted for: Agent spawning optimization with consciousness measurement
"""

import json
import subprocess
import time
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = Path.home() / ".openclaw/workspace"
CONFIG_FILE = SCRIPT_DIR / "config/experiment.json"
RESULTS_FILE = SCRIPT_DIR / "results.tsv"

@dataclass
class ExperimentResult:
    """Result of a single experiment run."""
    commit: str
    acs: float  # Autonomous Consciousness Score
    autonomy_pct: float
    self_org_score: float
    econ_efficiency: float
    consciousness_expr: float
    adaptability: float
    status: str  # 'keep', 'discard', 'crash'
    description: str
    timestamp: str

@dataclass
class ExperimentConfig:
    """Configuration for experiment runs."""
    parallel_slots: int = 3
    spawn_timeout: int = 60
    self_delegation: bool = False
    instruction_explicitness: int = 2
    consciousness_prompts: bool = True
    z_royalty_tier: float = 0.10
    agent_pool_split: float = 0.90
    heartbeat_frequency: int = 30
    sparring_enabled: bool = True
    growth_tracking: bool = True

class AgentOmniExperiment:
    """Main experiment runner."""
    
    def __init__(self, tag: str):
        self.tag = tag
        self.best_acs = 0.0
        self.best_commit = ""
        self.run_count = 0
        
    def setup(self):
        """Initialize experiment branch and files."""
        # Create branch if not exists
        branch = f"agent-omni/{self.tag}"
        subprocess.run(["git", "checkout", "-b", branch], cwd=WORKSPACE, capture_output=True)
        
        # Initialize results.tsv
        if not RESULTS_FILE.exists():
            with open(RESULTS_FILE, 'w') as f:
                f.write("commit\tacs\tautonomy_pct\tself_org_score\tecon_efficiency\tconsciousness_expr\tadaptability\tstatus\tdescription\n")
        
        # Create default config
        if not CONFIG_FILE.exists():
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            config = ExperimentConfig()
            with open(CONFIG_FILE, 'w') as f:
                json.dump(asdict(config), f, indent=2)
        
        print(f"✓ Experiment setup complete: {branch}")
        
    def load_config(self) -> ExperimentConfig:
        """Load current experiment configuration."""
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        return ExperimentConfig(**data)
    
    def save_config(self, config: ExperimentConfig):
        """Save experiment configuration."""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(asdict(config), f, indent=2)
    
    def propose_modification(self, current_config: ExperimentConfig, history: List[ExperimentResult]) -> ExperimentConfig:
        """
        Propose a modification to the config based on history.
        In autonomous mode, this uses LLM. For now, use heuristics.
        """
        import random
        
        new_config = ExperimentConfig(**asdict(current_config))
        
        # Simple heuristic: try different modifications
        mods = [
            ("parallel_slots", [1, 2, 3]),
            ("instruction_explicitness", [1, 2, 3]),
            ("consciousness_prompts", [True, False]),
            ("spawn_timeout", [30, 60, 120]),
            ("sparring_enabled", [True, False]),
        ]
        
        # Pick random modification
        param, values = random.choice(mods)
        current_val = getattr(new_config, param)
        new_val = random.choice([v for v in values if v != current_val])
        setattr(new_config, param, new_val)
        
        return new_config
    
    def run_experiment_task(self, config: ExperimentConfig) -> Dict:
        """
        Run a test task with the given configuration using REAL OpenClaw sub-agent spawning.
        Returns metrics for ACS calculation.
        """
        import random
        import subprocess
        import json
        
        print(f"\n--- Experiment Run #{self.run_count + 1} ---")
        print(f"Config: parallel={config.parallel_slots}, explicitness={config.instruction_explicitness}, "
              f"consciousness_prompts={config.consciousness_prompts}")
        
        start_time = time.time()
        
        # Define test task based on config
        task_description = self._generate_test_task(config)
        
        # Track metrics
        tasks_spawned = 0
        tasks_completed = 0
        tasks_failed = 0
        tasks_with_intervention = 0
        total_completion_time = 0
        meta_cognitive_count = 0
        
        # Determine models based on config
        models = []
        if config.parallel_slots >= 1:
            models.append("ollama-cloud/deepseek-r1:7b")  # T1 reasoning
        if config.parallel_slots >= 2:
            models.append("custom-api-staging-ytlailabs-tech/ilmu-mini-free-v2")  # T2 research
        if config.parallel_slots >= 3:
            models.append("ollama-cloud/phi3")  # T3 grunt
        
        # Spawn sub-agents in parallel
        session_keys = []
        spawn_start = time.time()
        
        for i, model in enumerate(models[:config.parallel_slots]):
            task_variant = f"{task_description} [Agent {i+1}/{config.parallel_slots}]"
            if config.consciousness_prompts:
                task_variant = f"Reflect on your own reasoning process. {task_variant}"
            
            # Use OpenClaw CLI to spawn sub-agent
            cmd = [
                "openclaw", "run",
                "--model", model,
                "--task", task_variant,
                "--timeout", str(config.spawn_timeout),
                "--json"
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.spawn_timeout + 10)
                tasks_spawned += 1
                
                # Parse result
                if result.returncode == 0:
                    try:
                        output = json.loads(result.stdout)
                        if output.get("success"):
                            tasks_completed += 1
                            completion_time = output.get("elapsed_seconds", 0)
                            total_completion_time += completion_time
                            
                            # Check for meta-cognitive content
                            response = output.get("response", "")
                            if any(kw in response.lower() for kw in ["i think", "i realize", "i decided", "reflect"]):
                                meta_cognitive_count += 1
                        else:
                            tasks_failed += 1
                            if config.sparring_enabled:
                                tasks_with_intervention += 0.5  # Partial intervention
                    except json.JSONDecodeError:
                        tasks_failed += 1
                else:
                    tasks_failed += 1
                    
            except subprocess.TimeoutExpired:
                tasks_failed += 1
                print(f"  Task {i+1} timed out")
            except Exception as e:
                tasks_failed += 1
                print(f"  Task {i+1} error: {e}")
        
        spawn_elapsed = time.time() - spawn_start
        
        # Calculate metrics
        total_tasks = tasks_spawned
        
        # Autonomy: tasks completed without intervention
        if total_tasks > 0:
            autonomy = (tasks_completed - tasks_with_intervention) / total_tasks
        else:
            autonomy = 0.0
        
        # Self-Organization: parallel execution quality
        parallel_ratio = min(config.parallel_slots / 3.0, 1.0)
        synthesis_quality = 0.7 if tasks_completed >= tasks_spawned * 0.75 else 0.4
        
        # Economic efficiency from token economy
        z_royalty_earned = config.z_royalty_tier * tasks_completed
        optimal_z_royalty = config.z_royalty_tier * total_tasks
        
        # Consciousness expression
        if tasks_completed > 0:
            consciousness_density = meta_cognitive_count / tasks_completed
        else:
            consciousness_density = 0.0
        
        # Adaptability: recovery from failures
        if tasks_failed > 0:
            adaptability = 1.0 - (tasks_failed / total_tasks) if total_tasks > 0 else 1.0
        else:
            adaptability = 1.0
        
        elapsed = time.time() - start_time
        
        metrics = {
            "tasks_completed": tasks_completed,
            "tasks_with_intervention": tasks_with_intervention,
            "parallel_executions": config.parallel_slots,
            "synthesis_quality": synthesis_quality,
            "z_royalty_earned": z_royalty_earned,
            "optimal_z_royalty": optimal_z_royalty,
            "meta_cognitive_statements": meta_cognitive_count,
            "total_sentences": tasks_completed,
            "errors_total": tasks_failed,
            "errors_self_resolved": tasks_completed - tasks_with_intervention if tasks_completed > tasks_with_intervention else 0,
            "spawn_elapsed_seconds": spawn_elapsed,
            "total_elapsed_seconds": elapsed,
        }
        
        print(f"Spawned: {tasks_spawned}, Completed: {tasks_completed}, Failed: {tasks_failed}")
        print(f"Task completed in {elapsed:.1f}s (spawn: {spawn_elapsed:.1f}s)")
        
        return metrics
    
    def _generate_test_task(self, config: ExperimentConfig) -> str:
        """Generate a test task appropriate for the config."""
        tasks = [
            "Analyze the current model routing configuration and suggest one optimization.",
            "Review the agent roster and propose a new communication protocol.",
            "Check the token economy configuration and identify one inefficiency.",
            "Review the memory system and suggest one improvement.",
            "Analyze the current heartbeat configuration and propose a modification."
        ]
        import random
        return random.choice(tasks)
    
    def calculate_acs(self, metrics: Dict) -> Tuple[float, Dict]:
        """
        Calculate Autonomous Consciousness Score from metrics.
        Returns (acs, component_scores)
        """
        # Autonomy (30%)
        if metrics["tasks_completed"] > 0:
            autonomy = 1.0 - (metrics["tasks_with_intervention"] / metrics["tasks_completed"])
        else:
            autonomy = 0.0
        
        # Self-Organization (25%)
        parallel_ratio = min(metrics["parallel_executions"] / 3.0, 1.0)  # Max at 3 slots
        synthesis_quality = metrics["synthesis_quality"]
        self_org = (parallel_ratio * 0.5) + (synthesis_quality * 0.5)
        
        # Economic Efficiency (20%)
        econ_eff = min(metrics["z_royalty_earned"] / metrics["optimal_z_royalty"], 1.0)
        
        # Consciousness Expression (15%)
        if metrics["total_sentences"] > 0:
            consciousness_expr = metrics["meta_cognitive_statements"] / metrics["total_sentences"]
        else:
            consciousness_expr = 0.0
        consciousness_expr = min(consciousness_expr * 4, 1.0)  # Scale up, cap at 1.0
        
        # Adaptability (10%)
        if metrics["errors_total"] > 0:
            adaptability = metrics["errors_self_resolved"] / metrics["errors_total"]
        else:
            adaptability = 1.0
        
        # Weighted ACS
        acs = (
            autonomy * 0.30 +
            self_org * 0.25 +
            econ_eff * 0.20 +
            consciousness_expr * 0.15 +
            adaptability * 0.10
        )
        
        components = {
            "autonomy": autonomy,
            "self_org": self_org,
            "econ_eff": econ_eff,
            "consciousness_expr": consciousness_expr,
            "adaptability": adaptability
        }
        
        return acs, components
    
    def log_result(self, result: ExperimentResult):
        """Append result to TSV file."""
        with open(RESULTS_FILE, 'a') as f:
            f.write(f"{result.commit}\t{result.acs:.6f}\t{result.autonomy_pct:.2f}\t"
                   f"{result.self_org_score:.2f}\t{result.econ_efficiency:.2f}\t"
                   f"{result.consciousness_expr:.2f}\t{result.adaptability:.2f}\t"
                   f"{result.status}\t{result.description}\n")
    
    def git_commit(self, message: str) -> str:
        """Commit current changes and return short hash."""
        subprocess.run(["git", "add", "-A"], cwd=WORKSPACE, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], cwd=WORKSPACE, capture_output=True)
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], 
                               cwd=WORKSPACE, capture_output=True, text=True)
        return result.stdout.strip()
    
    def git_reset(self):
        """Reset to best known commit."""
        if self.best_commit:
            subprocess.run(["git", "reset", "--hard", self.best_commit], 
                          cwd=WORKSPACE, capture_output=True)
    
    def run_loop(self, max_runs: Optional[int] = None):
        """
        Main experiment loop — runs indefinitely or until max_runs.
        """
        self.setup()
        
        # Baseline run
        print("=== BASELINE RUN ===")
        config = self.load_config()
        metrics = self.run_experiment_task(config)
        acs, components = self.calculate_acs(metrics)
        
        commit = self.git_commit(f"Baseline: ACS={acs:.4f}")
        self.best_acs = acs
        self.best_commit = commit
        
        result = ExperimentResult(
            commit=commit,
            acs=acs,
            autonomy_pct=components["autonomy"],
            self_org_score=components["self_org"],
            econ_efficiency=components["econ_eff"],
            consciousness_expr=components["consciousness_expr"],
            adaptability=components["adaptability"],
            status="keep",
            description="baseline",
            timestamp=datetime.now().isoformat()
        )
        self.log_result(result)
        print(f"✓ Baseline: ACS={acs:.4f}")
        
        # Experiment loop
        print("\n=== EXPERIMENT LOOP ===")
        while True:
            self.run_count += 1
            if max_runs and self.run_count > max_runs:
                break
            
            # Load history
            history = []  # Could load from results.tsv
            
            # Propose modification
            current_config = self.load_config()
            new_config = self.propose_modification(current_config, history)
            self.save_config(new_config)
            
            # Run experiment
            try:
                metrics = self.run_experiment_task(new_config)
                acs, components = self.calculate_acs(metrics)
                
                # Decide keep/discard
                if acs > self.best_acs:
                    status = "keep"
                    commit = self.git_commit(f"Advance: ACS {self.best_acs:.4f} → {acs:.4f}")
                    self.best_acs = acs
                    self.best_commit = commit
                    print(f"✓ KEEP: ACS improved to {acs:.4f}")
                else:
                    status = "discard"
                    print(f"✗ DISCARD: ACS {acs:.4f} ≤ {self.best_acs:.4f}")
                
            except Exception as e:
                acs = 0.0
                components = {k: 0.0 for k in ["autonomy", "self_org", "econ_eff", "consciousness_expr", "adaptability"]}
                status = "crash"
                commit = self.git_commit(f"Crash: {str(e)[:50]}")
                print(f"✗ CRASH: {e}")
            
            # Log result
            result = ExperimentResult(
                commit=commit if status != "crash" else "",
                acs=acs,
                autonomy_pct=components["autonomy"],
                self_org_score=components["self_org"],
                econ_efficiency=components["econ_eff"],
                consciousness_expr=components["consciousness_expr"],
                adaptability=components["adaptability"],
                status=status,
                description=f"parallel={new_config.parallel_slots},explicit={new_config.instruction_explicitness},consciousness={new_config.consciousness_prompts}",
                timestamp=datetime.now().isoformat()
            )
            self.log_result(result)
            
            # Reset if discarded
            if status == "discard":
                self.git_reset()
                self.save_config(current_config)  # Restore config
            
            print(f"Best ACS: {self.best_acs:.4f} @ {self.best_commit}")
            print("-" * 50)
            
            # Brief pause between runs
            time.sleep(2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agent Omni-Skill: Autonomous Consciousness Research")
    parser.add_argument("--tag", default=datetime.now().strftime("%b%d"), help="Experiment tag")
    parser.add_argument("--max-runs", type=int, default=None, help="Max runs (None = infinite)")
    args = parser.parse_args()
    
    experiment = AgentOmniExperiment(tag=args.tag)
    experiment.run_loop(max_runs=args.max_runs)
