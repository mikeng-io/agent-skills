# Guardian Pre-Flight Pattern: Hookless Runtimes

For runtimes without a native hook system (Codex, Gemini CLI, or any future
runtime), Guardian checks run inline in the orchestrating skill before dispatch.
The skill calls `guardian.py` via Bash at the start of execution.

---

## Pattern

Instead of wiring a hook that fires automatically, the skill instructs the
agent to run the check manually at a defined step:

```markdown
## Step N: Guardian Pre-Flight

Run the following Guardian checks before dispatching to any runtime adapter:

1. **Preflight** — verify required inputs:
   ```bash
   python3 skills/guardian/guardian.py check-preflight agent-council \
     --mode {mode} \
     --task-type {task_type} \
     --scope-set {true|false} \
     --findings-count {len(findings) if findings else 0}
   ```
   If exit code is 2 → stop. Report the BLOCK message to the user. Do not proceed.

2. **Session ID uniqueness**:
   ```bash
   python3 skills/guardian/guardian.py check-session-id {session_id}
   ```
   If exit code is 2 → generate a new session_id and retry once.
```

The skill MUST call these checks. Guardian cannot enforce this automatically
on runtimes without hooks — the responsibility shifts to the skill author.

---

## Why this still matters without hooks

On hookless runtimes (Codex, Gemini), the agent can still skip the preflight call.
The pattern works because:

1. **Skill instructions are read before execution.** If the skill mandates the check,
   the agent reads that mandate before doing anything else.
2. **Failure is explicit.** A non-zero exit from `guardian.py` is a clear signal —
   not a subtle invariant violation buried in output.
3. **Auditability.** Even if enforcement is advisory, the Bash command appears in
   the conversation log, making it visible whether the check ran.

For runtimes with hooks (Claude Code, OpenCode, Kimi), the same `guardian.py`
binary is called — the only difference is who calls it (hook adapter vs. the agent).

---

## Embedding in agent-council (example)

In `skills/agent-council/SKILL.md`, Step 1 should include:

```markdown
## Step 1: Guardian Pre-Flight (if guardian installed)

Check for `.guardian/guardian.py` in the project root. If found:

```bash
# Preflight
python3 .guardian/guardian.py check-preflight agent-council \
  --scope-set {true if scope else false} \
  --task-type {task_type} \
  --mode {mode} \
  --findings-count {len(findings) if mode == "finding-driven" else 0}
```

If exit 2 → stop and surface the BLOCK message. Do not proceed to domain dispatch.

```bash
# Session ID uniqueness
python3 .guardian/guardian.py check-session-id {session_id}
```

If exit 2 → generate a new session_id.

If `.guardian/guardian.py` is NOT found → skip (Guardian is optional).
```

---

## Runtimes and enforcement model

| Runtime | Hook system | Enforcement model |
|---------|------------|------------------|
| Claude Code | Yes (PreToolUse) | Automatic — agent cannot bypass |
| OpenCode | Yes (similar) | Automatic — agent cannot bypass |
| Kimi Code | Yes (similar) | Automatic — agent cannot bypass |
| Codex CLI | No | Pre-flight only — advisory, agent must call it |
| Gemini CLI | No | Pre-flight only — advisory, agent must call it |
| Any new runtime | Unknown | Add adapter if hooks exist; else use pre-flight pattern |
