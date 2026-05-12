---
name: agent-council
description: Unified multi-agent orchestration skill. Takes a tier parameter (0/1/2/3) that scales from a single agent through in-runtime sub-agent dispatch up to cross-runtime councils with debate. Replaces the historical separate skills "agent-council", "runtime-council", and "deep-council" — all are tiers of the same operation. Supports review, audit, verify, research, planning, implementation, and brainstorm/design modes.
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
  - Bash(python3 *)
---

# Agent Council: Unified Tier-Parameterized Council

Execute this skill to orchestrate agent work at any scale, from a single agent up to a cross-runtime council with debate. **The tier parameter selects the scale; `task_type` selects the authority profile.** Review, verification, planning, implementation, research, and future auto-orchestration are all routed through this same council surface. Do not invoke separate council skills — there is only one.

Guardian, when installed, enforces the council's registration manifest and output authority. It does not decide orchestration; it blocks malformed or unauthorized registrations before `agent-council` dispatches work.

## Phase 0: Orientation

Before doing anything else, read the vocabulary:

```
Read: [skills-root]/council-taxonomy/SKILL.md
```

`council-taxonomy` is this suite's authoritative glossary — tier model, runtime vocabulary, diversity dimensions, and anti-patterns. Every step below assumes that vocabulary. If you skip it, you will produce confused artifacts that downstream agents cannot interpret.

`[skills-root]` is the parent of this skill's directory — resolve with `ls ../` from this skill's location.

---

## Phase 1: Registration & Scope

This phase establishes the council manifest. It resolves what the council is allowed to do, what it is acting on, and whether Guardian is available to enforce the registration.

### Required dependencies

Verify required skills are present:

```
[skills-root]/council-taxonomy/SKILL.md
[skills-root]/context/SKILL.md
[skills-root]/preflight/SKILL.md
[skills-root]/domain-registry/README.md
[skills-root]/runtime-contracts/SKILL.md
```

If a required file is missing, stop and emit an install advisory.

Guardian is optional but should be detected at one of these paths:

```
[skills-root]/guardian/guardian.py
.guardian/guardian.py
```

For Tier 2+ dispatch, also verify runtime adapters:

```
[skills-root]/runtime-claude/SKILL.md
[skills-root]/runtime-codex/SKILL.md
[skills-root]/runtime-gemini/SKILL.md
[skills-root]/runtime-opencode/SKILL.md
[skills-root]/runtime-kimi/SKILL.md
```

If only some *runtime adapters* are missing → log which are unavailable; Tier 2+ will dispatch only the ones present.

### Scope resolution

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
  task_type: ""          # canonical runtime-contracts task_type
  mode: ""               # canonical council mode
  domains: []            # from context (authoritative), supplemented by preflight
  constraints: []        # from preflight (empty if skipped)
  context_summary: ""    # combined description for agent prompts
  intensity: "standard"  # quick | standard | thorough — from routing signals + user request
```

### Council manifest

Build a single manifest before routing or dispatch:

```yaml
council_manifest:
  skill: agent-council
  session_id: "council-{YYYYMMDD-HHmmss}"
  scope: ""                # from working_scope.artifact
  task_type: ""            # review | audit | research | analysis | planning | implementation
  mode: ""                 # review | audit | brainstorm | design | research | synthesis | finding-driven
  domains: []              # from working_scope.domains
  context_summary: ""      # from working_scope.context_summary
  intensity: ""            # quick | standard | thorough
  tier: null               # populated during routing
  ic_tier: null            # populated for finding-driven mode
  capability_profile: ""   # inspect | modify, derived from runtime-contracts
  guardian_enforced: false
  guardian_warnings: []
  registration_errors: []
```

Read `runtime-contracts/SKILL.md` for the canonical capability profile mapping. `task_type` controls authority: inspect tasks (`review`, `audit`, `research`, `analysis`, `planning`) must not modify project state; `implementation` may modify project state.

### Guardian registration enforcement

If Guardian is present, run registration checks against the manifest before selecting a tier or dispatching any agent:

```bash
python3 {guardian_path} check-preflight agent-council \
  --scope-set true \
  --task-type {council_manifest.task_type} \
  --mode {council_manifest.mode} \
  --findings-count {len(findings) if council_manifest.mode == "finding-driven" else 0} \
  --domains-set {true if council_manifest.domains else false}

