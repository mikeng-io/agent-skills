---
name: deep-council
description: Multi-model review council. Dispatches review tasks to all available bridge adapters (Claude, Gemini, Codex, OpenCode), each of which runs internal sub-agents. Synthesizes findings across model families using debate-protocol. Usable standalone or as a second-pass from deep-verify. Orchestrator-agnostic — can be invoked by Claude Code, OpenCode, or Codex CLI.
location: managed
context: fork
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
  - Write
  - Bash(mkdir *)
  - Bash(ls *)
  - Bash(which *)
  - Bash(cat *)
---

# Deep Council: Multi-Model Review Council

Execute this skill to run a multi-model review using all available bridge adapters, synthesizing findings across model families.

## Execution Instructions

When invoked, you will:

1. Extract context and classify scope
2. Read and inventory available bridges
3. Dispatch all available bridges in parallel via Task agents
4. Synthesize findings across bridges using debate-protocol logic
5. Produce a consolidated multi-model report

---

## Step 1: Context Extraction

Apply deep-context analysis (inline — do not invoke as a separate skill):

```yaml
council_context:
  review_scope: ""        # Files and/or description extracted from conversation
  context_summary: ""     # What is being reviewed and why
  artifact_type: ""       # code | financial | marketing | creative | research | mixed
  domains: []             # Selected from domain-registry signals in conversation
  intensity: "standard"   # quick | standard | thorough (from user request)
  review_id: ""           # Generate a unique ID: council-{YYYYMMDD-HHmmss}
  task_type: "review"     # review | audit | research | planning | analysis | generic
                          # Extracted from user intent — defaults to "review" for council runs
```

**Extract from conversation:**
- Files mentioned → `review_scope`
- Topics, concerns, intent → `context_summary`
- Domain signals → match against domain-registry trigger_signals

Read domain-registry to confirm domain selection:
```
Read: [skills-root]/domain-registry/domains/technical.md
Read: [skills-root]/domain-registry/domains/business.md
Read: [skills-root]/domain-registry/domains/creative.md
```

---

## Step 1B: Model Discovery & Settings

Before dispatching bridges, discover what models and providers are configured and confirm with the user. This step runs once per project — results are cached in `.bridge-settings.json`.

### Load or Discover

```bash
# Check for existing settings
cat .bridge-settings.json 2>/dev/null
```

If `.bridge-settings.json` exists and is current → **load settings and proceed to Step 2** (skip user prompt unless user passes `--reconfigure`).

If not found or `--reconfigure` → run discovery:

```bash
# Codex: list available models
codex models list 2>/dev/null

# OpenCode: list authenticated providers
opencode auth list 2>/dev/null

# Gemini: check availability
which gemini 2>/dev/null && echo "available"
```

### Present to User

Show discovered configuration:

```
Available bridges for this review:

  [claude]     ✓ Always available (Task sub-agents)
  [gemini]     ✓ CLI found           Model: {gemini default}
  [codex]      ✓ MCP configured      Models: {from codex models list}
  [opencode]   ✓ Providers: {list}   Default: {provider/model}

Reasoning level (applies to Codex):  medium / high / xhigh  [medium]

Enable/disable bridges, select models, or press Enter to accept defaults.
```

Wait for user input. Accept `Enter` to use defaults.

### Save Settings

```json
// .bridge-settings.json
{
  "bridges": {
    "claude":    { "enabled": true },
    "gemini":    { "enabled": true },
    "codex":     { "enabled": true,  "model": null },
    "opencode":  { "enabled": true,  "model": null }
  },
  "reasoning_level": "medium",
  "updated": "{ISO-8601}",
  "ttl_hours": 24
}
```

`model: null` means use the bridge's runtime-detected latest model.

On load, if `(current_time - updated) > ttl_hours` → force re-discovery even without `--reconfigure`.

Apply these settings when dispatching bridges in Step 4.

---

## Step 2: Read Bridge Reference Docs

Use the Read tool to load each bridge's reference document:

```
Read: [skills-root]/bridge-claude/SKILL.md
Read: [skills-root]/bridge-gemini/SKILL.md
Read: [skills-root]/bridge-codex/SKILL.md
Read: [skills-root]/bridge-opencode/SKILL.md
```

These files define exactly how each bridge executor should operate. Their instructions will be embedded verbatim into Task agent prompts.

---

## Step 3: Check Bridge Availability

For each bridge, determine availability:

