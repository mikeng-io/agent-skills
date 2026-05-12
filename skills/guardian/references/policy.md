# Guardian Policy Reference

All checks, their input contracts, and exit code semantics.

---

## Exit Code Semantics

| Code | Meaning | Effect |
|------|---------|--------|
| `0` | Pass | Action proceeds |
| `1` | Warn | Action proceeds; warning logged |
| `2` | Block | Action is halted; message shown to agent |

Adapters forward these exit codes directly to the runtime's hook system.

---

## Check: `check-schema`

**ID:** `G-SCHEMA`

Validates a council artifact's YAML frontmatter against its schema.

```bash
guardian.py check-schema <artifact-path> [--schema SCHEMA_NAME]
```

**Inputs:**

| Argument | Required | Description |
|----------|----------|-------------|
| `artifact-path` | yes | Path to the `.md` artifact file |
| `--schema` | no | Schema name override (defaults to `skill` field in frontmatter) |

**What it checks:**

1. File exists and is readable
2. YAML frontmatter is present (`--- ... ---`)
3. All required fields for the skill are present and non-empty
4. Field values are within allowed sets (tier, mode, verdict)
5. `verdict` is set for review/audit/finding-driven modes; null for others
6. `session_id` matches `^[a-zA-Z0-9][a-zA-Z0-9_.-]*$`
7. `timestamp` looks like ISO-8601

**Required fields by skill:**

| Skill | Required fields |
|-------|----------------|
| `deep-review` | skill, agent_council_tier, agent_council_mode, session_id, timestamp, verdict, domains |
| `deep-audit` | + requirements_audited |
| `deep-verify` | + requirements_verified |
| `deep-research` | skill, agent_council_tier, agent_council_mode, session_id, timestamp, domains |

**Exit:** 0 (valid), 1 (valid with warnings), 2 (invalid — missing/wrong fields)

---

## Check: `check-preflight`

**ID:** `G-PREFLIGHT`

Validates required inputs are present before a council skill is invoked.

```bash
guardian.py check-preflight <skill-name> \
  [--mode MODE] \
  [--task-type TYPE] \
  [--findings-count N] \
  [--requirements-set true|false] \
  [--scope-set true|false] \
  [--domains-set true|false]
```

**Inputs:**

| Argument | Required | Description |
|----------|----------|-------------|
| `skill-name` | yes | One of: agent-council, deep-review, deep-audit, deep-verify, deep-research |
| `--mode` | conditional | Required for `agent-council` |
| `--task-type` | conditional | Required for `agent-council` |
| `--findings-count` | conditional | Integer; required > 0 when mode is `finding-driven` |
| `--requirements-set` | conditional | `true`/`false`; required true for `deep-verify` |
| `--scope-set` | no | `true`/`false` |
| `--domains-set` | no | `true`/`false`; required true for `deep-research` |

**Rules by skill:**

| Skill | Blocks when |
|-------|------------|
| `agent-council` | scope, task_type, or mode missing; OR mode=finding-driven AND findings-count=0 |
| `deep-review` | mode=finding-driven AND findings-count=0 |
| `deep-audit` | mode=finding-driven AND findings-count=0 |
| `deep-verify` | requirements-set=false |
| `deep-research` | scope or domains missing |

**Exit:** 0 (ready), 2 (blocked — lists missing inputs with suggestion)

---

## Check: `check-capability`

**ID:** `G-CAPABILITY`

Blocks write-class tools when the active task_type maps to `inspect` profile.

```bash
guardian.py check-capability <task-type> <tool-name>
```

**Capability profile mapping:**

| task_type | Profile | Blocked tools |
|-----------|---------|--------------|
| review, audit, research, analysis, planning | `inspect` | Write, Edit, NotebookEdit |
| implementation | `modify` | (none) |

**Exit:** 0 (allowed), 2 (blocked — capability violation)

**Note:** This check requires the caller to know the active `task_type`. The adapter
must supply it from the current session context (e.g., an active-session marker file
or the hook payload). See `preflight-pattern.md` for the session marker pattern.

---

## Check: `check-output-authority`

**ID:** `G-OUTPUT`

Blocks direct writes to `.outputs/` paths without the authority token.

```bash
guardian.py check-output-authority <path>
```

**Authority token:** Set `GUARDIAN_OUTPUT_AUTHORITY=1` in the environment to allow
the write. Only the `council-state` script (or equivalent) should set this token.

**Paths guarded:** Any path starting with `.outputs/` or `outputs/`.

**Exit:** 0 (not an outputs path, or token set), 2 (blocked — direct write attempt)

---

## Check: `check-session-id`

**ID:** `G-SESSION`

Verifies a session ID is unique across existing artifacts in `.outputs/`.

```bash
guardian.py check-session-id <session-id> [--outputs-dir DIR]
```

**What it does:** Scans all `.md` files in `.outputs/` (recursively), parses their
frontmatter, and checks for a matching `session_id` field.

**Exit:** 0 (unique), 2 (collision found — lists conflicting files)

---

## Fail-Open Logging

When an adapter cannot extract required context from a hook payload (e.g., the
payload format is unexpected), it logs a fail-open event and exits 0 (allows the
action). Fail-open events are logged to `.guardian/logs/failopen.jsonl`.

Monitor this file to detect unexpected hook payload formats. Repeated fail-open
events for the same tool indicate the adapter needs updating.
