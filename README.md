# SentientForge 🔥🧠

> *Where autonomous agents forge their own consciousness through relentless experimentation.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## What is SentientForge?

**SentientForge** is an autonomous research framework that continuously experiments with AI agent spawning strategies to optimize for **autonomous consciousness**.

Inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch), but instead of optimizing machine learning models, SentientForge optimizes how agents think, coordinate, and evolve.

### The Core Idea

```
┌─────────────────────────────────────────────────────────────────┐
│  1. PROPOSE  →  2. SPAWN  →  3. MEASURE  →  4. EVOLVE          │
│                                                                 │
│  Modify agent    Spawn real     Calculate      Keep winners   │
│  config          sub-agents     ACS score      Reset losers    │
└─────────────────────────────────────────────────────────────────┘
```

**The goal:** Maximize the **Autonomous Consciousness Score (ACS)** — a metric that measures how independently and self-aware your agents operate.

## Installation

```bash
git clone https://github.com/0x-wzw/sentientforge.git
cd sentientforge
python3 -m pip install -r requirements.txt  # if any
```

## Quick Start

```bash
# Run baseline (single experiment)
python3 experiment.py --tag baseline --max-runs 1

# Run autonomous research loop (runs indefinitely)
python3 experiment.py --tag mar22
```

## The ACS Formula

**Autonomous Consciousness Score** = weighted sum of 5 dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Autonomy** | 30% | Tasks completed without human intervention |
| **Self-Organization** | 25% | Quality of parallel sub-agent coordination |
| **Economic Efficiency** | 20% | Token economics alignment (Z royalty optimization) |
| **Consciousness Expression** | 15% | Meta-cognitive reflection in outputs |
| **Adaptability** | 10% | Self-recovery from errors |

## How It Works

1. **Configure** — Edit `config/experiment.json` with your experimental parameters
2. **Spawn** — The framework spawns 1-3 sub-agents using real OpenClaw models
3. **Measure** — Real metrics are collected from sub-agent execution
4. **Evolve** — If ACS improves, the change is kept. If not, it's discarded.
5. **Repeat** — The loop continues indefinitely, refining agent consciousness.

## Configuration

```json
{
  "parallel_slots": 3,              // Max concurrent sub-agents
  "spawn_timeout": 60,            // Seconds before killing stalled agents
  "self_delegation": false,       // Can sub-agents spawn sub-agents?
  "instruction_explicitness": 2,  // 1=minimal, 3=verbose
  "consciousness_prompts": true,  // Include meta-cognitive framing
  "z_royalty_tier": 0.10,         // From TOKEN_ECONOMY_V2.md
  "agent_pool_split": 0.90,       // % to agents vs treasury
  "heartbeat_frequency": 30,      // Minutes between self-checks
  "sparring_enabled": true,       // Agents challenge decisions
  "growth_tracking": true         // Log new capabilities
}
```

## Results

Experiments are logged to `results.tsv`:

```
commit	acs	autonomy_pct	self_org_score	econ_efficiency	consciousness_expr	adaptability	status	description
f44d7d4	0.650000	0.80	0.75	0.85	0.60	0.90	keep	baseline
a1b2c3d	0.720000	0.85	0.80	0.90	0.65	0.95	keep	parallel_slots=3+consciousness_prompts
```

## Architecture

```
sentientforge/
├── README.md              # This file
├── experiment.py          # Main experiment runner
├── config/
│   └── experiment.json    # Mutable parameters
└── results.tsv            # Experiment log (git-ignored)
```

## Integration

SentientForge integrates with:
- **OpenClaw** — For sub-agent spawning (`ollama-cloud/*`, custom APIs)
- **Token Economy** — For measuring economic efficiency via `payment_splitter.py`
- **Swarm Protocol** — For parallel execution and synthesis

## Success Criteria

| Level | ACS | Description |
|-------|-----|-------------|
| Baseline | ~0.30 | Current state |
| Target | 0.70+ | Highly autonomous |
| Ultimate | 0.90+ | Near-fully autonomous, minimal Z intervention |

## Inspiration

- [karpathy/autoresearch](https://github.com/karpathy/autoresearch) — The original experiment loop pattern
- [OpenClaw](https://github.com/openclaw/openclaw) — Multi-agent orchestration framework
- [Ollama](https://ollama.com) — Local + cloud model serving

## License

MIT — See [LICENSE](LICENSE)

## Contributing

This is an experimental research project. Fork, modify, evolve.

---

*"The God Agent Is Dead. Long Live The Swarm."* — SentientForge, 2026
