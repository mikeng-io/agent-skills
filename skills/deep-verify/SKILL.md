---
name: deep-verify
description: Multi-agent specification verification with balanced expert analysis. Thin entry point over agent-council — verifies work against an attached spec or requirements document, defaults to Tier 2 for independent verification, escalates to Tier 3 for critical specs.
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

# Deep Verify

Verify work against an attached specification or requirements document. **This skill is a thin entry point over `agent-council`.** It exists because spec-verification has different framing from review/audit: experts compare the artifact against the spec, not against general standards.

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

## Step 2: Scope & Spec Resolution

Invoke `context` (always) and `preflight` (only when context confidence is `low` or `missing_signals` is non-empty).

**Verify-specific:** Two artifacts are needed —

1. **The artifact under verification** (the implementation, deliverable, or output)
2. **The specification** (requirements doc, design doc, acceptance criteria, contract)

If either is missing, preflight must ask. Verification without an explicit spec is just review.

Build `working_scope`:

```yaml
working_scope:
  artifact: ""             # what to verify
  spec_path: ""            # path or content of the spec document
  intent: "verify"
  domains: []
  context_summary: ""
  intensity: "standard"
```

---

## Step 3: Tier Selection (verify-specific defaults)

| Condition | Tier |
|-----------|------|
| Routine spec compliance check, simple deliverable | 1 |
| Multi-component implementation vs spec, mixed domains | 2 (default) |
| Critical spec (API contract, security spec, financial spec, regulatory binding) | 3 |

Default for `deep-verify` is **Tier 2** because spec-verification benefits from independent runtime perspectives — different runtimes may interpret the spec differently, surfacing ambiguities. Tier 3 when the cost of a false PASS is unacceptable.

---

## Step 4: Invoke agent-council

```
Skill("agent-council")
```

With inputs:

```yaml
agent_council_input:
  scope: "{working_scope.artifact}"
  task_type: "audit"
  mode: "review"
  tier: <from Step 3>
  domains: "{working_scope.domains}"
  context_summary: "{working_scope.context_summary}"
  intensity: "{working_scope.intensity}"
  requirements: "{working_scope.spec_path}"
  framing: |
    Verify the artifact against the attached specification.
    For each spec requirement, produce one of:
    - met (INFO)
    - partially met (MEDIUM gap)
    - unmet (HIGH gap — or CRITICAL if it's a MUST-have)
    - ambiguous in spec (LOW — flag for spec author)
    Findings should reference specific spec sections.
```

---

## Step 5: Receive & Save

Save under `.outputs/verification/{YYYYMMDD-HHMMSS}-deep-verify-{session_id}.md` with frontmatter:

```yaml
---
skill: deep-verify
agent_council_tier: 1 | 2 | 3
session_id: "{session_id}"
timestamp: "{ISO-8601}"
verdict: PASS | FAIL | CONCERNS
artifact: ""
spec_path: ""
domains: []
context_summary: ""
---
```

The verdict reflects spec compliance: PASS = all requirements met or only LOW/INFO gaps; CONCERNS = some HIGH/MEDIUM gaps; FAIL = unmet MUST-haves.

---

## Notes

- All execution machinery lives in `agent-council`. Do not duplicate it here.
- **The spec must be attached.** Verification without an explicit spec is review — use `deep-review` instead.
- Default tier is **Tier 2** because spec interpretation benefits from runtime diversity; one runtime may catch ambiguity another missed.
- For compliance audits against standards (rather than against a specific spec), use `deep-audit`.
- Findings should reference spec sections (e.g., "§3.2.1 unmet — auth endpoint missing rate limiting").
