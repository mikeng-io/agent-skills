---
name: deep-research
description: Multi-domain research framework with evidence-backed observations and contradictions. Thin entry point over agent-council — sets task_type=research, mode=research, and defaults to Tier 2 for multi-source perspective diversity.
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

# Deep Research

Multi-domain research with evidence-backed observations, contradictions, and confidence-scored synthesis. **This skill is a thin entry point over `agent-council`.** Research mode produces observations and hypotheses, not findings with severity — verdict is null.

---

## Step 0: Read council-taxonomy (MANDATORY)

```
Read: [skills-root]/council-taxonomy/SKILL.md
```

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

**Research-specific scope:** A research session needs a research question, not just an artifact. Preflight should ask for the explicit question (e.g., "what tradeoffs exist between approach A and B?", "what evidence supports claim X?") if not in the original prompt.

---

## Step 3: Tier Selection (research-specific defaults)

| Condition | Tier |
|-----------|------|
| Quick single-domain literature check | 1 |
| Multi-domain research, cross-perspective synthesis | 2 (default) |
| Foundational decision research, high-stakes hypothesis testing, irreversible commitment | 3 |

Default for `deep-research` is **Tier 2** because research benefits from runtime diversity — different runtimes pull from different evidence channels, surface different sources, and frame questions differently. Tier 3 when the research output will drive a major decision.

---

## Step 4: Invoke agent-council

```
Skill("agent-council")
```

With inputs:

```yaml
agent_council_input:
  scope: "{working_scope.artifact}"
  research_question: "{working_scope.research_question}"
  task_type: "research"
  mode: "research"
  tier: <from Step 3>
  domains: "{working_scope.domains}"
  context_summary: "{working_scope.context_summary}"
  intensity: "{working_scope.intensity}"
  framing: |
    Produce evidence-backed observations, not findings with severity.
    Each observation must include:
    - claim (what is being asserted)
    - evidence (specific source, citation, or measurement)
    - confidence (high | medium | low)
    - contradictions (other observations or sources that disagree)
    Verdict is null — research does not pass/fail.
```

Research mode in `agent-council` uses the observations output schema from `runtime-contracts`, not the findings schema.

---

## Step 5: Receive & Save

Save under `.outputs/research/{YYYYMMDD-HHMMSS}-deep-research-{session_id}.md` with frontmatter:

```yaml
---
skill: deep-research
agent_council_tier: 1 | 2 | 3
session_id: "{session_id}"
timestamp: "{ISO-8601}"
verdict: null
research_question: ""
domains: []
observations_count: 0
contradictions_count: 0
context_summary: ""
---
```

Body includes the observations array, contradictions matrix, and confidence-scored synthesis.

---

## Notes

- All execution machinery lives in `agent-council`. Do not duplicate it here.
- Research mode produces **observations**, not findings. No severity, no verdict.
- Default tier is **Tier 2** because different runtimes pull from different evidence channels (web search, docs, code, browser).
- Contradictions are explicitly surfaced — research that suppresses disagreement is broken research.
- For decisions that need pass/fail verdicts, use `deep-audit` or `deep-review` instead.
