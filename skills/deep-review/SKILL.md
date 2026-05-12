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

## Step 4: Detect Re-Review Inputs and Select Mode

Before invoking `agent-council`, check whether this is a **re-review** or a **fresh review**. The user (or upstream skill) may have supplied any of:

- `fixes_applied` — a diff/description of changes since the prior review
- `prior_findings` — the previous council's findings
- `prior_session_id` — id of the prior `agent-council` artifact (findings can be loaded from it)
- `original_proposal` — design/intent the work is supposed to uphold

Or the user prompt may say "re-review my fixes," "after fixes," "check my fixes for the prior findings," etc. — these are re-review triggers.

| Detected inputs | Mode |
|----------------|------|
| Fresh review (no prior findings/fixes mentioned) | `mode: review` |
| Any of: `fixes_applied`, `prior_findings`, `prior_session_id` | `mode: finding-driven` |

If you detected re-review intent but the user didn't pass explicit prior findings → run preflight to ask: "I see this is a re-review. Where are the prior findings? (a) point me to the prior `agent-council` artifact, (b) paste them, (c) treat this as a fresh review instead."

---

## Step 5: Invoke agent-council

```
Skill("agent-council")
```

**For a fresh review** (default):

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

**For a re-review** (mode = finding-driven):

```yaml
agent_council_input:
  scope: "{working_scope.artifact}"
  task_type: "review"
  mode: "finding-driven"
  tier: <from Step 3 — multi-fix re-reviews often warrant Tier 2>
  domains: "{working_scope.domains}"
  context_summary: "{working_scope.context_summary}"
  intensity: "{working_scope.intensity}"
  framing: "constructive improvement feedback"
  findings: "{prior_findings — see runtime-contracts Finding Object Schema}"
  fixes_applied: "{the diff or description of fixes}"
  original_proposal: "{if available, the design/spec being upheld}"
  prior_session_id: "{if available}"
```

The `framing: constructive improvement feedback` cue tells domain experts to produce remediation-oriented findings rather than pass/fail audit-style findings — that's the only difference from raw `agent-council` invocation. In finding-driven mode, this framing also applies to regression and design-drift findings.

---

## Step 6: Receive & Save

`agent-council` returns a council report conforming to `runtime-contracts`. Save under `.outputs/review/{YYYYMMDD-HHMMSS}-deep-review-{session_id}.md` with frontmatter:

```yaml
---
skill: deep-review
agent_council_tier: 1 | 2 | 3
agent_council_mode: review | finding-driven
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
- **Re-review routing**: When the user is re-reviewing fixes against a prior council's findings, this skill forwards to `agent-council` in `mode: finding-driven` automatically. See council-taxonomy Anti-Pattern 8 for why naive re-review (just running fresh `mode: review` again) misses regression, design drift, and fix-interaction issues.
- For audit-style pass/fail compliance work, use `deep-audit` instead. For spec-verification, use `deep-verify`. For research, use `deep-research`.
