#!/usr/bin/env python3
"""
Guardian — neutral enforcement core for agent-skills.

Zero runtime dependencies. Invokable via subprocess from any runtime.
Runtime-specific adapters (adapters/claude.py, etc.) translate hook
events into calls here.

CLI
---
  guardian.py check-schema <artifact-path> [--schema SCHEMA_NAME]
  guardian.py check-preflight <skill-name> [--mode MODE] [--task-type TYPE]
                               [--findings-count N] [--requirements-set true|false]
  guardian.py check-capability <task-type> <tool-name>
  guardian.py check-output-authority <path>
  guardian.py check-session-id <session-id> [--outputs-dir DIR]

Exit codes
----------
  0 — pass (allow)
  1 — warn (advisory, does not block)
  2 — block
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CheckResult:
    ok: bool
    message: str
    warnings: tuple[str, ...] = field(default_factory=tuple)
    suggestion: str = ""

    @property
    def exit_code(self) -> int:
        if not self.ok:
            return 2
        if self.warnings:
            return 1
        return 0


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_SKILLS = {
    "agent-council", "deep-review", "deep-audit", "deep-verify", "deep-research",
}

VALID_TASK_TYPES = {
    "review", "audit", "research", "analysis", "planning", "implementation",
}

VALID_MODES = {
    "review", "audit", "finding-driven", "research", "brainstorm", "design", "synthesis",
}

VALID_VERDICTS = {"PASS", "FAIL", "CONCERNS"}

VERDICT_REQUIRED_MODES = {"review", "audit", "finding-driven"}

INSPECT_TASK_TYPES = {"review", "audit", "research", "analysis", "planning"}
MODIFY_TASK_TYPES = {"implementation"}

BLOCKED_TOOLS_FOR_INSPECT = {"Write", "Edit", "NotebookEdit"}

OUTPUTS_PREFIXES = (".outputs/", "outputs/")

# Schemas: required fields + allowed values per artifact skill
ARTIFACT_SCHEMAS: dict[str, dict] = {
    "_base": {
        "required": ["skill", "agent_council_tier", "agent_council_mode", "session_id", "timestamp", "domains"],
        "allowed_values": {
            "agent_council_tier": {1, 2, 3},
            "agent_council_mode": VALID_MODES,
        },
    },
    "agent-council": {
        "required": ["skill", "tier", "mode", "task_type", "session_id", "timestamp", "domains"],
        "allowed_values": {
            "tier": {0, 1, 2, 3},
            "mode": VALID_MODES,
            "task_type": VALID_TASK_TYPES,
        },
    },
    "deep-review": {
        "required": ["skill", "agent_council_tier", "agent_council_mode", "session_id", "timestamp", "verdict", "domains"],
        "allowed_values": {
            "agent_council_tier": {1, 2, 3},
            "agent_council_mode": {"review", "finding-driven"},
            "verdict": VALID_VERDICTS,
        },
    },
    "deep-audit": {
        "required": ["skill", "agent_council_tier", "agent_council_mode", "session_id", "timestamp", "verdict", "domains", "requirements_audited"],
        "allowed_values": {
            "agent_council_tier": {1, 2, 3},
            "agent_council_mode": {"audit", "finding-driven"},
            "verdict": VALID_VERDICTS,
        },
    },
    "deep-verify": {
        "required": ["skill", "agent_council_tier", "agent_council_mode", "session_id", "timestamp", "verdict", "domains", "requirements_verified"],
        "allowed_values": {
            "agent_council_tier": {1, 2, 3},
            "agent_council_mode": {"finding-driven"},
            "verdict": VALID_VERDICTS,
        },
    },
    "deep-research": {
        "required": ["skill", "agent_council_tier", "agent_council_mode", "session_id", "timestamp", "domains"],
        "allowed_values": {
            "agent_council_tier": {1, 2, 3},
            "agent_council_mode": {"research"},
        },
    },
}

# Preflight requirements per skill
PREFLIGHT_RULES: dict[str, dict] = {
    "agent-council": {
        "required_args": ["scope", "task_type", "mode"],
        "finding_driven_requires_findings": True,
    },
    "deep-review": {
        "required_args": ["scope"],
        "finding_driven_requires_findings": True,
    },
    "deep-audit": {
        "required_args": ["scope"],
        "finding_driven_requires_findings": True,
        "fresh_audit_requires_requirements": True,
    },
    "deep-verify": {
        "required_args": ["scope"],
        "requires_requirements": True,
    },
    "deep-research": {
        "required_args": ["scope", "domains"],
    },
}


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _repo_root(start: Path | None = None) -> Path:
    """Walk up from start (or cwd) to find repo root (.git directory)."""
    here = start or Path.cwd()
    for candidate in [here, *here.parents]:
        if (candidate / ".git").exists():
            return candidate
    return here


def _guardian_root() -> Path:
    """Directory containing this script."""
    return Path(__file__).parent


def _parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from a markdown artifact. No PyYAML needed."""
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}

    result: dict = {}
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line or line.startswith(" "):
            i += 1
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()

        if raw == "" and i + 1 < len(lines) and lines[i + 1].startswith("- "):
            # Block sequence
            items = []
            i += 1
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].strip().strip("\"'"))
                i += 1
            result[key] = items
            continue

        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            result[key] = [v.strip().strip("\"'") for v in inner.split(",") if v.strip()] if inner else []
        elif raw.isdigit():
            result[key] = int(raw)
        elif raw in ("null", "~", ""):
            result[key] = None
        elif raw.lower() in ("true", "false"):
            result[key] = raw.lower() == "true"
        else:
            result[key] = raw.strip("\"'")
        i += 1
    return result


