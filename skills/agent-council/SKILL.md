---
name: agent-council
description: Unified multi-agent council skill. Takes a tier parameter (0/1/2/3) that scales from a single review through in-runtime sub-agent dispatch up to cross-runtime council with debate. Replaces the historical separate skills "agent-council", "runtime-council", and "deep-council" — all are tiers of the same operation. Supports review, audit, research, and brainstorm/design modes.
location: managed
dependencies:
  - council-taxonomy
  - context
  - preflight
  - domain-registry
  - runtime-contracts
  - runtime-claude
  - runtime-codex
  - runtime-gemini
  - runtime-opencode
  - runtime-kimi
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

# Agent Council: Unified Tier-Parameterized Council

Execute this skill to run a multi-agent review at any scale, from a single agent up to a cross-runtime council with debate. **The tier parameter selects the scale.** Do not invoke separate council skills — there is only one.

## Step 0: Read council-taxonomy (MANDATORY)

Before doing anything else, read the vocabulary:

```
Read: [skills-root]/council-taxonomy/SKILL.md
```

`council-taxonomy` is this suite's authoritative glossary — tier model, runtime vocabulary, diversity dimensions, and anti-patterns. Every step below assumes that vocabulary. If you skip it, you will produce confused artifacts that downstream agents cannot interpret.

`[skills-root]` is the parent of this skill's directory — resolve with `ls ../` from this skill's location.

---

## Step 1: Dependency Check

Verify required skills are present:

```
[skills-root]/council-taxonomy/SKILL.md
[skills-root]/context/SKILL.md
[skills-root]/preflight/SKILL.md
[skills-root]/domain-registry/README.md
[skills-root]/runtime-contracts/SKILL.md
```

For Tier 2+ dispatch, also verify runtime adapters:

```
[skills-root]/runtime-claude/SKILL.md
[skills-root]/runtime-codex/SKILL.md
[skills-root]/runtime-gemini/SKILL.md
[skills-root]/runtime-opencode/SKILL.md
[skills-root]/runtime-kimi/SKILL.md
```

If a *required* file is missing → stop and emit an install advisory.
If only some *runtime adapters* are missing → log which are unavailable; Tier 2+ will dispatch only the ones present.

---

## Step 2: Resolve Scope & Context

**Always invoke `context`:**

```
Skill("context")
```

`context` classifies the artifact, detects domains from `domain-registry`, and assesses confidence.

**Conditionally invoke `preflight`** when context confidence is `low` OR `missing_signals` is non-empty. Preflight asks at most 3 targeted questions to fill exactly the gaps `context` could not resolve.

Merge into `working_scope`:

```yaml
working_scope:
  artifact: ""           # what to analyze
  intent: ""             # review | audit | verify | research | implement | analysis | planning
  domains: []            # from context (authoritative), supplemented by preflight
  constraints: []        # from preflight (empty if skipped)
  context_summary: ""    # combined description for agent prompts
  intensity: "standard"  # quick | standard | thorough — from routing signals + user request
```

---

## Step 3: Select Tier

The `tier` parameter determines the council's scale and dispatch mechanism.

### Inputs to tier selection

1. **Explicit user input** — if the invocation specified `tier: N`, use it.
2. **Derived from working_scope** if unspecified:

| Signal | Suggested tier |
|--------|---------------|
| `domains_count == 1` AND trivial scope AND no integration concerns | 0 |
| `domains_count <= 5` AND no high-stakes signals AND `intensity != thorough` | 1 |
| `domains_count > 5` OR explicit cross-runtime / multi-model request OR `intensity == thorough` AND domain count moderate | 2 |
| `domains_count >= 9` OR security/compliance signal OR explicit "deep" / "highest confidence" request OR irreversible decision | 3 |

High-stakes signals (from the user prompt or scope): `critical`, `security`, `compliance`, `production`, `cryptographic`, `financial`, `audit`, `irreversible`.

### Tier-up rule (post-dispatch escalation)

If a Tier 1 council completes with:
- 3+ `disputed` findings, OR
- aggregate confidence `low`, OR
- a domain expert explicitly flagged "needs cross-runtime verification"

→ Re-dispatch at Tier 2 (or Tier 3 for high-stakes). Record the escalation in the final artifact's `tier_history` field. Do not silently swallow the lower-tier output — include it as `prior_tier_report` for transparency.

