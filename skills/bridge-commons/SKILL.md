---
name: bridge-commons
description: Shared contract for all bridge adapters — pre-flight SOP, standardized input/output schemas, artifact format, and status semantics. Read by any bridge or orchestrating skill. Not invocable standalone.
location: managed
context: reference
---

# Bridge Commons: Shared Contract

This document defines the shared contract that all bridge adapters implement. Every bridge reads this document and conforms to the schemas, status semantics, artifact format, and pre-flight ordering defined here.

## What Bridges Are

Bridges are reference adapters — they define how to dispatch tasks to specific AI runtimes (Claude Code sub-agents, Gemini CLI, Codex CLI, OpenCode). Each bridge:

- Is a **reference document**, not a runnable skill
- Is **read by orchestrating skills** (e.g., deep-council) via the `Read` tool
- Has its **instructions embedded** into Task agent prompts — not invoked separately
- Returns a **structured report** conforming to this contract
- Is **non-blocking** — unavailability produces `SKIPPED`, not a failure

---

## Pre-Flight SOP

Every bridge executes these checks in order before dispatching. Deviate only where a bridge's specific connection chain differs.

### Check ordering

1. **Primary connection** — preferred execution path (Task tool, HTTP server, MCP)
2. **Secondary connection** — CLI fallback
3. **Tertiary connection** — API fallback (if applicable to this bridge)
4. **Authentication** — verify credentials for the selected path
5. **Multi-agent capability** — detect and record; degrade gracefully if absent
6. **Timeout estimation** — calculate from scope + intensity

If none of steps 1–3 succeed → return `status: SKIPPED` immediately. Never block the calling orchestrator.

### HALTED vs SKIPPED

| Status | Cause | Orchestrator action |
|--------|-------|---------------------|
| `SKIPPED` | Non-fatal unavailability — CLI missing, timeout, parse failure | Non-blocking — continue with other bridges |
| `HALTED` | Requires user decision — no provider configured, explicit user abort | Surface `halt_message` and wait; do not continue |
| `ABORTED` | User chose to stop the entire operation | Stop the orchestrator |
| `COMPLETED` | Task ran and outputs are available | Include in synthesis |

---

## Timeout Estimation

Calculate per request from scope and intensity. Never hardcode.

| Scope | Base timeout |
|-------|-------------|
| < 5 files or < 500 LOC | 60 s |
| 5–20 files or < 2,000 LOC | 180 s |
| 20–50 files or < 10,000 LOC | 300 s |
| 50+ files or 10,000+ LOC | 600 s |

| Intensity | Multiplier |
|-----------|-----------|
| `quick` | 0.5 |
| `standard` | 1.0 |
| `thorough` | 1.5 |

Apply any bridge-specific multiplier on top (e.g., OpenCode applies 1.5× for provider routing overhead).

```
final_timeout = base_timeout × intensity_multiplier × bridge_multiplier
```

Wrap every CLI invocation with `timeout {final_timeout}` or equivalent.

---

## Input Schema

All bridges accept this standard input:

```json
{
  "bridge_input": {
    "session_id": "unique identifier for this session",
    "scope": "files, topics, or description of what to work on",
    "task_description": "what the agent should do",
    "task_type": "review | planning | implementation | analysis | research",
    "domains": ["domain1", "domain2"],
    "context_summary": "brief description of context",
    "intensity": "quick | standard | thorough"
  }
}
```

`task_type` drives how agent prompts are framed:

| task_type | Output items use | Framing |
|-----------|-----------------|---------|
| `review` | `finding`, `recommendation` | "What is wrong or could be improved?" |
| `analysis` | `finding`, `observation` | "What does this tell us?" |
| `planning` | `plan-item` | "What should be done and in what order?" |
| `implementation` | `implementation-note` | "What is needed to build this correctly?" |
| `research` | `observation`, `recommendation` | "What do we know? What are the options?" |

---

## Agent Prompt Template

Construct agent prompts from `bridge_input`. Adapt framing based on `task_type`:

```
You are a {expert_role}.

SCOPE: {scope}
TASK: {task_description}
CONTEXT: {context_summary}
INTENSITY: {intensity}
DOMAINS: {domains}

{domain-specific focus areas from domain-registry}

Return your output as JSON:
{
  "agent": "{expert_role}",
  "domain": "{domain}",
  "outputs": [
    {
      "id": "",
      "type": "finding | recommendation | plan-item | implementation-note | observation",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO | null",
      "title": "Short title",
      "description": "Detailed description",
      "evidence": "Specific reference",
      "action": "Recommended action"
    }
  ],
  "summary": "Brief summary",
  "confidence": "high | medium | low"
}
```

---

## Output Item Types