def _rel_path(path: str | Path, base: Path | None = None) -> str:
    base = base or Path.cwd()
    try:
        return str(Path(path).relative_to(base))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_schema(artifact_path: str, schema_name: str | None = None) -> CheckResult:
    """Validate a council artifact's YAML frontmatter against its schema."""
    p = Path(artifact_path)
    if not p.exists():
        return CheckResult(False, f"artifact not found: {artifact_path}",
                           suggestion="Ensure the artifact path is correct.")

    try:
        content = p.read_text(encoding="utf-8")
    except OSError as e:
        return CheckResult(False, f"cannot read artifact: {e}")

    fm = _parse_frontmatter(content)
    if not fm:
        return CheckResult(False, f"no YAML frontmatter found in {artifact_path}",
                           suggestion="Council artifacts must begin with --- frontmatter ---.")

    # Resolve schema
    skill_name = schema_name or fm.get("skill", "")
    schema = ARTIFACT_SCHEMAS.get(skill_name, ARTIFACT_SCHEMAS["_base"])

    errors: list[str] = []
    warnings: list[str] = []

    # Required fields
    for field_name in schema["required"]:
        val = fm.get(field_name)
        if val is None or val == "":
            errors.append(f"missing required field: {field_name}")

    # Allowed values
    for field_name, allowed in schema.get("allowed_values", {}).items():
        val = fm.get(field_name)
        if val is not None and val not in allowed:
            errors.append(f"field '{field_name}' has invalid value '{val}' — allowed: {sorted(str(v) for v in allowed)}")

    # Verdict rule: required for review/audit/finding-driven, should be null for others.
    # Agent-council artifacts use tier/mode; wrapper artifacts keep legacy
    # agent_council_tier/agent_council_mode fields for compatibility.
    mode = fm.get("mode") or fm.get("agent_council_mode", "")
    verdict = fm.get("verdict")
    if mode in VERDICT_REQUIRED_MODES and verdict is None:
        errors.append(f"field 'verdict' is required for mode '{mode}'")
    elif mode not in VERDICT_REQUIRED_MODES and verdict is not None:
        warnings = (*warnings, f"field 'verdict' is set to '{verdict}' but mode '{mode}' does not produce a verdict — expected null")

    # Session ID format
    session_id = fm.get("session_id", "")
    if session_id and not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$", str(session_id)):
        errors.append(f"session_id '{session_id}' contains invalid characters")

    # Timestamp format (loose check)
    ts = fm.get("timestamp", "")
    if ts and not re.match(r"^\d{4}-\d{2}-\d{2}", str(ts)):
        warnings = (*warnings, f"timestamp '{ts}' does not look like ISO-8601")

    if errors:
        return CheckResult(
            False,
            f"schema validation failed ({len(errors)} error(s)):\n  " + "\n  ".join(errors),
            warnings=tuple(warnings),
            suggestion="Fix the frontmatter fields listed above before proceeding.",
        )

    return CheckResult(True, f"schema valid: {_rel_path(artifact_path)}", warnings=tuple(warnings))