python3 {guardian_path} check-session-id {council_manifest.session_id}
```

If Guardian exits `2`, stop and surface the BLOCK message. Do not route, dispatch, or write an artifact. If session ID uniqueness fails, generate a new `session_id` and retry once; if the retry fails, stop.

If Guardian exits `1`, continue but record the warning in `guardian_warnings`. If Guardian is absent, continue and keep `guardian_enforced: false`.

The manifest is the shared registration object for the rest of the run. Runtime adapters receive a projection of it as `runtime_input`; output artifacts preserve it so Guardian can validate the completed registration.

---

## Phase 2: Routing

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

Record the selected tier in `council_manifest.tier`.

### Finding-driven mode: IC-tier asymmetry

When `mode == "finding-driven"` with `fixes_applied` containing ≥2 fixes AND at least one **signal-gating trigger** fires, the **Integration Checker may run at a higher tier than the rest of the council**. Fix-interaction analysis (Check #4 in Finding-Driven Mode) is where runtime diversity helps most — but only when the interaction is non-obvious. When the interaction is encoded directly in the diff, a Tier-1 IC will catch it; running cross-runtime IC adds N× context for the same finding.

**Signal-gating triggers (raise IC tier when one or more is present):**

- Concurrency / locks / mutexes / shared state across goroutines or threads
- Persistent storage migrations or schema changes
- Security-sensitive code (auth, crypto, session handling, secret material)
- Cross-component invariants (e.g., shared cache key, distributed lock, API contract)
- Reordering of side effects across components
- More than 5 fixes (combinatorial blast — pairs × triples grow fast)

**Without any trigger, keep IC at the council tier.** Fix count alone is not enough.

| Council intent | Council tier | IC tier |
|---------------|--------------|---------|
| Multi-fix re-review, no signal-gating trigger | 1 | 1 |
| Multi-fix re-review with concurrency / shared state / security signal | 1 | **2** |
| Critical-proposal multi-fix re-review, signal-gated | 2 | **3** |

Record both as `council_manifest.tier` and `council_manifest.ic_tier`. The actual hoist is executed in **IC-Hoist** below. See **Finding-Driven Mode** for the four-check framework.

---

## Phase 3: Domain & Prompt Planning

Read domain definitions from `domain-registry`:

```
Read: [skills-root]/domain-registry/domains/technical.md
Read: [skills-root]/domain-registry/domains/business.md
Read: [skills-root]/domain-registry/domains/creative.md
```

For each domain in `council_manifest.domains`, resolve:
- `expert_role` — domain-registry's named expert
- `focus_areas` — what the expert should focus on
- `standards` — what standards or references apply

These flow into every sub-agent / runtime adapter prompt. **Mode matters:** for `brainstorm` / `design` modes, frame prompts to produce proposals; for `review` / `audit`, frame for findings.

If no domain in the registry substantially covers a concern, synthesize a session-based virtual expert role rather than forcing a mismatched registry entry.

Select the prompt template and conditional inputs to pass:

| `mode` | Prompt template source | Inputs to inject |
|--------|------------------------|------------------|
| Any open-ended mode (`review`/`audit`/`brainstorm`/`design`/`research`/`synthesis`) | `runtime-contracts` Agent Prompt Template | `scope`, `task_description`, `task_type`, `mode`, `domains`, `context_summary`, `intensity` |
| `finding-driven` | Finding-Driven Mode section in this skill (domain-expert prompt + IC prompt below) | All of the above, PLUS `findings`, `fixes_applied`, `original_proposal`, `prior_session_id` (the last three may be empty strings — the prompt templates self-disable corresponding checks when inputs are absent) |

**Tier 0 in finding-driven mode is forbidden.** Tier 0 has no IC role, so Check #4 (fix-interaction) cannot run, and finding-driven without all four checks is misleading. If the user explicitly requests Tier 0 + finding-driven → halt with: `"Tier 0 + finding-driven is contradictory. Use Tier 1 for in-runtime four-check, or Tier 0 + review mode for trivial single-agent review."`

**Tier 2+ in finding-driven mode:** the runtime adapters' `runtime_input` payload MUST include the four finding-driven fields. See Step 6.2.3 for the extended schema.

---

## Phase 4: Dispatch

Dispatch branches first on **mode**, then on **tier**.

---

### Tier 0: Single Review

Single agent, no diversity. Use only when the scope is trivial (1 domain, no integration concerns). Allowed modes: open-ended only (not `finding-driven` — see Step 6.0).

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

1. Construct one prompt per role using the template selected in Step 6.0. For `finding-driven` mode, use the prompt templates from the Finding-Driven Mode section below (which embed the finding-driven inputs) instead of the generic Agent Prompt Template.
2. Spawn all agents in parallel using the runtime's native dispatch mechanism. Detect the mechanism by tool availability — see `runtime-contracts/tool-discovery.md`.
3. After all complete, run the Post-Analysis Protocol from `runtime-contracts`:
   - `intensity: quick` → 1 consolidation pass, 0 debate rounds
   - `intensity: standard` → 1 challenge + 1 response round
   - `intensity: thorough` → up to 3 rounds until convergence
4. The DA challenges findings, the IC surfaces cross-component gaps, domain experts respond/revise across rounds. Domain expansion via `cross_domain_signals` is handled per `runtime-contracts`.
5. **IC-hoist (finding-driven mode, optional):** If `council_context.ic_tier > council_context.tier`, additionally dispatch a parallel IC-only fan-out at the higher tier — see Step 6.IC below.

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

For each enabled adapter, spawn a Task agent (the "runtime executor") with the adapter's instructions embedded verbatim and the `runtime_input` JSON:

```json
{
  "runtime_input": {
    "session_id": "{session_id}-{runtime}",
    "scope": "{working_scope.artifact}",
    "task_description": "{constructed from intent + mode}",
    "task_type": "{council_context.task_type}",
    "mode": "{council_context.mode}",
    "domains": ["{domain1}", "{domain2}"],
    "context_summary": "{council_context.context_summary}",
    "intensity": "{council_context.intensity}",

    "findings": [],
    "fixes_applied": "",
    "original_proposal": "",
    "prior_session_id": ""
  }
}
```

When `mode == "finding-driven"`, populate `findings` / `fixes_applied` / `original_proposal` / `prior_session_id` from the council's input. For open-ended modes, leave the last four empty — runtime adapters MUST honor this by skipping the finding-driven prompt section per `runtime-contracts` Agent Prompt Template.

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

### Step 6.IC: IC-Hoist (finding-driven mode only, conditional)

This sub-step runs **in addition to** the main tier dispatch when `council_context.ic_tier > council_context.tier`. It does NOT replace the regular Integration Checker — it adds a higher-tier IC pass that ONLY looks at fix-interaction.

**When to dispatch:**

The IC-hoist runs when ALL of these are true:
- `mode == "finding-driven"`
- `fixes_applied` contains 2+ fixes
- At least one signal-gated trigger fires (set via Step 3 IC-tier asymmetry rule, or by explicit input): the fixes touch shared state, concurrency primitives, security-sensitive code, persistent storage, or cross-component invariants. **Do NOT auto-hoist on fix count alone** — runtime diversity helps where evidence is underdetermined, not where the diff is concrete.

**Dispatch protocol:**

1. After the main tier dispatch completes (and produces a council report at `council_context.tier`), prepare a IC-only fan-out at `council_context.ic_tier`.
2. The IC-hoist fan-out invokes the same machinery as Tier 2 (Step 6.2) but spawns ONLY the Integration Checker role in each enabled runtime adapter, using the finding-driven IC prompt (see Finding-Driven Mode below).
3. Each hoisted IC produces fix-interaction findings under their `outputs[]` with `type: "fix-interaction-finding"`.
4. Merge the hoisted IC outputs into the main council report's `outputs[]` (deduped by similarity), tagged with `agent: "integration-checker-hoisted"`.

**When NOT to hoist:**

If the council tier is already 2 or 3, the IC already ran across runtimes — hoisting adds no diversity. Only hoist when `tier == 1` (or when explicit `ic_tier` is set higher by the orchestrator).

Record in the council report: `ic_tier: <actual tier the IC ran at>`, distinct from the main `tier`.

---

## Step 7: Synthesis & Verdict

Combine outputs into the unified council report. **Verdict routes by `mode` first, then `task_type`** — see `runtime-contracts/SKILL.md` "Verdict Logic" for the canonical tables.

Routing summary:

- `mode == "finding-driven"` → use the finding-driven verdict table (canonical in `runtime-contracts`). The presence of design-drift / regression / fix-interaction findings can flip a "all addressed" verdict to `CONCERNS`. **Takes precedence over `task_type` routing.**
- `mode` in {`brainstorm`, `design`, `research`, `synthesis`} → no verdict (`verdict: null`). Output proposals / observations / synthesis records instead.
- Otherwise route by `task_type`: `review`/`analysis` use the standard severity table; `audit` uses the compliance-calibrated table.

Refer to `runtime-contracts` for the exact verdict conditions. Do not duplicate them here.

---

## Step 8: Save Artifact

Write to `.outputs/council/{YYYYMMDD-HHMMSS}-tier{N}-{session_id}.md` with frontmatter:

```yaml
---
skill: agent-council
tier: 0 | 1 | 2 | 3
ic_tier: 0 | 1 | 2 | 3                  # null outside finding-driven; equals tier unless IC-hoist ran
session_id: "{session_id}"
timestamp: "{ISO-8601}"
mode: review | audit | brainstorm | design | research | synthesis | finding-driven
task_type: ""
verdict: PASS | FAIL | CONCERNS | null
domains: []
diversity_sources: []
runtimes_used: []        # populated for tier >= 2
models_used: []          # populated when model diversity is active
debate_rounds: 0
tier_history: []         # if escalation occurred
prior_session_id: ""     # populated when mode == finding-driven and a prior council artifact was passed in
context_summary: ""
---
```

Also save JSON companion: `{YYYYMMDD-HHMMSS}-tier{N}-{session_id}.json` with the full report.

### Council report schema

```json
{
  "type": "agent-council",
  "tier": 0,
  "ic_tier": null,
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
  "confidence": "high | medium | low",

  "prior_session_id": null,
  "input_findings_count": null
}
```

**For brainstorm/design/research modes:** replace `outputs` with `proposals` or `observations` arrays as defined in `runtime-contracts`.

**For finding-driven mode:** the four finding-driven output types (`resolution`, `regression-finding`, `design-drift-finding`, `cross-domain-impact`, `fix-interaction-finding`) live in the standard `outputs[]` array, filterable by `type` — they do NOT get their own top-level arrays (the schema previously listed `regression_findings` / `design_drift_findings` / `fix_interaction_findings` as parallel arrays; this duplicated `outputs[]` semantics and has been removed). Consumers should filter `outputs[]` by `type` when they need a specific category. Resolution items additionally carry `resolution_status` and `target_finding_id` fields — see `runtime-contracts` "Finding-driven-mode types".

`ic_tier` is non-null whenever finding-driven mode runs; it equals `tier` unless Step 6.IC (IC-hoist) elevated it. `prior_session_id` is populated when a prior council artifact was passed in as the `findings` source.

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
  findings: []                  # the findings list (the lens) — see Finding Object Schema below
  fixes_applied: ""             # OPTIONAL — diff/description of changes since findings were surfaced
  original_proposal: ""         # OPTIONAL — the design/spec/intent being upheld
  prior_session_id: ""          # OPTIONAL — if findings came from a prior council session
  # ... + standard fields (scope, domains, tier, intensity)
```