### Tier-down rule (don't inflate)

Do not run Tier 3 for ≤2-domain routine reviews. Tier inflation wastes context and time. If in doubt, start at Tier 1 and let the tier-up rule escalate.

Record the selected tier in `council_context.tier`.

### Finding-driven mode: IC-tier asymmetry

When `mode == "finding-driven"` with `fixes_applied` containing ≥2 fixes, the **Integration Checker may run at a higher tier than the rest of the council**. Fix-interaction analysis (Check #4 in Finding-Driven Mode) is where runtime diversity helps most — one runtime sees the local fix; a different runtime is more likely to catch the cross-fix invariant break.

| Council intent | Council tier | IC tier |
|---------------|--------------|---------|
| Trivial fix re-review (1 fix, 1 domain) | 1 | 1 |
| Multi-fix re-review (≥2 fixes, may interact) | 1 | **2** |
| Critical-proposal multi-fix re-review | 2 | **3** |

Record both as `council_context.tier` and `council_context.ic_tier`. See **Finding-Driven Mode** below for details.

---

## Step 4: Populate Council Context

```yaml
council_context:
  tier: 0 | 1 | 2 | 3
  session_id: "council-{YYYYMMDD-HHmmss}"
  scope: ""                # from working_scope.artifact
  context_summary: ""      # from working_scope.context_summary
  task_type: ""            # review | audit | research | analysis | planning | implement
  mode: ""                 # review | audit | brainstorm | design | research | synthesis
  capability_profile: ""   # inspect | modify — derived from task_type via runtime-contracts
  domains: []              # from working_scope.domains
  intensity: ""            # quick | standard | thorough
  diversity_sources: []    # populated as dispatch proceeds (role/model/runtime/toolchain/debate-layer)
```

Read `runtime-contracts/SKILL.md` for the canonical capability profile mapping (e.g., `task_type: review` → `capability_profile: inspect`).

---

## Step 5: Domain Selection

Read domain definitions from `domain-registry`:

```
Read: [skills-root]/domain-registry/domains/technical.md
Read: [skills-root]/domain-registry/domains/business.md
Read: [skills-root]/domain-registry/domains/creative.md
```

For each domain in `working_scope.domains`, resolve:
- `expert_role` — domain-registry's named expert
- `focus_areas` — what the expert should focus on
- `standards` — what standards or references apply

These flow into every sub-agent / runtime adapter prompt. **Mode matters:** for `brainstorm` / `design` modes, frame prompts to produce proposals; for `review` / `audit`, frame for findings.

If no domain in the registry substantially covers a concern, synthesize a session-based virtual expert role rather than forcing a mismatched registry entry.

---

## Step 6: Tier Dispatch

This is the only step that branches on tier. All other steps are tier-agnostic.

### Tier 0: Single Review

Single agent, no diversity. Use only when the scope is trivial (1 domain, no integration concerns).

1. Spawn one Task agent with the domain expert's prompt (constructed using the Agent Prompt Template from `runtime-contracts`).
2. Wait for completion.
3. Skip debate (no DA, no IC).
4. Output conforms to `runtime-contracts` output schema; `debate_rounds: 0`; `diversity_sources: ["role"]`.

### Tier 1: Local Agent Council (in-runtime)

Multiple sub-agents within the current runtime — `Task` in Claude Code, `task` (lowercase) in OpenCode, `Agent` tool in Kimi, `delegate_task` in Hermes, etc.

**Roles dispatched in parallel:**

| Role | Count | Source |
|------|-------|--------|
| Domain Expert | One per domain in `council_context.domains` | `domain-registry` |
| Devil's Advocate | 1 | fixed role |
| Integration Checker | 1 | fixed role |

Total parallel agents = `len(domains) + 2`. If `domains > 5`, group related domains so the parallel agent count stays manageable.

**Dispatch protocol:**

1. Construct one prompt per role using the Agent Prompt Template from `runtime-contracts/SKILL.md`.
2. Spawn all agents in parallel using the runtime's native dispatch mechanism. Detect the mechanism by tool availability — see `runtime-contracts/tool-discovery.md`.
3. After all complete, run the Post-Analysis Protocol from `runtime-contracts`:
   - `intensity: quick` → 1 consolidation pass, 0 debate rounds
   - `intensity: standard` → 1 challenge + 1 response round
   - `intensity: thorough` → up to 3 rounds until convergence
4. The DA challenges findings, the IC surfaces cross-component gaps, domain experts respond/revise across rounds. Domain expansion via `cross_domain_signals` is handled per `runtime-contracts`.

`diversity_sources` = `["role"]` (+ `"debate-layer"` if any debate round ran).

### Tier 2: Cross-Runtime Council

Fan out to multiple runtime adapters in parallel. Each runtime adapter runs its own internal Tier 1 council using its native dispatch.

**Step 6.2.1: Load runtime settings.**

```bash
cat .runtime-settings.json
```

If not found, run a discovery pass and present available runtimes to the user. Save to `.runtime-settings.json` with a TTL.

```json
{
  "runtimes": {
    "claude":   { "enabled": true },
    "gemini":   { "enabled": true, "model": null },
    "codex":    { "enabled": true, "model": null },
    "opencode": { "enabled": true, "models": [] },
    "kimi":     { "enabled": true, "model": null }
  },
  "reasoning_level": "medium",
  "updated": "{ISO-8601}",
  "ttl_hours": 24
}
```

See `runtime-contracts/SKILL.md` for the full settings schema.

**Step 6.2.2: Read each enabled adapter's SKILL.md.**

```
Read: [skills-root]/runtime-claude/SKILL.md
Read: [skills-root]/runtime-codex/SKILL.md
Read: [skills-root]/runtime-gemini/SKILL.md
Read: [skills-root]/runtime-opencode/SKILL.md
Read: [skills-root]/runtime-kimi/SKILL.md
```

**Step 6.2.3: Dispatch one Task agent per enabled adapter in parallel.**

For each enabled adapter, spawn a Task agent (the "runtime executor") with the adapter's instructions embedded verbatim and the standard `runtime_input` JSON:

```json
{
  "runtime_input": {
    "session_id": "{session_id}-{runtime}",
    "scope": "{working_scope.artifact}",
    "task_description": "{constructed from intent + mode}",
    "task_type": "{council_context.task_type}",
    "domains": ["{domain1}", "{domain2}"],
    "context_summary": "{council_context.context_summary}",
    "intensity": "{council_context.intensity}"
  }
}
```

Each runtime executor:
- Performs the adapter's pre-flight (availability, auth, capability detection)
- Runs its own internal Tier 1 council (parallel domain experts + DA + IC)
- Returns a report conforming to the `runtime-contracts` output schema

**Step 6.2.4: Collect reports.**

Wait for all runtime executors to complete. Each returns one of:
- `COMPLETED` — include in synthesis
- `SKIPPED` — record reason, continue without
- `HALTED` — interactive: surface to user; non-interactive: auto-convert to SKIPPED and record in `auto_skipped_halted_runtimes`
- `ABORTED` — stop entire operation

If zero runtimes returned `COMPLETED` → return `status: ABORTED`, advise the user to install or configure at least one runtime adapter.

`diversity_sources` = `["role", "runtime", "toolchain"]` (+ `"model"` if any runtime ran multi-model, + `"debate-layer"` for any per-runtime debate rounds).

### Tier 3: Cross-Runtime Council with Debate

Same as Tier 2, then add a cross-runtime synthesis round.

**Step 6.3.1: Mechanical deduplication.**

After collecting all runtime reports:
- Group findings by similarity (same domain + similar title/description)
- Mark cross-runtime-confirmed findings (≥2 runtimes surfaced the same issue)
- Mark single-runtime findings (only one runtime surfaced)

**Step 6.3.2: Cross-runtime debate.**

Spawn a **Debate Coordinator** Task agent with:
- All runtime reports
- Deduplication output
- This prompt:

```
You are the Debate Coordinator for a Tier 3 cross-runtime council.

Inputs:
- Reports from {N} runtimes: {runtime list}
- Cross-runtime-confirmed findings: {list}
- Single-runtime findings: {list}

Run a shared-bias challenge:
1. For each cross-runtime-confirmed finding, ask: "Did all runtimes agree because the
   finding is genuinely true, or because they share a blind spot (same training data,
   same prompt framing, same toolchain)?" Identify the actual independent evidence
   per runtime; downgrade findings supported only by reasoning, not evidence.
2. For each single-runtime finding: ask "Why did only this runtime surface this?
   Is it a runtime-specific blind spot of the others, or a hallucination?" Promote
   if the evidence is strong; downgrade if not.
3. Surface integration findings that emerge only from comparing runtime outputs
   (e.g., runtime A flagged X, runtime B flagged Y — combined they imply Z).
4. For intensity == thorough: run a second round challenging the first round's outputs.

Return:
{
  "confirmed_findings": [...],           // survived debate
  "downgraded_findings": [...],           // severity reduced after challenge
  "withdrawn_findings": [...],            // invalidated
  "disputed_findings": [...],             // unresolved after debate
  "integration_findings": [...],          // new findings from cross-runtime comparison
  "shared_bias_warnings": [...],          // explicit notes where bias was suspected
  "debate_rounds": 1 or 2
}
```

`diversity_sources` = `["role", "runtime", "toolchain", "debate-layer"]` (+ `"model"` if multi-model was active in any runtime).

---

## Step 7: Synthesis & Verdict

Combine outputs into the unified council report. Apply verdict logic per `runtime-contracts`:

For `task_type` in {review, analysis}:
- `FAIL` — any CRITICAL output
- `CONCERNS` — ≥1 HIGH output, or ≥3 MEDIUM outputs
- `PASS` — only MEDIUM/LOW/INFO

For `task_type: audit` (compliance-calibrated):
- `FAIL` — any CRITICAL, or ≥2 HIGH compliance-gaps
- `CONCERNS` — 1 HIGH compliance-gap, or ≥3 MEDIUM gaps
- `PASS` — all met or only LOW/INFO gaps

For `mode` in {brainstorm, design, research} → no verdict (`verdict: null`). Output proposals/observations instead.

---

## Step 8: Save Artifact

Write to `.outputs/council/{YYYYMMDD-HHMMSS}-tier{N}-{session_id}.md` with frontmatter:

```yaml
---
skill: agent-council
tier: 0 | 1 | 2 | 3
session_id: "{session_id}"
timestamp: "{ISO-8601}"
mode: review | audit | brainstorm | design | research
task_type: ""
verdict: PASS | FAIL | CONCERNS | null
domains: []
diversity_sources: []
runtimes_used: []        # populated for tier >= 2
models_used: []          # populated when model diversity is active
debate_rounds: 0
tier_history: []         # if escalation occurred
context_summary: ""
---
```

Also save JSON companion: `{YYYYMMDD-HHMMSS}-tier{N}-{session_id}.json` with the full report.

### Council report schema

```json
{
  "type": "agent-council",
  "tier": 0,
  "session_id": "...",
  "mode": "review",
  "task_type": "review",
  "verdict": "PASS",
  "intensity": "standard",
  "domains_covered": [],
  "diversity_sources": [],
  "runtimes_used": [],
  "models_used": [],
  "debate_rounds": 0,
  "tier_history": [],
  "outputs": [],
  "withdrawn_outputs": [],
  "disputed_outputs": [],
  "shared_bias_warnings": [],
  "auto_skipped_halted_runtimes": [],
  "partial_coverage": false,
  "context_summary": "...",
  "confidence": "high | medium | low"
}
```

For brainstorm/design/research modes, replace `outputs` with `proposals` or `observations` arrays as defined in `runtime-contracts`.

---

## Modes

Mode is independent of tier. A Tier 3 council can run in brainstorm mode; a Tier 1 council can run in finding-driven mode. Mode affects **what the council looks at** and **how prompts are framed**.

### Two families of modes

**Open-ended modes** — no prior findings; the council surfaces what's true / wrong / possible:
- `review` / `audit` — produce findings with severity; return verdict.
- `brainstorm` / `design` — produce competing proposals; no verdict; converge via challenge/merge/reject.
- `research` — produce evidence-backed observations with confidence and contradictions; no verdict.
- `synthesis` — Tier 3 only; the cross-runtime synthesis output mode.

**Finding-driven mode** — anchored to specific findings/concerns:
- `finding-driven` — input includes a `findings` list; the council assesses the artifact through the lens of those findings, performing up to four checks: resolution, regression, design-drift, and fix-interaction. See **Finding-Driven Mode** below.

### Brainstorm-mode discipline

The first round (Round 1) must receive a **minimal, non-leading packet**:
- artifact / topic scope, user goal, hard constraints, allowed mutation level, output contract
- **Exclude**: expected findings, suspected root cause, coordinator's preferred architecture, other participants' findings, desired verdict

Later rounds may introduce proposal inventories, challenges, and reconciliation packets. See `runtime-contracts` for the brainstorm output schema.

---

## Finding-Driven Mode

A `finding-driven` council is anchored to a specific findings list — the "lens" through which it views the artifact. Use it whenever the council should assess the artifact **in relation to known concerns**, not as an open exploration.

### Use cases

| Use case | What the `findings` list contains |
|----------|----------------------------------|
| **Post-fix re-review** | Prior council's findings (Stage 1 findings being re-checked after fixes) |
| **Spec compliance check** | Requirements from the spec (each requirement is a "finding to verify") |
| **Regression check after a change** | Known historical bugs or behaviors that must not regress |
| **Targeted review** | User-listed concerns ("review around these 4 things") |
| **Threat-model assessment** | Listed threats from a STRIDE/PASTA exercise |

### Required inputs

```yaml
finding_driven_input:
  mode: "finding-driven"
  findings: []                  # the findings list (the lens)
  fixes_applied: ""             # OPTIONAL — diff/description of changes since findings were surfaced
  original_proposal: ""         # OPTIONAL — the design/spec/intent being upheld
  prior_session_id: ""          # OPTIONAL — if findings came from a prior council session
  # ... + standard fields (scope, domains, tier, intensity)
```

The three optional inputs unlock additional checks:
- Without `fixes_applied` → only resolution check runs (verify each finding against the artifact)
- With `fixes_applied` → resolution + regression + fix-interaction checks
- With `original_proposal` → design-drift check is added

### The four checks

A finding-driven council performs up to four checks, depending on inputs provided:

| # | Check | Question | Requires |
|---|-------|----------|----------|
| 1 | **Resolution** | Did each finding get addressed? | always |
| 2 | **Regression** | Did the fix introduce new issues in the same domain? | `fixes_applied` |
| 3 | **Design drift** | Did the fix subtly violate the original proposal's intent? | `fixes_applied` + `original_proposal` |
| 4 | **Fix interaction** | Do *combinations* of fixes create new issues that no single fix would alone? | `fixes_applied` (≥2 fixes) |

Check #4 is the most commonly missed: naive re-review treats each fix as isolated. Real systems have invariants that span fixes, and fix(F1) + fix(F2) together can break what fix(F1) alone preserves.

### Tier interaction (important asymmetry)

Finding-driven councils may dispatch the **Integration Checker at a higher tier than the rest of the council**, because fix-interaction (Check #4) is exactly where runtime diversity helps catch shared-blind-spot misses.

| Council intent | Rest of council | Integration Checker |
|---------------|-----------------|---------------------|
| Trivial fix re-review (1 finding, 1 fix) | Tier 1 | Tier 1 |
| Multi-fix re-review (≥2 fixes interact) | Tier 1 | **Tier 2** (cross-runtime IC) |
| Critical proposal, multi-fix re-review | Tier 2 | **Tier 3** (cross-runtime IC + debate) |

Record this in the artifact as `ic_tier`: the tier the Integration Checker actually ran at.

### Domain expert prompt (re-review with fixes)

```
This is a finding-driven council. You are a {expert_role}.

You are NOT doing an open review. You are assessing the artifact through the lens
of specific findings.

SCOPE: {scope}
DOMAINS: {domains}
INTENSITY: {intensity}

Prior findings (the lens):
{findings filtered to your domain — and findings in adjacent domains for cross-checks}

Fixes applied since findings were surfaced:
{fixes_applied}

Original proposal (must be upheld):
{original_proposal — only if provided}

Run up to four checks (skip the ones whose inputs are missing):

1. RESOLUTION
   For each prior finding in your domain, report:
   - status: addressed | partially-addressed | not-addressed | superseded | obsolete
   - evidence: specific reference to the fix (or note why not addressed)

2. REGRESSION (only if fixes_applied)
   Did the fixes introduce new issues in YOUR domain that didn't exist before the fix?
   Produce findings with type: "regression-finding".

3. DESIGN DRIFT (only if fixes_applied AND original_proposal)
   Where did the fix subtly diverge from the proposal's stated intent?
   Look for: changed contracts, weakened invariants, scope creep, removed behaviors
   that the proposal required. Produce findings with type: "design-drift-finding".
   These are often more important than the original findings because they're invisible
   to the person who applied the fix.

4. CROSS-DOMAIN IMPACT
   Where did a fix in ANOTHER domain affect your domain? (You are positioned to see
   this; the other domain's expert is not.) Produce findings with type: "cross-domain-impact".

Return outputs in the standard council schema, with each output tagged by
type: "resolution" | "regression-finding" | "design-drift-finding" | "cross-domain-impact".
```

### Integration Checker prompt (re-review with fixes)

```
This is a finding-driven council. You are the Integration Checker.

Your specific job in this mode is FIX-INTERACTION analysis. Domain experts catch
single-fix side effects. You catch what they cannot: combinations.

Fixes applied:
{fixes_applied}

For each PAIR and TRIPLE of fixes, ask:
- Do these fixes interact at any shared interface, state, or invariant?
- Does fix(A) + fix(B) together break something that neither alone breaks?
- Does fix(A) change an assumption that fix(B) depends on?
- Do these fixes together drift further from the original proposal than each alone?

Produce findings with type: "fix-interaction-finding" — each must explicitly name
the fixes involved and the invariant/interface affected.

Also produce standard integration findings (interface mismatches, contract gaps)
across the post-fix state of the system.
```

### Output schema additions

Finding-driven mode adds these arrays to the standard output:

```json
{
  "mode": "finding-driven",
  "prior_session_id": "...",
  "input_findings_count": 5,
  "prior_findings_status": [
    {
      "finding_id": "F1",
      "status": "addressed | partially-addressed | not-addressed | superseded | obsolete",
      "evidence": "..."
    }
  ],
  "regression_findings": [],         // new issues introduced by single fixes
  "design_drift_findings": [],       // fix-vs-proposal divergence
  "fix_interaction_findings": [],    // emergent issues from fix combinations
  "ic_tier": 1                        // tier the Integration Checker actually ran at
}
```

### Verdict logic for finding-driven mode

| Verdict | Condition |
|---------|-----------|
| `FAIL` | Any `not-addressed` finding that was CRITICAL/HIGH, OR any CRITICAL regression / design-drift / fix-interaction finding |
| `CONCERNS` | Any HIGH regression / design-drift / fix-interaction finding, OR ≥2 partially-addressed CRITICAL/HIGH findings |
| `PASS` | All findings addressed, no HIGH+ new issues, no design drift |

A re-review that says "all fixes addressed their findings" but introduces design drift is still `CONCERNS` — that's the point of the mode.

---

## Tier Selection Quick Reference

| Situation | Tier |
|-----------|------|
| 1 trivial domain, no integration concerns | 0 |
| 2–5 domains, single-runtime review, fast turnaround | 1 |
| 5–10 domains, want toolchain/model-family diversity, independent verification | 2 |
| 9+ domains, irreversible/high-stakes decision, security/compliance, max confidence | 3 |
| Tier 1 returned 3+ disputed findings or `low` confidence | Escalate to 2 or 3 |
| Routine 2-domain code-style review | Tier 1 (not Tier 3) |

When in doubt, start at Tier 1 and let the tier-up rule escalate.

---

## Notes

- **Read GLOSSARY.md first.** Anti-patterns 1–7 in the glossary apply directly to this skill. Tier inflation/deflation and fabricated runtime outputs are the most common failure modes.
- **Mode is orthogonal to tier.** Any tier can run any mode (with the obvious exception: Tier 0 in brainstorm produces a single proposal, which usually isn't useful).
- **SKIPPED runtimes are non-blocking** at Tier 2/3. As long as one runtime returns COMPLETED, the council proceeds.
- **Tier escalation is a feature, not a fallback.** Use it deliberately when the lower tier reveals genuine uncertainty.
- **Capability profile flows through every dispatch.** `inspect` vs `modify` is set at the council level and translated to runtime-specific flags by each adapter.
- **Domain expansion via `cross_domain_signals` runs at every tier ≥ 1.** New domain experts can be added mid-debate when a finding has implications outside an expert's domain.
- **Diversity sources are recorded explicitly.** Never leave `diversity_sources` empty; if only role diversity is active, say so.
- **No fabrication.** If a runtime adapter is unavailable at Tier 2/3, mark it SKIPPED and proceed. Do not invent its output.
