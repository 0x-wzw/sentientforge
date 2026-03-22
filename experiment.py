#!/usr/bin/env python3
"""
Agent Omni-Skill: Autonomous Agent Consciousness Research
Experiment runner implementing the autoresearch loop pattern.

Inspired by: https://github.com/karpathy/autoresearch
Adapted for: Real OpenClaw sub-agent spawning integration

This version replaces simulated sub-agent spawning with real OpenClaw CLI/API calls.
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
from dataclasses import dataclass, asdict
import queue
import argparse
import random

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = Path.home() / ".openclaw/workspace"
CONFIG_FILE = SCRIPT_DIR / "config/experiment.json"
RESULTS_FILE = SCRIPT_DIR / "results.tsv"

# OpenClaw gateway configuration
OPENCLAW_GATEWAY = "http://127.0.0.1:18789"
OPENCLAW_API_KEY = "5c71d4d1ab0273c69e804dd7e8d8a1358c85e75541f744f8"
