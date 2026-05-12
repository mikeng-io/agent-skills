---
name: deep-audit
description: Multi-agent standards and compliance auditing with pass/fail verdicts. Thin entry point over agent-council — sets task_type=audit and defaults to Tier 2 (compliance benefits from runtime diversity), escalating to Tier 3 for security/regulatory work.
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

# Deep Audit

Compliance and standards audit with pass/fail verdicts. **This skill is a thin entry point over `agent-council`.** All execution machinery lives in `agent-council`.

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

**Audit-specific scope:** The audit needs an explicit `requirements` field — the standards, regulations, or compliance checklist to audit against. Preflight should ask for this if not in the original prompt.

---

## Step 3: Tier Selection (audit-specific defaults)

| Condition | Tier |
|-----------|------|
| Internal code-style audit, no regulatory dimension | 1 |
| Standards audit (accessibility, performance) OR mixed-domain audit | 2 (default) |
| Security audit, regulatory compliance (GDPR/SOC2/HIPAA/PCI), cryptographic review | 3 |

Default for `deep-audit` is **Tier 2** because compliance work benefits from runtime/toolchain diversity (one runtime might miss a compliance gap another catches). Tier 3 for high-stakes regulatory work where shared-bias detection is essential.

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
  mode: "audit"
  tier: <from Step 3>
  domains: "{working_scope.domains}"
  context_summary: "{working_scope.context_summary}"
  intensity: "{working_scope.intensity}"
  requirements: "{working_scope.requirements}"  # standards / regulations to audit against
  framing: "compliance-calibrated: unmet MUST → HIGH, unmet SHOULD → MEDIUM, met → INFO"
```

The audit verdict logic in `agent-council` is compliance-calibrated per `runtime-contracts`:
- `FAIL` — any CRITICAL, or ≥2 HIGH compliance-gaps
- `CONCERNS` — 1 HIGH compliance-gap, or ≥3 MEDIUM gaps
- `PASS` — all requirements met or only LOW/INFO gaps

---

## Step 5: Receive & Save

Save under `.outputs/audit/{YYYYMMDD-HHMMSS}-deep-audit-{session_id}.md` with frontmatter:

```yaml
---
skill: deep-audit
agent_council_tier: 1 | 2 | 3
session_id: "{session_id}"
timestamp: "{ISO-8601}"
verdict: PASS | FAIL | CONCERNS
domains: []
requirements_audited: []
context_summary: ""
---
```

---

## Notes

- All execution machinery lives in `agent-council`. Do not duplicate it here.
- Default tier is **Tier 2** because audit work benefits from runtime diversity to catch compliance gaps a single runtime might miss.
- For regulatory/security audits, escalate to Tier 3. The cost of a false PASS in those domains is unacceptable.
- For improvement-feedback reviews (no pass/fail), use `deep-review` instead.
