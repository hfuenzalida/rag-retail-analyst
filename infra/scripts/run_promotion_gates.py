#!/usr/bin/env python3
"""Run all automated promotion gates from infra/promotion-gates.yaml."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
GATES_FILE = REPO_ROOT / "infra" / "promotion-gates.yaml"


def run_gate(gate: dict) -> bool:
    gate_id = gate["id"]
    if gate.get("manual"):
        print(f"[SKIP] {gate_id}: manual gate (human sign-off required)")
        return True

    command = gate.get("command")
    if not command:
        print(f"[FAIL] {gate_id}: no command defined", file=sys.stderr)
        return False

    print(f"[RUN] {gate_id}: {gate.get('description', command)}")
    result = subprocess.run(command, shell=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print(f"[FAIL] {gate_id}", file=sys.stderr)
        return False
    print(f"[PASS] {gate_id}")
    return True


def main() -> int:
    if not GATES_FILE.exists():
        print(f"Missing gates file: {GATES_FILE}", file=sys.stderr)
        return 1

    gates_doc = yaml.safe_load(GATES_FILE.read_text(encoding="utf-8")) or {}
    gates = gates_doc.get("gates", [])
    failed = False

    for gate in gates:
        if gate.get("required", True) and not run_gate(gate):
            failed = True

    if failed:
        print("Promotion gates FAILED.", file=sys.stderr)
        return 1

    print("All automated promotion gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