| `type` | Severity applies? | Use when |
|--------|-------------------|---------|
| `finding` | Yes | Identifying a problem or risk |
| `recommendation` | Yes | Suggesting an improvement |
| `plan-item` | No (use `null`) | A step or action to execute |
| `implementation-note` | No (use `null`) | A detail needed during implementation |
| `observation` | Optional | A neutral insight or data point |

---

## Severity Scale

| Severity | Meaning |
|----------|---------|
| `CRITICAL` | Must be addressed immediately; blocks progress |
| `HIGH` | Significant risk or quality issue |
| `MEDIUM` | Moderate concern; should be addressed |
| `LOW` | Minor issue; worthwhile to fix |
| `INFO` | Informational only |
| `null` | Not applicable (plan items, observations) |

---

## Verdict Logic

Apply only when `task_type` is `review` or `analysis`. Set `null` for all other task types.

| Verdict | Condition |
|---------|-----------|
| `FAIL` | Any `CRITICAL` output |
| `CONCERNS` | One or more `HIGH` outputs, or three or more `MEDIUM` outputs |
| `PASS` | No `CRITICAL` or `HIGH`; only `MEDIUM`, `LOW`, or `INFO` |

---

## Output Schema

```json
{
  "bridge": "claude | gemini | codex | opencode",
  "model_family": "anthropic/claude | google/gemini | openai/codex | multi-provider",
  "connection_used": "task-tool | agent-teams | claude-cli | api | cli | http-api | mcp",
  "session_id": "...",
  "task_type": "review | planning | implementation | analysis | research",
  "status": "COMPLETED | SKIPPED | HALTED | ABORTED",
  "skip_reason": "...",
  "halt_reason": "...",
  "halt_message": "Advisory text to surface to the user",
  "domains_covered": ["domain1", "domain2"],
  "outputs": [
    {
      "id": "X001",
      "type": "finding | recommendation | plan-item | implementation-note | observation",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO | null",
      "title": "Short title",
      "description": "Detailed description",
      "evidence": "Specific reference — file, line, quote",
      "action": "Recommended action or next step",
      "domain": "Which domain this belongs to",
      "agent": "Which agent or reviewer produced this"
    }
  ],
  "verdict": "PASS | FAIL | CONCERNS | null",
  "confidence": "high | medium | low"
}
```

**Output ID prefixes:** `C` (claude), `G` (gemini), `X` (codex), `O` (opencode).

---

## Output Deduplication

When multiple agents within a bridge produce similar outputs:

1. Assign unique IDs to all outputs first
2. Identify near-identical outputs (same `domain`, similar `title` and `description`)
3. Keep the highest-severity version; discard the duplicate
4. Record the merge in the JSONL event log

---

## Artifact Format

Every bridge saves two files per execution for auditability.

### JSONL event log

Path: `.outputs/bridges/{bridge}-{YYYYMMDD-HHMMSS}-{session_id}.jsonl`

Write events as they occur — one JSON object per line:

```jsonl
{"event": "bridge_start", "bridge": "gemini", "session_id": "abc123", "timestamp": "2026-03-01T08:00:00Z"}
{"event": "preflight", "step": "availability_check", "result": "found", "path": "/usr/local/bin/gemini"}
{"event": "preflight", "step": "timeout_estimate", "value_seconds": 180}
{"event": "dispatch", "mode": "single-agent", "domains": ["security", "api"]}
{"event": "output", "id": "G001", "severity": "HIGH", "title": "Missing input validation"}
{"event": "bridge_complete", "status": "COMPLETED", "verdict": "CONCERNS", "output_count": 3, "timestamp": "2026-03-01T08:03:22Z"}
```

### Markdown summary

Path: `.outputs/bridges/{bridge}-{YYYYMMDD-HHMMSS}-{session_id}.md`

YAML frontmatter + human-readable summary:

```yaml
---
bridge: gemini
session_id: abc123
timestamp: 2026-03-01T08:00:00Z
task_type: review
domains: [security, api]
verdict: CONCERNS
status: COMPLETED
---
```

### Directory creation

```bash
mkdir -p .outputs/bridges
```

---

## CLI Error Handling

Common patterns across all CLI-based bridges:

| Exit code | Meaning | Action |
|-----------|---------|--------|
| `0` | Success | Parse output |
| `124` | Timeout (from `timeout` wrapper) | Return `SKIPPED`, reason: `timeout_after_{n}s` |
| Other non-zero | CLI error | Capture stderr; return `SKIPPED` with detail |

Invalid or unparseable output → attempt to extract structured content; if unrecoverable, return `SKIPPED`.

---

## Notes

- Bridges do not modify source files unless `task_type` is `implementation`
- Bridges do not make external network calls beyond what their connected runtime provides
- `SKIPPED` is always non-blocking — orchestrators must handle it gracefully
- `HALTED` requires explicit user input before the bridge can continue or be skipped
- All fields in the output schema are required; use `null` where not applicable