```yaml
bridge_claude:
  status: always_available   # Task tool dispatch, no CLI needed

bridge_gemini:
  check: "which gemini"
  status: available | unavailable

bridge_codex:
  check_mcp: "cat .mcp.json 2>/dev/null | grep -i codex"
  check_cli: "which codex"
  status: available_mcp | available_cli | unavailable

bridge_opencode:
  check_mcp: "cat .mcp.json 2>/dev/null | grep -i opencode"
  check_cli: "which opencode"
  status: available_mcp | available_cli | unavailable
```

Build availability list: `available_bridges = [bridge names that are available]`
Build skipped list: `skipped_bridges = [bridge names that are unavailable]`

At least one bridge must return COMPLETED for synthesis to proceed. If zero bridges complete, emit ABORTED with explanation.

---

## Step 4: Dispatch Bridges in Parallel

For each available bridge, spawn a Task agent. The Task prompt embeds:
1. The full bridge SKILL.md instructions (read in Step 2)
2. The specific bridge_input for this review

### Bridge Input (same for all bridges)

```json
{
  "bridge_input": {
    "session_id": "{review_id}",
    "review_id": "{review_id}",
    "scope": "{review_scope}",
    "review_scope": "{review_scope}",
    "task_type": "{task_type}",
    "task_description": "{context_summary}",
    "domains": {domains},
    "context_summary": "{context_summary}",
    "intensity": "{intensity}"
  }
}
```

`session_id` and `scope` are the bridge-commons canonical field names; `review_id` and `review_scope` are aliases for backward compatibility.

### Task Prompt Template (for each bridge)

```
You are executing the {bridge_name} review bridge.

## Bridge Instructions

{full contents of bridge-{name}/SKILL.md}

## Your Input

{bridge_input JSON}

## Your Task

Follow the bridge instructions exactly. Check availability first (if required),
then execute the review with the provided input. Return the complete bridge
report JSON as your final output.
```

### Parallel Dispatch

Spawn ALL available bridge Task agents simultaneously:
```
Task: bridge-claude executor (always launched)
Task: bridge-gemini executor (if gemini available)
Task: bridge-codex executor (if codex available)
Task: bridge-opencode executor (if opencode available)
```

Wait for ALL tasks to complete before proceeding.

---

## Step 5: Collect Bridge Reports

Collect all bridge reports. Each should conform to its bridge's output format:
- `bridge_claude_report` — findings, verdict, domains_covered
- `bridge_gemini_report` — findings, verdict, status (may be SKIPPED)
- `bridge_codex_report` — findings, verdict, status (may be SKIPPED)
- `bridge_opencode_report` — findings, verdict, status, models_used

SKIPPED bridges are noted but do not block synthesis.

### HALTED Bridges

If any bridge returns `status: HALTED`:

1. Surface the bridge's `halt_message` to the user
2. Offer: [skip this bridge / retry after setup / abort entire review]
3. **Non-interactive default**: auto-SKIPPED with a warning in the report
   (`"auto_skipped_halted_bridges": [{"bridge": "...", "halt_reason": "..."}]`)
4. Continue council synthesis with remaining COMPLETED bridges

HALTED does not block the council — it is surfaced and handled, then the council proceeds.

---

## Step 6: Cross-Bridge Synthesis

Apply debate-protocol logic inline (do not invoke debate-protocol as a separate skill — embed its synthesis logic directly):

### Finding Classification

For each unique finding across all bridges:

```yaml
multi_model_confirmed:
  condition: "Finding confirmed by 2+ bridge reports"
  note: "Highest confidence — multiple model families agree"
  action: "Elevate to multi-model-confirmed status"

single_source:
  condition: "Finding from exactly 1 bridge"
  note: "Medium confidence — single model family"
  action: "Retain with bridge attribution"

disputed:
  condition: "Finding present in 1+ bridges but explicitly contradicted by another"
  note: "Low confidence — model families disagree"
  action: "Flag as disputed with both positions"
```

### Synthesis Rules

1. **Deduplication**: Findings with >70% description overlap across bridges → merge into single finding (inherit highest severity, list all contributing bridges)
2. **Severity escalation**: If 2+ bridges independently rate the same issue as HIGH or CRITICAL → escalate to top severity
3. **Devil's Advocate application**: Apply DA weight across cross-bridge perspective (a finding challenged by one bridge's DA but confirmed by another's domain expert = disputed)
4. **Confidence calculation**: `multi-model-confirmed` > `single-source (claude)` > `single-source (other bridge)` > `disputed`

### Cross-Bridge Verdict

