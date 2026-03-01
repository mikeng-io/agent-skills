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

Construct one prompt per domain in `bridge_input.domains`. Resolve `{expert_role}`, `{focus_areas}`, and `{standards}` from domain-registry using the **Lookup Protocol** in `domain-registry/README.md`. If no registry entry substantially covers the domain concern, synthesize a session-based virtual expert rather than falling back to a mismatched role. Adapt framing based on `task_type`:

```
You are a {expert_role}.

SCOPE: {scope}
TASK: {task_description}
CONTEXT: {context_summary}
INTENSITY: {intensity}
DOMAIN: {domain}

Focus areas: {focus_areas}
Standards:   {standards}

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
  "cross_domain_signals": [
    {
      "domain": "name of another domain that should examine this finding",
      "reason": "why this domain needs to weigh in"
    }
  ],
  "summary": "Brief summary",
  "confidence": "high | medium | low"
}

`cross_domain_signals` is optional. Use it when your findings have implications that fall outside your domain and require a different domain expert's perspective. Leave empty (`[]`) if no cross-domain expansion is needed.
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
  "connection_used": "native-dispatch | cli | api | http-api | mcp",
  "session_id": "...",
  "task_type": "review | planning | implementation | analysis | research",
  "status": "COMPLETED | SKIPPED | HALTED | ABORTED",
  "skip_reason": "...",
  "halt_reason": "...",
  "halt_message": "Advisory text to surface to the user",
  "domains_covered": ["domain1", "domain2"],
  "debate_rounds": 2,
  "outputs": [
    {
      "id": "X001",
      "type": "finding | recommendation | plan-item | implementation-note | observation",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO | null",
      "status": "confirmed | revised | discovered | null",
      "title": "Short title",
      "description": "Detailed description",
      "evidence": "Specific reference — file, line, quote",
      "action": "Recommended action or next step",
      "domain": "Which domain this belongs to",
      "agent": "Which agent or reviewer produced this"
    }
  ],
  "withdrawn_outputs": [...],
  "disputed_outputs": [
    {
      "output": {...},
      "unresolved_challenge": "Challenge text that was not resolved"
    }
  ],
  "verdict": "PASS | FAIL | CONCERNS | null",
  "confidence": "high | medium | low"
}
```

**Output ID prefixes:** `C` (claude), `G` (gemini), `X` (codex), `O` (opencode).

`debate_rounds`: number of rounds completed (0 for quick/consolidation-only, 1+ for debate mode). `null` when status is not COMPLETED.

---

## Output Deduplication

When multiple agents within a bridge produce similar outputs:

1. Assign unique IDs to all outputs first
2. Identify near-identical outputs (same `domain`, similar `title` and `description`)
3. Keep the highest-severity version; discard the duplicate
4. Record the merge in the JSONL event log

---

## Post-Analysis Protocol

After the initial parallel analysis, every bridge runs a post-analysis protocol before returning results. Two approaches are available — select based on intensity:

| Intensity | Approach | Rounds after initial analysis |
|-----------|----------|-------------------------------|
| `quick` | Consolidation pass | 1 (single cross-domain review) |
| `standard` | Two-round debate | 1 challenge + 1 response round |
| `thorough` | Continuous debate | Up to N rounds until convergence or max |

For Claude with Agent Teams, this entire section is superseded by the full `debate-protocol` skill, which provides the same structure with async SendMessage between teammates.

---

### Roles

Domain experts are determined by the orchestrating skill (deep-council, deep-review, etc.) before the bridge is called — the bridge receives them via `bridge_input.domains` and executes. Bridges do not perform domain selection.

Spawn these roles in parallel at the start of each round:

| Role | Count | Source | Purpose |
|------|-------|--------|---------|
| **Domain Expert** | One per domain in `bridge_input.domains` | domain-registry — expert role, focus areas, and standards per domain | Subject-matter analysis; defends and revises findings across rounds |
| **Challenger** | 1 (always) | Fixed role — no domain-registry lookup | Cross-domain challenge — Devil's Advocate equivalent; escalates or withdraws challenges each round |
| **Integration Checker** | 1 (always) | Fixed role — no domain-registry lookup | Surfaces cross-component issues; adds new findings as debates reveal interface gaps |

