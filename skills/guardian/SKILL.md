---
name: guardian
description: Runtime-neutral enforcement core for agent-skills. Validates manifest schemas, enforces preflight gates before council skills run, blocks unauthorized writes to .outputs/, and checks capability profiles. Optional — users choose whether to enable hard-gate enforcement. Read this skill to understand the Guardian pattern; wire the hooks to activate enforcement.
location: managed
context: reference
dependencies: []
optional: true
---

# Guardian

Runtime-neutral enforcement for the agent-skills suite. Guardian enforces
what skills alone cannot: manifest schema correctness, preflight gate
preconditions, and artifact write authority.

**Optional by design.** Skills work without Guardian. Enable it when you need
hard-gate enforcement — when you need the agent to be *physically blocked*
from proceeding rather than just instructed not to.

---

## What Guardian enforces

| Check | What it blocks | When it fires |
|-------|---------------|---------------|
| **Schema** | Malformed council artifacts (wrong fields, invalid values) | After artifact written (PostToolUse) or on demand |
| **Preflight** | Missing required inputs before council skill runs | Before `Skill(agent-council)` / `Skill(deep-*)` |
| **Output authority** | Direct `Write`/`Edit` to `.outputs/` without authority token | PreToolUse on any `.outputs/` write |
| **Session ID uniqueness** | Duplicate session IDs across artifacts | Before council session starts |
| **Capability profile** | Write-class tools used during inspect-profile tasks | PreToolUse on `Write`/`Edit` |

---

## Architecture

```
guardian.py                  ← Neutral core. Zero runtime imports.
                               CLI: guardian.py <check> [args]
                               Exit: 0=pass, 1=warn, 2=block

adapters/claude.py           ← Claude Code hook → guardian.py
adapters/opencode.py         ← OpenCode hook → guardian.py
adapters/kimi.py             ← Kimi Code hook → guardian.py

hooks/guard-council.py       ← Thin wrapper: Skill(agent-council) PreToolUse
hooks/guard-output.py        ← Thin wrapper: Write(.outputs/*) PreToolUse

schemas/
  council-artifact.schema.json  ← JSON Schema for council artifacts

references/
  policy.md                  ← All check IDs, contracts, exit codes
  hook-wiring-claude.md      ← Claude Code settings.json wiring guide
  preflight-pattern.md       ← Pre-flight pattern for hookless runtimes
```

---

## Quick start: enabling Guardian

### Step 1 — Copy scripts to your project

```bash
# Copy guardian core and adapters to your project root
cp skills/guardian/guardian.py .guardian/guardian.py
cp -r skills/guardian/adapters .guardian/adapters
cp -r skills/guardian/hooks .guardian/hooks
```

### Step 2 — Wire hooks for your runtime

See `references/hook-wiring-claude.md` for Claude Code.
See `references/preflight-pattern.md` for Codex / Gemini (no hooks).

### Step 3 — Choose which checks to activate

Start with just output authority (lowest friction):
```json
"PreToolUse": [
  {
    "matcher": "Write(*.outputs/*)",
    "hooks": [{"type": "command", "command": "python3 .guardian/hooks/guard-output.py"}]
  }
]
```

Add preflight when ready:
```json
{
  "matcher": "Skill(deep-review)",
  "hooks": [{"type": "command", "command": "python3 .guardian/hooks/guard-council.py"}]
}
```

---

## CLI reference

```bash
# Validate a council artifact's frontmatter
python3 guardian.py check-schema .outputs/review/20260512-120000-deep-review-abc123.md

# Preflight check before running agent-council in finding-driven mode
python3 guardian.py check-preflight agent-council \
  --mode finding-driven \
  --task-type review \
  --findings-count 5 \
  --scope-set true

# Check capability profile
python3 guardian.py check-capability review Write  # → BLOCK (inspect profile)
python3 guardian.py check-capability implementation Write  # → pass

# Check output authority
python3 guardian.py check-output-authority .outputs/review/my-report.md  # → BLOCK (no token)
GUARDIAN_OUTPUT_AUTHORITY=1 python3 guardian.py check-output-authority .outputs/review/my-report.md  # → pass

# Check session ID uniqueness
python3 guardian.py check-session-id abc123 --outputs-dir .outputs/
```

---

## Adding a new runtime

1. Copy `adapters/claude.py` → `adapters/{runtime}.py`
2. Change `HOOK_ARGS_ENV` and `HOOK_TOOL_ENV` to match the runtime's env vars
3. Verify `_tool_name()` and `_tool_input()` parse the runtime's hook payload format
4. Write a thin hook script (copy `hooks/guard-council.py`, change the import)
5. Register the hook in that runtime's settings file

The `guardian.py` core never changes. Only the adapter needs updating.

---

## References

- `references/policy.md` — All check IDs with input contracts and exit code semantics
- `references/hook-wiring-claude.md` — Claude Code `settings.json` wiring
- `references/preflight-pattern.md` — Codex / Gemini / hookless runtime pattern