**Finding object schema** (canonical definition in `runtime-contracts/SKILL.md` "Finding Object Schema"):

Each item in `findings` must have `{id, title, description, severity, domain, source}`. Items can be lifted directly from a prior `agent-council` artifact's `outputs[]` array — they already conform. For spec-compliance use, each spec requirement becomes one finding (with `source: "spec:<path>"`).

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

Return outputs in the standard council schema. Tag each output by `type`:
- `resolution` — status check for a prior finding. MUST include `target_finding_id` (referencing the input finding's id) and `resolution_status` (`addressed | partially-addressed | not-addressed | superseded | obsolete`). Severity is `null`.
- `regression-finding` — new issue introduced by a fix in your domain.
- `design-drift-finding` — fix-vs-proposal divergence.
- `cross-domain-impact` — finding where a fix in another domain affects yours.

All items go into the single `outputs[]` array — consumers filter by `type`. Do NOT emit parallel arrays.
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

For each interaction you find, emit an output with type: "fix-interaction-finding".
In the `evidence` field, EXPLICITLY NAME the fixes involved (e.g., "Fix2 + Fix3")
and the invariant or interface affected.

Also produce standard integration findings (type: "finding", domain: "integration")
for interface mismatches and contract gaps across the post-fix state of the system.
```

### Output

Finding-driven mode does NOT introduce new top-level arrays. All items go into the canonical `outputs[]` array, tagged by `type`. The council-level schema gains only two finding-driven-specific fields (in addition to the always-present `ic_tier`):

```json
{
  "mode": "finding-driven",
  "prior_session_id": "...",       // already in the council report schema
  "input_findings_count": 5,        // already in the council report schema
  "ic_tier": 2                      // already in the council report schema; documents actual IC tier
}
```

Consumer-side filtering (examples):
- Resolution checks: `outputs.filter(o => o.type === "resolution")`
- Regression findings: `outputs.filter(o => o.type === "regression-finding")`
- Design-drift findings: `outputs.filter(o => o.type === "design-drift-finding")`
- Fix-interaction findings: `outputs.filter(o => o.type === "fix-interaction-finding")`

### Verdict logic for finding-driven mode

Defined canonically in `runtime-contracts/SKILL.md` "Verdict Logic" → "For `mode == finding-driven`". Do not duplicate the table here. The short version: any unaddressed CRITICAL/HIGH or any CRITICAL new-issue (regression/drift/interaction) → `FAIL`. Any HIGH new-issue → `CONCERNS`. Otherwise → `PASS`.

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
