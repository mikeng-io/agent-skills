---
name: bridge-claude
description: Reference adapter for Claude (Anthropic) dispatch. Read by any orchestrating skill via the Read tool. Defines how to invoke Claude sub-agents or the Anthropic API, with availability checks. Usable by any AI orchestrator — Claude Code, OpenCode, Codex, Gemini, or custom agents.
location: managed
context: reference
---

# Bridge: Claude (Anthropic) Adapter

This file is a REFERENCE DOCUMENT. Any orchestrating skill reads it via the `Read` tool and embeds its instructions directly into Task agent prompts. It is not invoked as a standalone skill — it is a reusable set of instructions for Anthropic model dispatch.

**Input schema, agent prompt template, output schema, verdict logic, timeout formula, artifact format, and status semantics are defined in `bridge-commons/SKILL.md`. This file covers only Claude-specific connection detection and execution paths.**

## Bridge Identity

```yaml
bridge: claude
model_family: anthropic/claude
availability: conditional   # Depends on executor — not always available
connection_preference:
  1: native-dispatch  # Executor is Claude Code — Task tool / Agent Teams
  2: cli              # Any other executor — invoke `claude -p` CLI
  3: api              # Last resort — Anthropic HTTP API via ANTHROPIC_API_KEY
  4: skip             # None available — return SKIPPED (non-blocking)
```

---

## Step 1: Pre-Flight — Connection Detection

### Check A: Task Tool Available?

If the executor is Claude Code (or any agent with native Task tool access), this is the preferred path. No external process needed.

If Task tool available → **use native-dispatch path** (Steps 3A + 3B).

---

### Check B: Claude Code CLI Installed?

```bash
which claude
```

If found → **use CLI path** (Step 3C). Any external executor (OpenCode, Codex, Gemini, custom agents) can invoke `claude -p` to get Claude's analysis without API keys.

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

## Step 2: Select Dispatch Mode

Claude bridge has two native-dispatch modes. Select based on task complexity and environment:

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

Teammates communicate findings and challenges directly without routing through the parent. This replaces the bridge-commons consolidation pass — debate-protocol provides a richer version.

### Teammate prompts

**Domain expert:**
```
You are a {expert_role}. Your task: {task_description}
Scope: {scope} | Context: {context_summary} | Intensity: {intensity}
Focus: {focus_areas from domain-registry}
Return your output as the JSON structure defined in bridge-commons Agent Prompt Template.
```

**Devil's Advocate:**
```
You are a Devil's Advocate. Challenge assumptions and find failure modes.
Scope: {scope} | Context: {context_summary}
Message domain expert teammates to challenge their findings directly.
Focus: pre-mortem failure modes, incorrect assumptions, edge cases, cross-domain risks.
Return outputs JSON with domain: "cross-domain".
```

**Integration Checker:**
```
You are an Integration Checker. Find cross-component issues.
Scope: {scope} | Context: {context_summary}
Focus: interface mismatches, undocumented contracts, error propagation gaps, timing dependencies.
Return outputs JSON with domain: "integration".
```

---

## Step 3B: Execute via Task Tool (fallback)

When Agent Teams is not available, spawn parallel Task sub-agents — one per domain + Devil's Advocate + Integration Checker. Sub-agents report results to parent only (no direct inter-agent communication). Build prompts using the Agent Prompt Template from bridge-commons.

```
Task 1: {domain_1} expert — focus: {focus_areas}, scope: {scope}
Task 2: {domain_2} expert — focus: {focus_areas}, scope: {scope}
...
Task N:   Devil's Advocate — challenge assumptions, find failure modes (domain: "cross-domain")
Task N+1: Integration Checker — cross-component impacts, implicit contracts (domain: "integration")
```

All tasks run in parallel. After all complete, run the bridge-commons Post-Analysis Protocol. For subsequent rounds, spawn new Task sub-agents with the context packet embedded in their prompts — the parent agent holds all state between rounds and manages the orchestrator synthesis step.

---

## Step 3C: Execute via CLI (external executors)

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
| `--allowedTools` | Restrict what Claude can do (read-only for analysis) |
| `--continue` | Resume the most recent session |

For read-only analysis, scope tools to `Read,Grep,Glob,Bash(ls *)`. For implementation tasks, use the full tool set.

---

## Step 3D: Execute via Anthropic API (last resort)

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

Single API call covers all domains in one prompt. Less parallelism than native-dispatch paths.

---

## Output

See bridge-commons Output Schema. Bridge-specific fields:

```json
{
  "bridge": "claude",
  "model_family": "anthropic/claude",
  "connection_used": "native-dispatch | cli | api",
  "agents_spawned": 4
}
```

Output ID prefix: `C` (e.g., `C001`, `C002`).

---

## Notes

- **Not always available** — check Task tool access or `ANTHROPIC_API_KEY` before using
- **SKIPPED is non-blocking** — if unavailable, other bridges continue
- **native-dispatch is preferred** — richer parallel dispatch when running in Claude Code
- **Agent Teams replaces consolidation pass** — when available, debate-protocol runs instead
- **API path works from any executor** — fallback for non-Claude orchestrators
- **Task type drives framing** — the same bridge handles review, planning, research, etc.
