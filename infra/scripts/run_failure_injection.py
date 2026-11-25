#!/usr/bin/env python3
"""Failure injection drills for kill switches and LLM fallbacks."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "app/tests/test_fallbacks.py",
        "app/tests/test_rollout.py",
        "app/tests/test_tenant.py",
        "app/tests/test_routing_controls.py",
        "-q",
    ]
    print("[RUN] failure injection suite:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=REPO_ROOT / "backend")
    if result.returncode != 0:
        print("Failure injection drills FAILED.", file=sys.stderr)
        return 1
    print("Failure injection drills passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
