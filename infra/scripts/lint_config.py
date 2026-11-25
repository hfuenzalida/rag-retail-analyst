#!/usr/bin/env python3
"""Validate schema, runtime controls, env templates, and golden dataset."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|secret|password)\s*=\s*[^#\s][^\s#]+")


def lint_runtime_controls() -> list[str]:
    errors: list[str] = []
    path = REPO_ROOT / "infra" / "flags" / "runtime-controls.yaml"
    if not path.exists():
        return [f"missing runtime controls: {path}"]
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for section in ("defaults", "feature_flags", "kill_switches", "rollout"):
        if section not in data:
            errors.append(f"runtime-controls.yaml missing section: {section}")
    return errors


def lint_env_examples() -> list[str]:
    errors: list[str] = []
    for name in ("env.example", "env.preview.example", "env.staging.example", "env.production.example"):
        path = REPO_ROOT / "infra" / name
        if not path.exists():
            errors.append(f"missing env template: {name}")
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            if SECRET_PATTERN.search(stripped) and "change" not in stripped.lower():
                if any(
                    token in stripped.lower()
                    for token in (
                        "preview-postgres",
                        "staging-postgres",
                        "rotate",
                        "dev-secret",
                        "replace_me",
                        "example.com",
                    )
                ):
                    continue
                errors.append(f"{name}:{line_no} possible hard-coded secret")
    return errors


def lint_schema() -> list[str]:
    path = REPO_ROOT / "backend" / "app" / "db" / "schema.sql"
    if not path.exists():
        return [f"missing schema: {path}"]
    text = path.read_text(encoding="utf-8")
    required = ("CREATE TABLE", "vector", "rag_documents")
    return [f"schema.sql missing {token}" for token in required if token.lower() not in text.lower()]


def lint_golden_dataset() -> list[str]:
    path = REPO_ROOT / "memory-bank" / "eval" / "golden-questions.json"
    if not path.exists():
        return [f"missing golden dataset: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid golden-questions.json: {exc}"]
    if not isinstance(data, list):
        return ["golden-questions.json must be a list"]
    for item in data:
        if "id" not in item or "question" not in item:
            return ["golden question entries require id and question"]
    return []


def main() -> int:
    errors: list[str] = []
    errors.extend(lint_runtime_controls())
    errors.extend(lint_env_examples())
    errors.extend(lint_schema())
    errors.extend(lint_golden_dataset())

    if errors:
        for err in errors:
            print(f"config lint: {err}", file=sys.stderr)
        return 1

    print("Config lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