The total number of parallel agents per round = `len(active_domains) + 2` (one expert per domain, plus Challenger and Integration Checker).

The initial domain list is not fixed for the lifetime of a session. During each round, domain experts and the Integration Checker may signal that additional domains need to examine a finding. The orchestrator adds those domains to the active list before the next round, spawning fresh experts for them. See Between Rounds — Orchestrator Synthesis below.

---

### Round 1 — Initial Analysis (always runs, parallel)

All roles run simultaneously with no inter-agent communication. Each produces independent findings using the Agent Prompt Template above.

The orchestrator (bridge dispatcher or deep-council) collects all Round 1 outputs and moves to the between-rounds step.

---

### Between Rounds — Orchestrator Synthesis

The orchestrator reviews all outputs from the previous round and builds a **context packet** for the next round:

1. Collect `cross_domain_signals` from all outputs — identify domains not yet in the active domain list
2. Add any new domains to the active domain list; these experts will be spawned fresh in the next round
3. Identify open challenges from the Challenger that weren't responded to
4. Identify conflicts between Domain Experts (same issue, different conclusions)
5. Identify gaps (cross-cutting concerns not addressed by any active domain)
6. Group challenges by target domain so experts receive only what's directed at them

**Domain expansion rule:** A domain in `cross_domain_signals` that is already active → assign challenges to that existing expert. A domain not yet active → spawn a new expert for it in the next round, providing the relevant finding as their starting context.

**Context packet format:**

```json
{
  "round": 2,
  "active_domains": ["...current domain list including any newly added..."],
  "newly_added_domains": [
    {
      "domain": "name of newly added domain",
      "trigger_finding_id": "X001",
      "reason": "why this domain was added"
    }
  ],
  "previous_findings": ["...all outputs from previous round..."],
  "open_challenges": [
    {
      "challenge_id": "CH001",
      "target_finding_id": "X001",
      "challenge_text": "This finding assumes X but the evidence shows Y instead",
      "directed_at_domain": "domain name"
    }
  ],
  "synthesis": "Round 1: 5 findings. 2 challenged. 1 new domain added. Gap: coverage expanded."
}
```

If no open challenges, no conflicts, and no new domains to add → stop early (convergence). Do not run additional rounds.

---

### Round N — Challenge & Response

Existing domain experts, Challenger, and Integration Checker re-run with the context packet. Newly added domain experts run for the first time with a focused prompt scoped to their trigger finding.

**Existing domain expert prompt addition:**
```
Previous findings from your domain:
{their_previous_round_outputs}

Challenges directed at your findings:
{challenges_targeting_this_domain}

For each challenge:
- If you agree: withdraw or revise the finding (update severity or description)
- If you disagree: provide evidence-backed defense
- Mark each output with status: confirmed | revised | withdrawn
- If you identify additional domains that should examine your findings, include cross_domain_signals
```

**Newly added domain expert prompt (first appearance in Round N):**
```
You are a {expert_role}.

SCOPE: {scope}
CONTEXT: {context_summary}

You have been brought in because a finding in another domain has implications for yours.

Trigger finding:
{the finding that produced the cross_domain_signal for this domain}

Reason you were added:
{cross_domain_signal.reason}

Analyze this finding from your domain's perspective. Produce your own findings.
Include cross_domain_signals if you identify further domain expansion needed.
```

**Challenger prompt addition:**
```
All domain expert findings from previous round:
{all_previous_findings}

Your previous challenges and expert responses:
{challenge_history}

For each challenge:
- If the expert defended convincingly: withdraw your challenge
- If the defense is insufficient: escalate (raise severity, add evidence)
- Challenge findings from any newly added domain experts
- Add new challenges for findings you haven't challenged yet
```

**Integration Checker prompt addition:**
```
All findings and challenges from previous round, including newly added domain experts:
{all_previous_findings_and_challenges}

Add new cross-component findings that emerge from the ongoing debate.
Focus on: interface gaps revealed by challenges, cascading impacts of revised findings,
and cross-cutting issues that span the newly added domains.
```

