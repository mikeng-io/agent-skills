---
name: deep-review
description: Multi-agent quality improvement review with constructive feedback. Thin entry point over agent-council — sets task_type=review and defaults to Tier 1, escalating to Tier 2/3 when domain count or stakes warrant.
location: managed
dependencies:
  - council-taxonomy
  - context
  - preflight
  - agent-council
  - domain-registry
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(ls *)
  - Bash(mkdir *)
  - Skill
  - Write
---

# Deep Review

Constructive quality review across one or more domains. **This skill is a thin entry point over `agent-council`.** It exists to provide a named invocation for review work; all execution machinery lives in `agent-council`.

---

## Step 0: Read council-taxonomy (MANDATORY)

```
Read: [skills-root]/council-taxonomy/SKILL.md
```

This skill assumes the tier model and vocabulary defined in the taxonomy. If you skip it, you will produce an artifact downstream consumers cannot interpret.

---

## Step 1: Dependency Check

```
[skills-root]/council-taxonomy/SKILL.md
[skills-root]/context/SKILL.md
[skills-root]/preflight/SKILL.md
[skills-root]/agent-council/SKILL.md
[skills-root]/domain-registry/README.md
```

If any are missing → stop and emit install advisory.

---

## Step 2: Scope & Context

Invoke `context` (always) and `preflight` (only when context confidence is `low` or `missing_signals` is non-empty). Build `working_scope`.

---

## Step 3: Tier Selection (review-specific defaults)

| Condition | Tier |
|-----------|------|
| `domains_count <= 5`, no high-stakes signals, routine code/copy review | 1 |
| `domains_count > 5` OR explicit "thorough" request OR cross-runtime verification desired | 2 |
| `domains_count >= 9` OR irreversible decision OR security/compliance dimension surfaces | 3 |

Default for `deep-review` is **Tier 1**. If the user explicitly asks for "deep" or "multi-model" review, escalate to Tier 2 or 3.

---

## Step 4: Invoke agent-council

```
Skill("agent-council")
```

With inputs:

```yaml
agent_council_input:
  scope: "{working_scope.artifact}"
  task_type: "review"
  mode: "review"
  tier: <from Step 3>
  domains: "{working_scope.domains}"
  context_summary: "{working_scope.context_summary}"
  intensity: "{working_scope.intensity}"
  framing: "constructive improvement feedback"
```

The `framing: constructive improvement feedback` cue tells domain experts to produce remediation-oriented findings rather than pass/fail audit-style findings — that's the only difference from raw `agent-council` invocation.

---

## Step 5: Receive & Save

`agent-council` returns a council report conforming to `runtime-contracts`. Save under `.outputs/review/{YYYYMMDD-HHMMSS}-deep-review-{session_id}.md` with frontmatter:

```yaml
---
skill: deep-review
agent_council_tier: 1 | 2 | 3
session_id: "{session_id}"
timestamp: "{ISO-8601}"
verdict: PASS | FAIL | CONCERNS
domains: []
context_summary: ""
---
```

Body = the council report.

---

## Notes

- All execution machinery (domain dispatch, debate, runtime adapters at Tier 2+) lives in `agent-council`. Do not duplicate it here.
- The default tier is intentionally **Tier 1**. Most code reviews don't need runtime diversity. Trust the tier-up rule in `agent-council` to escalate when warranted.
- For audit-style pass/fail compliance work, use `deep-audit` instead. For spec-verification, use `deep-verify`. For research, use `deep-research`.
