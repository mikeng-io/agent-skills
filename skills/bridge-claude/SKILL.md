---
name: bridge-claude
description: Reference adapter for Claude (Anthropic) dispatch. Read by any orchestrating skill via the Read tool. Defines how to invoke Claude sub-agents or the Anthropic API, with availability checks. Usable by any AI orchestrator — Claude Code, OpenCode, Codex, Gemini, or custom agents.
location: managed
context: reference
---

# Bridge: Claude (Anthropic) Adapter

This file is a REFERENCE DOCUMENT. Any orchestrating skill reads it via the `Read` tool and embeds its instructions directly into Task agent prompts. It is not invoked as a standalone skill — it is a reusable set of instructions for Anthropic model dispatch.

## Bridge Identity

```yaml
bridge: claude
model_family: anthropic/claude
availability: conditional   # Depends on executor — not always available
connection_preference:
  1: native-dispatch  # Executor is Claude Code — Task tool / Agent Teams
  2: cli       # Any other executor — invoke `claude -p` CLI
  3: api              # Last resort — Anthropic HTTP API via ANTHROPIC_API_KEY
  4: skip             # None available — return SKIPPED (non-blocking)
```

---

## Step 1: Pre-Flight — Connection Detection

### Check A: Task Tool Available?

If the executor is Claude Code (or any agent with native Task tool access), this is the preferred path. No external process needed.

If Task tool available → **use Task/Agent Teams path** (Steps 3A + 3B).

---

### Check B: Claude Code CLI Installed?

```bash
which claude
```

If found → **use Claude Code CLI path** (Step 3C). Any external executor (OpenCode, Codex, Gemini, custom agents) can invoke `claude -p` to get Claude's analysis without API keys.

---

### Check C: Anthropic API Accessible?

```bash
echo ${ANTHROPIC_API_KEY:+found}
```

If `ANTHROPIC_API_KEY` is set → **use API path** (Step 3D).

---

### Neither available → SKIPPED

```json
{
  "bridge": "claude",
  "status": "SKIPPED",
  "skip_reason": "No Anthropic access — Task tool unavailable, claude CLI not found, ANTHROPIC_API_KEY not set",
  "outputs": []
}
```

Claude bridge is non-blocking when unavailable. SKIPPED is a valid outcome.

---

## Step 2: Input Format

```json
{
  "bridge_input": {
    "session_id": "...",
    "scope": "Files and/or description of what to work on",
    "task_description": "What the agent should do (review, plan, implement, analyze, research, etc.)",
    "domains": ["domain1", "domain2"],
    "context_summary": "What the conversation/task is about",
    "intensity": "quick | standard | thorough",
    "task_type": "review | planning | implementation | analysis | research"
  }
}
```

`task_type` informs how agents frame their output — findings for review, plans for planning, designs for implementation.

---

## Step 3: Select Dispatch Mode

Claude bridge has two dispatch modes. Select based on task complexity and environment:

```yaml
dispatch_mode:
  agent_teams:
    condition: "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 AND (domains >= 3 OR intensity = thorough)"
    description: "Teammates share a task list and communicate directly — best for complex multi-domain work"
    preferred: true

  task_tool:
    condition: "Default — always available as fallback"
    description: "Sub-agents report results to parent — best for focused, independent tasks"
    preferred: false
```

**Agent Teams vs Task Tool:**

| | Task Tool | Agent Teams |
|---|-----------|------------|
| Communication | Sub-agents report to parent only | Teammates message each other directly |
| Coordination | Parent manages all | Shared task list, self-coordinating |
| Best for | Quick focused tasks | Multi-domain debate, complex analysis |
| Availability | Always | Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |

---

## Step 3: Build Agent Task

Construct the task prompt from `bridge_input`. Adapt framing to `task_type`:

```
You are a {expert_role} working on the following:

SCOPE: {scope}
TASK: {task_description}
CONTEXT: {context_summary}
INTENSITY: {intensity}

DOMAINS: {domains}

{domain-specific focus areas from domain-registry}

Produce your output as JSON:
{
  "agent": "{expert_role}",
  "domain": "{domain}",
  "bridge": "claude",
  "outputs": [
    {
      "id": "",
      "type": "finding | recommendation | plan-item | implementation-note | observation",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "Short title",
      "description": "Detailed description",
      "evidence": "Specific reference",
      "action": "Recommended action"
    }
  ],
  "summary": "Brief summary of output",
  "confidence": "high | medium | low"
}
```

---

## Step 3A: Execute via Agent Teams (preferred for complex tasks)

When `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is set and task complexity warrants it (3+ domains or thorough intensity), use Agent Teams. Teammates share a task list and can message each other directly — enabling real-time debate between domain experts.

```
1. TeamCreate → create "bridge-claude-{session_id}" team
2. Spawn teammates:
   - One per domain from bridge_input.domains
   - Devil's Advocate (always)
   - Integration Checker (always)
3. Create tasks in shared task list — one per teammate
4. Teammates self-coordinate: domain experts complete their analysis,
   Devil's Advocate challenges findings via direct messages,
   Integration Checker surfaces cross-component issues