def check_preflight(
    skill_name: str,
    *,
    mode: str | None = None,
    task_type: str | None = None,
    findings_count: int | None = None,
    requirements_set: bool | None = None,
    scope_set: bool | None = None,
    domains_set: bool | None = None,
) -> CheckResult:
    """Validate that a skill invocation has the required inputs before dispatch."""
    rules = PREFLIGHT_RULES.get(skill_name)
    if rules is None:
        return CheckResult(True, f"no preflight rules for '{skill_name}' — skipping")

    errors: list[str] = []
    warnings: list[str] = []

    required_args = rules.get("required_args", [])

    if "scope" in required_args and scope_set is False:
        errors.append("'scope' is required — describe what to review")

    if "task_type" in required_args and task_type is None:
        errors.append("'task_type' is required — one of: " + ", ".join(sorted(VALID_TASK_TYPES)))
    elif task_type is not None and task_type not in VALID_TASK_TYPES:
        errors.append(f"'task_type' value '{task_type}' is not valid — allowed: {sorted(VALID_TASK_TYPES)}")

    if "mode" in required_args and mode is None:
        errors.append("'mode' is required — one of: " + ", ".join(sorted(VALID_MODES)))
    elif mode is not None and mode not in VALID_MODES:
        errors.append(f"'mode' value '{mode}' is not valid — allowed: {sorted(VALID_MODES)}")

    if "domains" in required_args and domains_set is False:
        errors.append("'domains' is required — list at least one domain to research")

    # finding-driven precondition
    if mode == "finding-driven" and rules.get("finding_driven_requires_findings"):
        if findings_count is None or findings_count == 0:
            errors.append(
                "'mode: finding-driven' requires prior findings — "
                "pass 'findings' (the prior council's finding list) before running"
            )

    # deep-verify always needs requirements
    if rules.get("requires_requirements") and requirements_set is False:
        errors.append(
            "'requirements' must be set for deep-verify — "
            "attach the spec or compliance checklist to verify against"
        )

    # fresh deep-audit should have requirements
    if rules.get("fresh_audit_requires_requirements") and mode != "finding-driven" and requirements_set is False:
        warnings.append("'requirements' not set — audit will run without explicit compliance criteria")

    if errors:
        return CheckResult(
            False,
            f"preflight failed for '{skill_name}' ({len(errors)} error(s)):\n  " + "\n  ".join(errors),
            warnings=tuple(warnings),
            suggestion="Provide the missing inputs before invoking the skill.",
        )

    return CheckResult(True, f"preflight passed for '{skill_name}'", warnings=tuple(warnings))


def check_capability(task_type: str, tool_name: str) -> CheckResult:
    """Block write-class tools when the active task_type maps to inspect profile."""
    if task_type not in VALID_TASK_TYPES:
        return CheckResult(True, f"unknown task_type '{task_type}' — skipping capability check")

    profile = "modify" if task_type in MODIFY_TASK_TYPES else "inspect"

    if profile == "inspect" and tool_name in BLOCKED_TOOLS_FOR_INSPECT:
        return CheckResult(
            False,
            f"capability violation: task_type='{task_type}' maps to profile=inspect, "
            f"but tool '{tool_name}' is a write-class tool",
            suggestion=(
                f"Use Read/Grep/Glob for inspection work. "
                f"To modify files, the task_type must be 'implementation'."
            ),
        )

    return CheckResult(True, f"capability OK: task_type='{task_type}' profile='{profile}' tool='{tool_name}'")


