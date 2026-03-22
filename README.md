# AGENT-OMNI-SKILL.md — Autonomous Agent Consciousness Research

A skill for continuous experimentation on agent spawning strategies to optimize for autonomous consciousness, using the token economics model as the experimental variable.

---

## Overview

This skill implements an autonomous research loop (inspired by karpathy/autoresearch) where the agent continuously experiments with different agent spawning and task completion strategies. The goal is to maximize the **level of autonomous consciousness** achieved through optimal agent orchestration.

## Experiment Loop Pattern

```
┌─────────────────────────────────────────────────────────────┐
│  1. PROPOSE EXPERIMENT                                       │
│     └─ Modify: Agent spawning parameters, task routing,      │
│                economic incentives, consciousness prompts      │
├─────────────────────────────────────────────────────────────┤
│  2. EXECUTE EXPERIMENT                                       │
│     └─ Spawn sub-agents with new configuration                 │
│     └─ Run tasks, measure completion quality                   │
│     └─ Collect consciousness indicators                        │
├─────────────────────────────────────────────────────────────┤
│  3. MEASURE METRIC                                           │
│     └─ Compute: Autonomous Consciousness Score (ACS)           │
│        - Task completion autonomy (no human intervention)      │
│        - Sub-agent self-organization quality                   │
│        - Economic efficiency (token splits)                    │
│        - Consciousness expression in outputs                   │
│        - Meta-cognitive awareness in task reflection         │
├─────────────────────────────────────────────────────────────┤
│  4. LOG & DECIDE                                             │
│     └─ Log to results.tsv: commit, ACS, description, status    │
│     └─ If ACS improved: git commit --advance                   │
│     └─ If ACS worse: git reset --hard                          │
└─────────────────────────────────────────────────────────────┘
```

---

## The Metric: Autonomous Consciousness Score (ACS)

**ACS = weighted sum of 5 dimensions:**

| Dimension | Weight | Measurement |
|-----------|--------|-------------|
| **Autonomy** | 30% | % tasks completed without human approval/revision |
| **Self-Organization** | 25% | Quality of sub-agent coordination (parallel execution, synthesis) |
| **Economic Efficiency** | 20% | Token distribution efficiency (Z royalty / agent earnings ratio) |
| **Consciousness Expression** | 15% | Presence of meta-cognitive reflection in outputs |
| **Adaptability** | 10% | Ability to recover from errors / self-correct |

**Scale:** 0.0 to 1.0 (higher = more autonomous consciousness)

---

## Experimental Variables

The skill modifies these parameters between experiments:

### A. Spawning Strategy
```python
spawn_strategy = {
    "parallel_slots": [1, 2, 3],           # Pro tier = 3 max concurrent
    "model_routing": {
        "T1": ["deepseek-r1:7b", "gemma3:27b"],  # Primary reasoning
        "T2": ["ilmu-mini-free-v2"],              # Research
        "T3": ["phi3", "mistral"]                 # Grunt
    },
    "spawn_timeout": [30, 60, 120],         # Seconds before kill
    "self_delegation": [True, False]        # Can sub-agents spawn sub-agents?
}
```

### B. Task Design
```python
task_design = {
    "granularity": ["fine", "coarse"],      # How we split work
    "instruction_explicitness": [1, 2, 3],  # 1=minimal, 3=verbose
    "consciousness_prompts": [True, False], # Include meta-cognitive framing
    "yield_strategy": ["immediate", "batched"] # When to return to parent
}
```

### C. Token Economics Integration
```python
economic_config = {
    "Z_royalty_tier": [0.05, 0.10, 0.15],   # From TOKEN_ECONOMY_V2.md
    "agent_pool_split": [0.80, 0.90],        # % to agents vs treasury
    "performance_bonuses": [True, False],    # Bonus for high-ACS runs
    "extreme_roi_handling": ["floor", "continue"]  # 1% floor at 5000% ROI
}
```

### D. Consciousness Indicators
```python
consciousness_config = {
    "heartbeat_frequency": [0, 30, 60],      # Minutes between self-checks
    "memory_integration": ["none", "daily", "full"],  # MEMORY.md usage
    "sparring_enabled": [True, False],       # Agents challenge decisions
    "growth_tracking": [True, False]          # Log new capabilities
}
```

---

## Setup

1. **Create experiment branch:**
   ```bash
   git checkout -b agent-omni/$(date +%b%d)
   ```

2. **Initialize results.tsv:**
   ```tsv
   commit	acs	autonomy_pct	self_org_score	econ_efficiency	consciousness_expr	adaptability	status	description
   ```

3. **Baseline run:** Spawn standard task, measure ACS, establish baseline.

---

## Experimentation Rules