5. Wait for all tasks complete
6. Synthesize via TaskList
7. TeamDelete → clean up
```

Teammates communicate findings and challenges directly without routing through the parent.

### Teammate prompts

**Domain expert:**
```
You are a {expert_role}. Your task: {task_description}
Scope: {scope} | Context: {context_summary} | Intensity: {intensity}
Focus: {focus_areas from domain-registry}
Output format: the outputs JSON structure defined in bridge_input.
```

**Devil's Advocate:**
```
You are a Devil's Advocate. Challenge assumptions and find failure modes.
Scope: {scope} | Context: {context_summary}
Message domain expert teammates to challenge their findings directly.
Focus: pre-mortem failure modes, incorrect assumptions, edge cases, cross-domain risks.
Output format: same outputs JSON (domain: "cross-domain")
```

**Integration Checker:**
```
You are an Integration Checker. Find cross-component issues.
Scope: {scope} | Context: {context_summary}
Focus: interface mismatches, undocumented contracts, error propagation gaps, timing dependencies.
Output format: same outputs JSON (domain: "integration")
```

---

## Step 3B: Execute via Task Tool (fallback)

When Agent Teams is not available, spawn parallel Task sub-agents — one per domain + Devil's Advocate + Integration Checker. Sub-agents report results to parent only (no direct inter-agent communication).

```
Task 1: {domain_1} expert — focus: {focus_areas}, scope: {scope}
Task 2: {domain_2} expert — focus: {focus_areas}, scope: {scope}
...
Task N: Devil's Advocate — challenge assumptions, find failure modes
Task N+1: Integration Checker — cross-component impacts, implicit contracts
```

Use the same prompt templates as Agent Teams mode. All tasks run in parallel. Wait for all to complete.

---

## Step 3C: Execute via Claude Code CLI (external executors)

When any non-Claude-Code executor can call the `claude` CLI:

```bash
timeout {final_timeout} claude -p "{constructed_prompt}" \
  --output-format json \
  --allowedTools "Read,Grep,Glob,Bash(ls *)"
```

**Key flags:**

| Flag | Purpose |
|------|---------|
| `-p "prompt"` | Prompt string — non-interactive mode |
| `--output-format json` | Structured JSON output for parsing |
| `--output-format stream-json` | Streaming JSON for real-time processing |
| `--allowedTools` | Restrict what Claude can do (scope to read-only for analysis) |
| `--continue` | Resume the most recent session |

For read-only analysis, scope tools to `Read,Grep,Glob,Bash(ls *)`. For implementation tasks, use the full tool set.

See `cli-reference.md` for complete flag reference.

---

## Step 3D: Execute via Anthropic API (last resort for any executor)

When the orchestrator is not Claude Code (no Task tool access), fall back to direct API:

```bash
# Discover latest model first — do not hardcode
CLAUDE_MODEL=$(curl -s -H "x-api-key: $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/models | python3 -c \
  "import sys,json; models=json.load(sys.stdin)['data']; print(models[0]['id'])")

curl -s -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$CLAUDE_MODEL\",
    \"max_tokens\": 8096,
    \"messages\": [{\"role\": \"user\", \"content\": \"{constructed_prompt}\"}]
  }"
```

Single API call covers all domains in one prompt. Less parallelism than Task/Teams paths.

---

## Step 4: Collect and Aggregate

After all agents complete (Task path) or API responds:

1. Assign unique output IDs (`C001`, `C002`, ...)
2. Deduplicate near-identical outputs (keep highest severity)
3. Calculate overall verdict (if task_type is review or analysis)

### Verdict Logic (review/analysis only)

```yaml
FAIL:     Any CRITICAL output
CONCERNS: 1+ HIGH outputs, or 3+ MEDIUM outputs
PASS:     No CRITICAL/HIGH, only MEDIUM/LOW/INFO
```

For other task types (`planning`, `implementation`, `research`), verdict is `null`.

---

## Output Format

```json
{
  "bridge": "claude",
  "model_family": "anthropic/claude",
  "connection_used": "native-dispatch | cli | api",
  "session_id": "...",
  "status": "COMPLETED | SKIPPED",
  "skip_reason": "...",
  "task_type": "review | planning | implementation | analysis | research",
  "domains_covered": ["domain1", "domain2", "cross-domain", "integration"],
  "outputs": [
    {
      "id": "C001",
      "type": "finding | recommendation | plan-item | implementation-note | observation",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "...",
      "description": "...",
      "evidence": "...",
      "action": "...",
      "domain": "...",
      "agent": "..."
    }
  ],
  "verdict": "PASS | FAIL | CONCERNS | null",
  "agents_spawned": 4,
  "confidence": "high | medium | low"
}
```

---

## Notes

- **Not always available** — check Task tool access or `ANTHROPIC_API_KEY` before using
- **SKIPPED is non-blocking** — if unavailable, other bridges continue
- **Task tool path is preferred** — richer parallel dispatch when running in Claude Code
- **API path works from any executor** — fallback for non-Claude orchestrators
- **Task type drives framing** — the same bridge handles review, planning, research, etc.
