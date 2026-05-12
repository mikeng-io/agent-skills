#!/usr/bin/env python3
"""
Claude Code → Guardian adapter.

Reads Claude Code hook event from stdin or CLAUDE_HOOK_ARGS env var,
extracts relevant context, and dispatches to guardian.py checks.

Event format (Claude Code PreToolUse):
  stdin JSON: {
    "tool_name": "Skill" | "Write" | "Edit" | ...,
    "tool_input": { ... }
  }

Exit codes mirror guardian.py: 0=pass, 1=warn, 2=block.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_GUARDIAN = Path(__file__).parent.parent / "guardian.py"


# ---------------------------------------------------------------------------
# Hook payload parsing
# ---------------------------------------------------------------------------

def _load_payload() -> dict:
    """Read hook payload from stdin first, then CLAUDE_HOOK_ARGS env var."""
    # Try stdin (Claude Code sends payload here for PreToolUse)
    if not sys.stdin.isatty():
        try:
            raw = sys.stdin.read(1024 * 1024)  # 1 MB cap
            if raw.strip():
                return json.loads(raw)
        except (json.JSONDecodeError, OSError):
            pass

    # Fall back to env var
    raw = os.environ.get("CLAUDE_HOOK_ARGS", "")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

    return {}


def _tool_name(payload: dict) -> str:
    return (
        payload.get("tool_name")
        or os.environ.get("CLAUDE_HOOK_TOOL", "")
        or ""
    )


def _tool_input(payload: dict) -> dict:
    return payload.get("tool_input") or {}


def _file_path(tool_input: dict) -> str:
    return (
        tool_input.get("file_path")
        or tool_input.get("path")
        or ""
    )


def _skill_name(tool_input: dict) -> str:
    return (
        tool_input.get("skill")
        or tool_input.get("name")
        or ""
    )


def _skill_args(tool_input: dict) -> dict:
    """Parse skill args — may be a JSON string, a dict, or free-form text."""
    raw = tool_input.get("args") or tool_input.get("input") or ""
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip().startswith("{"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    return {}


# ---------------------------------------------------------------------------
# Guardian invocation
# ---------------------------------------------------------------------------

def _run_guardian(*args: str) -> int:
    result = subprocess.run(
        [sys.executable, str(_GUARDIAN), *args],
        env={**os.environ},
    )
    return result.returncode


def _fail_open(reason: str) -> int:
    """Log a fail-open event and allow the action (exit 0)."""
    print(f"GUARDIAN FAIL-OPEN: {reason}", file=sys.stderr)
    _write_failopen_log(reason)
    return 0


def _write_failopen_log(reason: str) -> None:
    try:
        import time
        log_dir = Path(".guardian/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        entry = json.dumps({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "adapter": "claude",
            "reason": reason,
        })
        with open(log_dir / "failopen.jsonl", "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Dispatchers
# ---------------------------------------------------------------------------

def dispatch_write_check(payload: dict) -> int:
    """PreToolUse: Write / Edit — check output authority."""
    ti = _tool_input(payload)
    path = _file_path(ti)
    if not path:
        return _fail_open("could not extract file_path from Write/Edit hook payload")
    return _run_guardian("check-output-authority", path)


def dispatch_skill_preflight(payload: dict) -> int:
    """PreToolUse: Skill — check preflight for council skills."""
    ti = _tool_input(payload)
    skill = _skill_name(ti)
    if not skill:
        return _fail_open("could not extract skill name from Skill hook payload")

    council_skills = {"agent-council", "deep-review", "deep-audit", "deep-verify", "deep-research"}
    if skill not in council_skills:
        return 0  # Not a council skill — allow

    args = _skill_args(ti)
    mode = args.get("mode") or args.get("agent_council_mode")
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


def dispatch_capability_check(payload: dict, task_type: str) -> int:
    """Check capability profile for a write-class tool call."""
    tool = _tool_name(payload)
    if not tool or not task_type:
        return 0
    return _run_guardian("check-capability", task_type, tool)


# ---------------------------------------------------------------------------
# Entry points (called from hook scripts)
# ---------------------------------------------------------------------------

def run_output_guard() -> None:
    payload = _load_payload()
    sys.exit(dispatch_write_check(payload))


def run_council_preflight() -> None:
    payload = _load_payload()
    sys.exit(dispatch_skill_preflight(payload))


def run_schema_validation(artifact_path: str, schema_name: str | None = None) -> None:
    cmd = ["check-schema", artifact_path]
    if schema_name:
        cmd += ["--schema", schema_name]
    sys.exit(_run_guardian(*cmd))


if __name__ == "__main__":
    # When invoked directly: guardian adapter dispatch based on tool name
    payload = _load_payload()
    tool = _tool_name(payload)

    if tool in ("Write", "Edit", "NotebookEdit"):
        sys.exit(dispatch_write_check(payload))
    elif tool == "Skill":
        sys.exit(dispatch_skill_preflight(payload))
    else:
        # Unknown tool — fail open
        sys.exit(_fail_open(f"no dispatch rule for tool '{tool}'"))