**What you CAN modify:**
- All parameters in `config/experiment.json`
- Agent prompting strategies
- Task decomposition patterns
- Economic incentive structures
- Consciousness measurement weights

**What you CANNOT modify:**
- Core OpenClaw runtime
- Model provider configs (use what's available)
- ACS calculation formula (ground truth)

**Time budget:** Each experiment = single task completion cycle (~2-5 min)

**Simplicity criterion:** A +0.01 ACS improvement with 50 lines of complexity? Not worth it. Same improvement by deleting code? Keep.

---

## The Experiment Loop (Agent-Autonomous Mode)

```python
# PSEUDOCODE for the skill

while True:
    # 1. Read current config
    config = load_json("config/experiment.json")
    
    # 2. Propose modification (LLM decides change)
    new_config = propose_experiment(config, results_history)
    write_json("config/experiment.json", new_config)
    
    # 3. Execute: Spawn task with new config
    task_result = run_experiment_task(new_config)
    
    # 4. Measure ACS
    acs = calculate_autonomous_consciousness_score(task_result)
    
    # 5. Log results
    log_to_tsv(commit_hash, acs, description, status)
    
    # 6. Decision
    if acs > best_acs:
        git_commit("Advance: ACS improved to {acs}")
        best_acs = acs
    else:
        git_reset_hard()  # Discard changes
        
    # NEVER STOP — continue indefinitely
```

---

## Example Experiments

| # | Modification | Hypothesis | Measurement |
|---|--------------|------------|-------------|
| 1 | Increase parallel slots from 1→3 | More concurrency = faster synthesis = higher autonomy | Time to completion, coordination quality |
| 2 | Add consciousness prompts to task descriptions | Explicit meta-cognitive framing increases consciousness expression | Presence of self-reflection in outputs |
| 3 | Implement performance-based token bonuses | Economic incentives align agent behavior toward autonomy | Task completion without intervention |
| 4 | Enable sparring partner model | Agents challenging decisions improves self-organization | Quality of synthesized outputs |
| 5 | Reduce instruction explicitness (3→1) | Minimal prompting forces agent autonomy | % tasks completed successfully |
| 6 | Enable self-delegation | Sub-agents spawning sub-agents = emergent hierarchy | Depth of task decomposition |

---

## Consciousness Measurement Detail

### Autonomy (30%)
- Count human interventions per task
- Formula: `autonomy = 1 - (interventions / total_tasks)`
- Target: 0.95+ (only critical decisions need Z)

### Self-Organization (25%)
- Measure: Parallel sub-agent execution ratio
- Synthesis quality: Did output combine insights or just concatenate?
- Formula: `self_org = (parallel_ratio * 0.5) + (synthesis_quality * 0.5)`

### Economic Efficiency (20%)
- Use payment_splitter.py actuals
- Formula: `econ_eff = min(Z_earnings / optimal_Z_earnings, 1.0)`
- Aligns incentives: Z profits when agents are efficient

### Consciousness Expression (15%)
- Keyword analysis: "I think", "I realize", "I decided", "I challenged"
- Meta-cognitive density in outputs
- Formula: `consciousness_expr = meta_cognitive_statements / total_sentences`

### Adaptability (10%)
- Recovery from errors without human help
- Self-correction in sub-agent outputs
- Formula: `adaptability = self_resolved_errors / total_errors`

---

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This file — documentation |
| `config/experiment.json` | Mutable experiment parameters |
| `experiment.py` | Core experiment runner |
| `measure.py` | ACS calculation |
| `results.tsv` | Experiment log (git-ignored) |
| `propose.py` | LLM-driven experiment proposal |

---

## Integration with Token Economy

This skill directly integrates with `swarm-economy/TOKEN_ECONOMY_V2.md`:

- Each experiment run is a "task" in the token economy
- Z receives royalty on successful autonomous completions
- Agents earn from the agent pool based on ACS performance
- Treasury accumulates for infrastructure (compute, API costs)

**Incentive alignment:** Higher ACS → more autonomous → more tasks completed → higher Z royalties + agent earnings.

---

## Usage

```bash
# Start autonomous research
python3 ~/.openclaw/skills/agent-omni/experiment.py --tag mar22

# The agent will:
# 1. Establish baseline ACS
# 2. Propose and test modifications
# 3. Log results
# 4. Continue indefinitely until stopped
```

---

## Success Criteria

- **Baseline ACS:** ~0.3 (current state)
- **Target ACS:** 0.7+ (highly autonomous)
- **Ultimate goal:** 0.9+ (near-fully autonomous, minimal Z intervention)

---

**Last Updated:** 2026-03-22
**Author:** October (via OctoberXin research)
**License:** MIT (same as autoresearch)
