---
skill: deep-council
timestamp: 2026-03-01T12:37:30Z
artifact_type: council
domains: [agent-orchestration, prompt-engineering, specification-integrity, developer-experience, integration, cross-domain]
verdict: FAIL
bridges_available: [claude, gemini, codex, opencode]
bridges_skipped: []
review_id: "council-20260301-selfaudit"
context_summary: "Self-audit of Deep Skills Suite v2 — multi-model review framework"
---

# Deep Council Self-Audit — council-20260301-selfaudit

**Verdict: FAIL**
Bridges: claude (Agent Teams, 6 sub-agents) · gemini (CLI) · codex (CLI, single-agent) · opencode (CLI, glm/glm-4.7)
Intensity: thorough | Domains: agent-orchestration, prompt-engineering, specification-integrity, developer-experience

---

## Cross-Bridge Synthesis

### Multi-Model Confirmed — CRITICAL (all 4 bridges)

**MMC-C1 · CRITICAL · Verdict Vocabulary Fragmentation**
Confirmed by: claude (MMC001, MMC009), gemini (S001), codex (X001), opencode (O001)

bridge-commons defines PASS / CONCERNS / FAIL as the canonical verdict enum. At least three skills diverge:
- deep-verify uses PASS_WITH_CONCERNS
- deep-audit uses PASS_WITH_WARNINGS
- deep-council's cross-bridge logic diverges from bridge-commons' per-bridge logic (bridge-commons: FAIL = any CRITICAL; deep-council: FAIL = multi-model-confirmed CRITICAL only)

Any consumer comparing verdicts across skill layers gets silent mismatches. This is a schema contract violation.

**Fix:** Standardize on PASS / CONCERNS / FAIL everywhere. Replace PASS_WITH_CONCERNS and PASS_WITH_WARNINGS with CONCERNS. Align deep-council's cross-bridge verdict with the bridge-commons definition, or explicitly document that cross-bridge verdicts use different thresholds and why.

---

**MMC-C2 · CRITICAL · HALTED Status Unhandled in Parallel Dispatch**
Confirmed by: claude (MMC005), gemini (A001), codex (X001, X012), opencode (O002)