**Note:** Cross-bridge verdict thresholds deliberately differ from per-bridge bridge-commons thresholds.
Per-bridge: FAIL = any single CRITICAL finding (that bridge's internal debate flagged it).
Cross-bridge: FAIL = multi-model-confirmed CRITICAL (requires multiple model families to agree).
This is intentional — cross-bridge synthesis accounts for depth asymmetry (some bridges run richer
debate than others) by requiring multi-model agreement before escalating to FAIL.

```yaml
FAIL:
  - Any multi-model-confirmed CRITICAL finding
  - Any single-source CRITICAL finding (from claude bridge — always available)
  - 3+ multi-model-confirmed HIGH findings

CONCERNS:
  - 1-2 multi-model-confirmed HIGH findings
  - Multiple single-source HIGH findings
  - Any disputed CRITICAL/HIGH finding

PASS:
  - No CRITICAL/HIGH confirmed findings
  - Only MEDIUM/LOW/INFO across all bridges
```

---

## Step 7: Produce Output

### Council Report Structure

```json
{
  "type": "deep-council",
  "review_id": "{review_id}",
  "verdict": "PASS | FAIL | CONCERNS",
  "timestamp": "{ISO-8601}",
  "bridges_invoked": ["claude", "gemini", "codex", "opencode"],
  "bridges_available": ["claude", "gemini"],
  "bridges_skipped": ["codex", "opencode"],
  "skip_reasons": {
    "codex": "CLI not found, MCP not configured",
    "opencode": "CLI not found, MCP not configured"
  },
  "domains_covered": ["{domain1}", "{domain2}"],
  "intensity": "standard",
  "multi_model_confirmed": [
    {
      "id": "MMC001",
      "severity": "HIGH",
      "title": "...",
      "description": "...",
      "evidence": "...",
      "remediation": "...",
      "confirmed_by": ["{bridge1}", "{bridge2}"],
      "source_findings": [
        {"bridge": "{bridge1}", "finding_id": "{original-id}"},
        {"bridge": "{bridge2}", "finding_id": "{original-id}"}
      ],
      "domains": ["{domain}"]
    }
  ],
  "single_source_findings": [
    {
      "id": "SS001",
      "severity": "MEDIUM",
      "title": "...",
      "description": "...",
      "source_bridge": "{bridge}",
      "domains": ["{domain}"]
    }
  ],
  "disputed_findings": [
    {
      "id": "D001",
      "title": "...",
      "positions": [
        {"bridge": "claude", "severity": "HIGH", "position": "..."},
        {"bridge": "gemini", "severity": "LOW", "position": "..."}
      ]
    }
  ],
  "synthesis_notes": "Summary of cross-model analysis"
}
```

If zero bridges return COMPLETED, emit the following instead and stop:

```json
{
  "status": "ABORTED",
  "abort_reason": "No bridges returned COMPLETED results",
  "bridges_attempted": ["..."],
  "bridges_skipped": ["..."],
  "bridges_halted": ["..."]
}
```

---

## Step 8: Save Artifact

Save to `.outputs/council/{YYYYMMDD-HHMMSS}-council-{review_id}.md` with YAML frontmatter:

```yaml
---
skill: deep-council
timestamp: {ISO-8601}
artifact_type: council
domains: [{domain1}, {domain2}]
verdict: PASS | FAIL | CONCERNS
bridges_available: [{bridge1}, {bridge2}]
bridges_skipped: [{bridge3}]
review_id: "{unique id}"
context_summary: "{brief description of what was reviewed}"
---
```

Also save JSON companion: `{YYYYMMDD-HHMMSS}-council-{review_id}.json`

**No symlinks.** To find the latest artifact:
```bash
ls -t .outputs/council/ | head -1
```

**QMD Integration (optional):**
```bash
qmd collection add .outputs/council/ --name "council-reports" --mask "**/*.md" 2>/dev/null || true
qmd update 2>/dev/null || true
```

---

## Fallback Mode

If invoked with `--fallback-mode` (e.g., from deep-verify as a second pass):

- Use only bridge-claude (always available)
- Apply debate-protocol logic with single-bridge findings
- Mark report `"fallback": true`
- Merge findings with calling skill's existing report

---

## Notes

- **No Skill-within-Skill**: Bridges are read via Read tool and embedded in Task prompts — NOT called via Skill tool
- **Minimum threshold**: At least one bridge must return COMPLETED; zero completions emits ABORTED
- **SKIPPED/HALTED bridges don't block**: Council proceeds and notes what was skipped or halted
- **Transparent attribution**: Every finding carries its source bridge(s)
- **Intensity propagates**: The intensity setting flows to all bridges and their sub-agents