---

### Termination Conditions

Stop running rounds when **any** of these is true:

| Condition | Description |
|-----------|-------------|
| Max rounds reached | `quick`: 0 rounds after initial; `standard`: 1; `thorough`: 3 |
| Convergence | No new findings or revisions compared to previous round |
| All challenges resolved | Every challenge is either withdrawn or defended (no `disputed` status) |

---

### Finding States

After debate completes, tag each output with a `status` field:

| Status | Meaning |
|--------|---------|
| `confirmed` | Survived at least one challenge round without revision |
| `revised` | Expert updated the finding in response to a challenge |
| `withdrawn` | Expert retracted (challenged and couldn't defend) |
| `disputed` | Unresolved — Challenger maintains challenge, expert maintains finding |
| `discovered` | New finding surfaced during a challenge round (not in Round 1) |

Withdrawn findings are excluded from the final `outputs` array but recorded in `withdrawn_outputs`.

---

### Context Passing Between Rounds

Since non-Claude bridges lack async messaging, context flows **explicitly** — the orchestrator embeds the full context packet in each Round N prompt:

| Bridge | Session continuity | Context injection |
|--------|-------------------|-------------------|
| OpenCode (HTTP API) | Session remembers Round 1 automatically | Send context packet as next message in same session |
| OpenCode (CLI) | No session state | Embed full Round 1 outputs + context packet in Round 2 prompt |
| Codex (MCP) | `threadId` maintains history | `codex-reply` with context packet as prompt |
| Codex (CLI) | No session state | New `codex exec` with embedded context |
| Gemini (subagents) | No cross-call state | New `gemini -p` call with embedded context |
| Claude (Task tool) | Parent agent holds all state | Spawn Round 2 sub-agents with context from parent |
| Claude (Agent Teams) | Teammates use SendMessage | Superseded by debate-protocol |

For bridges with session continuity (OpenCode HTTP, Codex MCP), the Round 2 prompt only needs to include the context packet — the session already has Round 1 history. For stateless bridges, embed the full previous-round findings in the prompt.

---

### Consolidation (after final round)

After debate terminates, the orchestrator runs a final consolidation:

1. Collect all `confirmed`, `revised`, and `discovered` outputs — these form the final `outputs` array
2. Collect `withdrawn` outputs into `withdrawn_outputs`
3. Collect `disputed` outputs into `disputed_outputs` with the unresolved challenge noted
4. Apply verdict logic from the Verdict Logic section above
5. Add any remaining cross-domain outputs (`domain: "cross-domain"`, `agent: "consolidation"`)

For `quick` intensity, the consolidation is the entire protocol — skip all debate rounds and go directly here after Round 1.

---

## Artifact Format

Every bridge saves two files per execution for auditability.

### JSONL event log

Path: `.outputs/bridges/{bridge}-{YYYYMMDD-HHMMSS}-{session_id}.jsonl`

Write events as they occur — one JSON object per line:

```jsonl
{"event": "bridge_start", "bridge": "{bridge}", "session_id": "{session_id}", "timestamp": "{ISO-8601}"}
{"event": "preflight", "step": "availability_check", "result": "found", "path": "{path}"}
{"event": "preflight", "step": "timeout_estimate", "value_seconds": "{n}"}
{"event": "dispatch", "mode": "multi-agent", "domains": ["{domain1}", "{domain2}"]}
{"event": "output", "id": "{id}", "severity": "{severity}", "title": "{title}"}
{"event": "bridge_complete", "status": "COMPLETED", "verdict": "{verdict}", "output_count": "{n}", "timestamp": "{ISO-8601}"}
```

### Markdown summary

Path: `.outputs/bridges/{bridge}-{YYYYMMDD-HHMMSS}-{session_id}.md`

YAML frontmatter + human-readable summary:

```yaml
---
bridge: {bridge}
session_id: {session_id}
timestamp: {ISO-8601}
task_type: {task_type}
domains: [{domain1}, {domain2}]
verdict: {verdict}
status: {status}
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