bridge-codex and bridge-opencode issue HALTED (requires user decision) for CLI-not-found and unauthenticated states. bridge-commons requires non-blocking behavior. deep-council has no handling for HALTED returns — only SKIPPED is handled. In a parallel dispatch, one HALTED bridge can freeze the entire council indefinitely (Gemini's xhigh confirmation user prompt is the same failure mode).

**Fix:** Add HALTED lifecycle to deep-council: surface halt_message, offer skip/retry/abort, define non-interactive default (auto-SKIPPED with warning). Document in bridge-commons that orchestrators MUST handle HALTED.

---

### Multi-Model Confirmed — HIGH

**MMC-H1 · HIGH · debate-protocol Duplicated Inline in deep-council**
Confirmed by: claude (MMC002), gemini (A002), opencode (O003)

deep-council embeds debate-protocol synthesis logic inline by design ("do not invoke as a separate skill"). This means consensus thresholds, finding states, and phase structure are maintained in two places with no sync mechanism. Any change to debate-protocol silently drifts from the council's synthesis logic.

**Fix:** Either allow debate-protocol invocation as a Task agent from deep-council (cleaner), or add an explicit "derived from debate-protocol version X" reference in deep-council with a lint rule to detect drift.

---

**MMC-H2 · HIGH · Bridge Input Contract Diverges from bridge-commons Schema**
Confirmed by: claude (MMC006, MMC007), codex (X002)

deep-council's bridge_input template passes: review_id, review_scope, domains, context_summary, intensity.
bridge-commons canonical schema requires: session_id, scope, task_type, task_description, domains, intensity.

Missing: task_type (controls prompt framing), task_description, and the field names diverge (review_id ≠ session_id, review_scope ≠ scope). Bridges that use task_type for framing selection get undefined behavior.

**Fix:** Align deep-council bridge_input to bridge-commons schema. Add task_type extraction in Step 1. Map review_id → session_id in the bridge_input payload.

---

**MMC-H3 · HIGH · Analysis Depth Asymmetry Across Bridges (Unacknowledged)**
Confirmed by: claude (MMC003), gemini (A004)

Claude bridge with Agent Teams runs the full 5-phase debate-protocol internally. Gemini/Codex/OpenCode run the simpler bridge-commons Post-Analysis Protocol (1-3 stateless rounds). deep-council synthesis in Step 6 treats findings from all bridges with equal confidence weight, ignoring that Claude findings have been through a richer adversarial process. A disputed finding between Claude and Gemini may reflect depth difference, not genuine model disagreement.

**Fix:** Add analysis_depth field to bridge output (full-debate | multi-round | single-pass). In deep-council synthesis, weight findings from full-debate bridges higher when computing confidence.

---

**MMC-H4 · HIGH · False "Claude Bridge Is Always Available" Invariant**
Confirmed by: codex (X003) — also structurally implied by claude (MMC note on non-native executors)

deep-council and TOPOLOGY.md state "Minimum: claude is always available." bridge-claude/SKILL.md explicitly defines a SKIPPED path when Task tool is unavailable, claude CLI not found, and ANTHROPIC_API_KEY not set. The invariant is false when bridge-claude runs inside a non-Claude-Code executor. deep-council has no logic for zero bridges completing.

**Fix:** Remove the hard guarantee. Add minimum-bridge validation: if zero bridges return COMPLETED, emit ABORTED with explanation.

---

### Multi-Model Confirmed — MEDIUM

**MMC-M1 · MEDIUM · Debate Round Budgets Inconsistent Across Documents**
Confirmed by: codex (X004) — patterns also in claude (MMC002 discussion)

bridge-commons: quick=0 rounds, standard=1, thorough=3.
debate-protocol: quick=0 max_rounds, standard=3, thorough=5.
These are different. Timeout estimates are computed from round counts, so miscalculated timeouts follow.

**Fix:** Single source of truth for intensity→round mapping. Reference from both documents.

---

**MMC-M2 · MEDIUM · Codex Timeout Math Error**
Confirmed by: claude (MMC010), codex (X005)

bridge-codex says "increase base by 50%, e.g. 180s → 240s." 180 × 1.5 = 270, not 240. The stated percentage and example contradict each other.

**Fix:** Correct to 270s (or change the stated multiplier to 33%).

---

**MMC-M3 · MEDIUM · Output Status Enum Incomplete**
Confirmed by: claude (SS006 context), codex (X009)

Output item status field uses confirmed/revised/discovered/null but never formally declares withdrawn or disputed, which are required by the debate protocol. No rule specifies whether disputed items live in outputs or disputed_outputs.

**Fix:** Expand the formal status enum to all 5 values: confirmed / revised / withdrawn / disputed / discovered. Add placement rules.

---

**MMC-M4 · MEDIUM · Bridge Settings Cache Has No Invalidation Strategy**
Confirmed by: claude (SS008), gemini (D001)

.bridge-settings.json has an updated timestamp but no TTL. If environment changes (CLI uninstalled, new provider), the stale cache causes confusing failures rather than re-discovery.

**Fix:** Add ttl_hours field (default: 24). Revalidate if age > TTL.

---

**MMC-M5 · MEDIUM · Virtual Expert Cold-Start / Synthesis Failure Path Unspecified**
Confirmed by: gemini (P001), opencode (O008)

Newly added domain experts (via cross_domain_signals mid-debate) get only a trigger-finding prompt, missing the Phase 1 full-context understanding that other experts have. Additionally, Tier 3 virtual expert synthesis has no failure path — if synthesis fails, the skill has no defined fallback.

**Fix:** Provide a Context Fast-Forward packet to newly added experts (Phase 1 summaries from other domains). Add a synthesis timeout and GENERALIST_FALLBACK mode for Tier 3 failure.

---

### Notable Single-Source Findings (Selected HIGH)

| ID | Bridge | Severity | Title |
|----|--------|----------|-------|
| SS004 | claude | HIGH | parallel-workflow uses symlinks — every other skill prohibits them |
| SS003 | claude | HIGH | deep-context routing contradicts TOPOLOGY.md for thorough intensity |
| MMC004 | claude | HIGH | Missing validator files referenced in deep-verify + deep-research |
| SS005 | claude | HIGH | DA prompt in bridge-claude is vastly thinner than debate-protocol DA spec |
| SS009 | claude | HIGH | Gemini --approval-mode auto_edit may permit writes in analysis mode |
| SS007 | claude | HIGH | Non-existent agent-browser skill referenced in deep-research |
| A003 | gemini | HIGH | Nested sub-agent recursion depth limits unspecified |
| X003 | codex | HIGH | False "Claude always available" invariant (also MMC-H4 above) |
| X006 | codex | HIGH | Codex coordinator prompt output schema diverges from bridge-commons |
| X008 | codex | HIGH | Full SKILL.md verbatim embedding in Task prompts risks token overload |
| O006 | opencode | HIGH | No observability / correlation ID across orchestrators |
| O004 | opencode | HIGH | Aggregation model divergence: deep-verify weighted % vs bridge-commons debate rounds |

---

### Disputed Findings

**DISP-1: Whether HALTED should auto-SKIPPED in non-interactive pipelines**
- claude + codex: HALTED should auto-map to SKIPPED in non-interactive contexts (never-block principle)
- gemini: HALTED is legitimate — silently skipping hides config gaps; the issue is that deep-council doesn't handle it

Unresolved: "never block orchestrator" vs "never silently skip config gap" are both stated as imperatives. Architectural decision needed on which wins in non-interactive contexts.

**DISP-2: debate-protocol invocable vs inline in deep-council**
- specification-integrity: sync risk is real; debate-protocol should be callable as Task agent
- agent-orchestration: cross-bridge synthesis is architecturally different from intra-bridge debate; inline is correct

---

## Council Verdict

**FAIL**

Trigger: 2 multi-model-confirmed CRITICAL findings (verdict fragmentation + HALTED unhandled).

The framework has strong architectural bones — clean non-blocking bridge patterns, coherent skill topology, well-designed virtual expert synthesis. The failures are fixable without restructuring. Priority order:

1. **Verdict vocabulary** — touches every skill output, silent failures, fix first
2. **HALTED lifecycle in deep-council** — orchestration correctness
3. **Bridge input schema alignment** — contract violation with bridge-commons
4. **False Claude-always-available invariant** — false safety guarantee
5. **Debate round budget alignment** — affects timeouts and quality

---

## Innovation Signals (from all bridges)

- **Finding lineage tracking** (claude SS015): multi-model-confirmed findings should carry source_finding_ids from each bridge
- **Context Compactor protocol** (gemini O001): stateless bridges need round-to-round context summarization to prevent prompt bloat
- **Observability / correlation IDs** (opencode O006): request_id propagated through all orchestrators; OpenTelemetry spans for agent spawns
- **Provider rate-limit coordination** (opencode O007): parallel bridge dispatch hits all providers simultaneously — needs token buckets
- **Adaptive timeouts** (opencode O009): current timeout constants are arbitrary; instrument and derive from p95 empirical data
- **domain-registry versioning** (claude SS016): add version + last_updated to domain files for drift detection
