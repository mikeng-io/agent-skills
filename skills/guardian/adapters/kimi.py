#!/usr/bin/env python3
"""
Kimi Code → Guardian adapter.

Kimi Code hooks execute configured shell commands and pass hook context as
JSON on stdin. Kimi's public hook documentation does not define
KIMI_HOOK_ARGS or KIMI_HOOK_TOOL environment variables; stdin is canonical.

Hook event format (Kimi Code PreToolUse — assumed similar to Claude Code):
  stdin JSON: {
    "tool_name": "Write" | "Edit" | "Skill" | ...,
    "tool_input": { ... }
  }

Exit codes mirror guardian.py: 0=pass, 1=warn, 2=block. Kimi treats exit 2
as a block and non-0/non-2 exits as allow-with-log, so Guardian warnings are
advisory only in Kimi hooks.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_GUARDIAN = Path(__file__).parent.parent / "guardian.py"

def _load_payload() -> dict:
    if not sys.stdin.isatty():
        try:
            raw = sys.stdin.read(1024 * 1024)
            if raw.strip():
                return json.loads(raw)
        except (json.JSONDecodeError, OSError):
            pass

    return {}


def _tool_name(payload: dict) -> str:
    return (
        payload.get("tool_name")
        or ""
    )


def _tool_input(payload: dict) -> dict:
    return payload.get("tool_input") or payload.get("input") or {}


def _run_guardian(*args: str) -> int:
    return subprocess.run(
        [sys.executable, str(_GUARDIAN), *args],
        env={**os.environ},
    ).returncode


def _fail_open(reason: str) -> int:
    print(f"GUARDIAN FAIL-OPEN (kimi): {reason}", file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# Dispatchers
# ---------------------------------------------------------------------------

def dispatch_write_check(payload: dict) -> int:
    ti = _tool_input(payload)
    path = ti.get("file_path") or ti.get("path") or ""
    if not path:
        return _fail_open("could not extract file_path from Write/Edit hook payload")
    return _run_guardian("check-output-authority", path)


def dispatch_skill_preflight(payload: dict) -> int:
    ti = _tool_input(payload)
    skill = ti.get("skill") or ti.get("name") or ""
    if not skill:
        return _fail_open("could not extract skill name from hook payload")

    council_skills = {"agent-council", "deep-review", "deep-audit", "deep-verify", "deep-research"}
    if skill not in council_skills:
        return 0

    args = ti.get("args") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}

    mode = args.get("mode")
    task_type = args.get("task_type")
    scope = args.get("scope")
    findings = args.get("findings") or []
    requirements = args.get("requirements")
    domains = args.get("domains") or []

    cmd = [
        "check-preflight", skill,
        "--scope-set", "true" if scope else "false",
        "--domains-set", "true" if domains else "false",
        "--requirements-set", "true" if requirements else "false",
    ]
    if mode:
        cmd += ["--mode", mode]
    if task_type:
        cmd += ["--task-type", task_type]
    if isinstance(findings, list):
        cmd += ["--findings-count", str(len(findings))]
    return _run_guardian(*cmd)


def run_output_guard() -> None:
    payload = _load_payload()
    sys.exit(dispatch_write_check(payload))


def run_council_preflight() -> None:
    payload = _load_payload()
    sys.exit(dispatch_skill_preflight(payload))


if __name__ == "__main__":
    payload = _load_payload()
    tool = _tool_name(payload)
    if tool in ("Write", "Edit", "NotebookEdit"):
        sys.exit(dispatch_write_check(payload))
    elif tool == "Skill":
        sys.exit(dispatch_skill_preflight(payload))
    else:
        sys.exit(_fail_open(f"no dispatch rule for tool '{tool}'"))
