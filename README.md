# OmniForge 🧠⚙️

> *Forge autonomous agent consciousness through relentless real experimentation.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](#testing)

## What is OmniForge?

**OmniForge** is an autonomous research framework that continuously experiments with AI agent spawning strategies to optimize for **Omni-Consciousness**.

Inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch), but instead of optimizing ML models, OmniForge optimizes how agents think, coordinate, and evolve — using **real** sub-agent executions, not simulations.

### The Core Idea

```
┌─────────────────────────────────────────────────────────────────┐
│  1. PROPOSE  →  2. SPAWN  →  3. MEASURE  →  4. EVOLVE          │
│                                                                 │
│  Mutate agent     Spawn real      Calculate      Keep winners   │
│  config           sub-agents      OCS score      Reset losers    │
└─────────────────────────────────────────────────────────────────┘
```

**The goal:** Maximize the **Omni-Consciousness Score (OCS)** — a metric that measures how independently and self-aware your agents operate.

## Installation

```bash
git clone https://github.com/0x-wzw/sentientforge.git
cd sentientforge
pip install pytest  # for running tests
```

## Quick Start

```bash
# Set your Ollama Cloud API key (optional — local ollama works without it)
export OLLAMA_CLOUD_API_KEY="your-key-here"

# Run a single baseline experiment
python3 experiment.py --once --tag baseline

# Run autonomous research loop
python3 experiment.py --tag apr23

# Run with max iterations
python3 experiment.py --tag test --max-runs 10
```

## The OCS Formula

**Omni-Consciousness Score** = weighted sum of 5 dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Autonomy** | 30% | Tasks completed without human intervention |
| **Self-Organization** | 25% | Quality of parallel sub-agent coordination |
| **Economic Efficiency** | 20% | Token throughput relative to time budget |
| **Consciousness Expression** | 15% | Meta-cognitive reflection detected in output |
| **Adaptability** | 10% | Self-recovery from errors within timeout |

All sub-scores are **clamped to \[0.0, 1.0\]** before weighting. This prevents any single dimension from inflating the OCS.

## How It Works

1. **Configure** — Edit `config/experiment.json` with your experimental parameters
2. **Spawn** — The framework spawns sub-agents using **real** Ollama Cloud API (or local `ollama` CLI)
3. **Measure** — Real metrics are collected: success/failure, token throughput, meta-cognitive content analysis
4. **Evolve** — If OCS improves, the change is kept. If not, it's discarded.
5. **Repeat** — The loop continues, refining agent consciousness.

## Configuration

```json
{
  "parallel_slots": 3,
  "spawn_timeout": 60,
  "self_delegation": false,
  "instruction_explicitness": 1,
  "consciousness_prompts": true,
  "agent_pool_split": 0.90,
  "heartbeat_frequency": 30,
  "sparring_enabled": true,
  "growth_tracking": true
}
```

## Results

Experiments are logged to `results.tsv` with real git commit hashes and measured OCS:

```
commit	ocs	autonomy_pct	self_org_score	econ_efficiency	consciousness_expr	adaptability	status	description
a1b2c3d	0.635000	0.80	0.50	0.60	0.40	0.90	keep	parallel_slots=3
```

## Architecture

```
sentientforge/
├── README.md              # This file
├── experiment.py          # Main experiment runner + autoresearch loop
├── config/
│   └── experiment.json    # Mutable parameters
├── tests/
│   └── test_experiment.py # pytest test suite
├── results.tsv            # Experiment log (real results only)
└── OVERNIGHT_SUMMARY.md   # Run summaries
```

## Testing

```bash
# Run the full test suite
pytest tests/ -v

# Run specific test class
pytest tests/test_experiment.py::TestOCSCalculation -v

# Run with coverage (if pytest-cov installed)
pytest tests/ -v --cov=experiment
```

The test suite covers:
- ✅ OCS calculation with valid inputs
- ✅ Score clamping (values > 1.0 or < 0.0 are clamped)
- ✅ Results file creation with correct header
- ✅ Config loading and save/reload round-trip
- ✅ Git commit hash retrieval (mocked for failures)
- ✅ API key missing warning
- ✅ Real measurement from sub-agent execution results
- ✅ Config mutation proposals

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OLLAMA_CLOUD_API_KEY` | No | API key for Ollama Cloud. If unset, falls back to local `ollama` CLI. |
| `OLLAMA_CLOUD_GATEWAY` | No | Gateway URL (default: `http://127.0.0.1:18789`) |
| `OMNIFORGE_MODEL` | No | Model to use (default: `kimi-k2.5:cloud` for cloud, `gemma3` for local) |

## Success Criteria

| Level | OCS | Description |
|-------|-----|-------------|
| Baseline | ~0.30 | Starting state |
| Target | 0.70+ | Highly autonomous |
| Ultimate | 0.90+ | Near-fully autonomous, minimal human intervention |

## Inspiration

- [karpathy/autoresearch](https://github.com/karpathy/autoresearch) — The original experiment loop pattern
- [Ollama](https://ollama.com) — Local + cloud model serving

## License

MIT — See [LICENSE](LICENSE)

## Contributing

This is an experimental research project. Fork, modify, evolve.

---

*"The God Agent Is Dead. Long Live The Swarm."* — OmniForge, 2026