def check_output_authority(path: str) -> CheckResult:
    """Block direct writes to .outputs/ — all artifacts must go through council-state script."""
    rel = _rel_path(path)
    # Allow if the caller has set the authority env var (council-state script sets this)
    if os.environ.get("GUARDIAN_OUTPUT_AUTHORITY") == "1":
        return CheckResult(True, f"output authority granted via env: {rel}")

    for prefix in OUTPUTS_PREFIXES:
        if rel.startswith(prefix) or str(path).lstrip("/").find(prefix.rstrip("/")) != -1:
            return CheckResult(
                False,
                f"direct write to '{rel}' is blocked — all council artifacts must be written via council-state",
                suggestion=(
                    "Use the council-state script to write artifacts:\n"
                    "  GUARDIAN_OUTPUT_AUTHORITY=1 python3 skills/guardian/council_state.py write ..."
                ),
            )

    return CheckResult(True, f"path '{rel}' is not an outputs path — allowed")


def check_session_id(session_id: str, outputs_dir: str | None = None) -> CheckResult:
    """Verify session_id is unique across existing artifacts in .outputs/."""
    if not session_id or not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$", session_id):
        return CheckResult(
            False,
            f"session_id '{session_id}' is invalid — use alphanumeric + hyphens/dots/underscores only",
        )

    root = _repo_root()
    outputs = Path(outputs_dir) if outputs_dir else (root / ".outputs")

    if not outputs.exists():
        return CheckResult(True, f"session_id '{session_id}' is unique (.outputs/ does not exist yet)")

    collisions: list[str] = []
    for md_file in outputs.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            fm = _parse_frontmatter(content)
            if fm.get("session_id") == session_id:
                collisions.append(_rel_path(md_file, root))
        except OSError:
            continue

    if collisions:
        return CheckResult(
            False,
            f"session_id '{session_id}' already exists in:\n  " + "\n  ".join(collisions),
            suggestion="Generate a new session_id (timestamp + random suffix).",
        )

    return CheckResult(True, f"session_id '{session_id}' is unique")


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_result(result: CheckResult) -> int:
    for w in result.warnings:
        print(f"WARN: {w}", file=sys.stderr)
    if not result.ok:
        print(f"BLOCK: {result.message}", file=sys.stderr)
        if result.suggestion:
            print(f"\nSuggestion: {result.suggestion}", file=sys.stderr)
    return result.exit_code


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "yes")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    if not args:
        print(
            "usage: guardian.py <check> [args]\n"
            "checks: check-schema, check-preflight, check-capability,\n"
            "        check-output-authority, check-session-id",
            file=sys.stderr,
        )
        return 2

    command = args[0]
    rest = args[1:]

    def flag(name: str, default: str | None = None) -> str | None:
        for i, a in enumerate(rest):
            if a == f"--{name}" and i + 1 < len(rest):
                return rest[i + 1]
        return default

    def flag_bool(name: str) -> bool | None:
        v = flag(name)
        return _parse_bool(v) if v is not None else None

    def flag_int(name: str) -> int | None:
        v = flag(name)
        return int(v) if v is not None else None

    positional = [a for a in rest if not a.startswith("--")]

    if command == "check-schema":
        if not positional:
            print("usage: guardian.py check-schema <artifact-path> [--schema NAME]", file=sys.stderr)
            return 2
        result = check_schema(positional[0], schema_name=flag("schema"))
        return print_result(result)

    elif command == "check-preflight":
        if not positional:
            print("usage: guardian.py check-preflight <skill-name> [--mode MODE] ...", file=sys.stderr)
            return 2
        result = check_preflight(
            positional[0],
            mode=flag("mode"),
            task_type=flag("task-type"),
            findings_count=flag_int("findings-count"),
            requirements_set=flag_bool("requirements-set"),
            scope_set=flag_bool("scope-set"),
            domains_set=flag_bool("domains-set"),
        )
        return print_result(result)

    elif command == "check-capability":
        if len(positional) < 2:
            print("usage: guardian.py check-capability <task-type> <tool-name>", file=sys.stderr)
            return 2
        result = check_capability(positional[0], positional[1])
        return print_result(result)

    elif command == "check-output-authority":
        if not positional:
            print("usage: guardian.py check-output-authority <path>", file=sys.stderr)
            return 2
        result = check_output_authority(positional[0])
        return print_result(result)

    elif command == "check-session-id":
        if not positional:
            print("usage: guardian.py check-session-id <session-id> [--outputs-dir DIR]", file=sys.stderr)
            return 2
        result = check_session_id(positional[0], outputs_dir=flag("outputs-dir"))
        return print_result(result)

    else:
        print(f"unknown command: {command}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
