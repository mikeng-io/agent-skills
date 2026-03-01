# Deep Skills Suite — Topology

This document describes the relationship between all skills, how they depend on each other, and how routing decisions are made based on context, complexity, and user input.

---

## Component Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Deep Skills Suite                              │
│                                                                     │
│  Foundation                                                         │
│  ├── domain-registry     Knowledge base — expert roles & signals    │
│  ├── bridge-commons      Shared contract — all bridges implement     │
│  └── debate-protocol     5-phase structured review debate           │
│                                                                     │
│  Context Intelligence                                               │
│  └── context        Classify artifact, select domains, route   │
│                                                                     │
│  Bridge Adapters (reference — not invocable standalone)            │
│  ├── bridge-claude       Task tool → claude CLI → Anthropic API     │
│  ├── bridge-gemini       gemini -p → SKIPPED                       │
│  ├── bridge-codex        MCP → codex exec → SKIPPED                │
│  └── bridge-opencode     HTTP API → opencode run → SKIPPED         │
│                                                                     │
│  Orchestrators                                                      │
│  ├── parallel-workflow   DAG dispatch — independent sub-agents      │
│  └── deep-council        Multi-model council — all bridges + debate │
│                                                                     │
│  Deep Skills (user-invocable)                                       │
│  ├── deep-explorer       Explore and map an artifact or codebase    │
│  ├── context        Classify and route (also standalone)       │
│  ├── deep-review         Multi-agent review with findings           │
│  ├── deep-audit          Compliance, security, standards audit      │
│  ├── deep-verify         Verify spec compliance and correctness     │
│  └── deep-research       Multi-domain research and synthesis        │
│                                                                     │
│  Optional Data Sources (invokable standalone or by other skills)   │
│  ├── deepwiki            Devin DeepWiki — codebase wiki Q&A        │
│  ├── brave-search        Brave Search MCP — web/news/local search  │
│  └── perplexity          Perplexity MCP — AI-synthesized answers   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Dependency Graph

```
domain-registry ◄─────────────────────────── all bridges
                                              deep-council
                                              deep-* skills

bridge-commons ◄──────────────────────────── bridge-claude
                                              bridge-gemini
                                              bridge-codex
                                              bridge-opencode

debate-protocol ◄─────────────────────────── deep-council (embedded inline)
                                              deep-verify (optional)

context ──────────────────────────────► domain selection
                                             routing decision

parallel-workflow ◄───────────────────────── deep-* skills (default path)
                                              deep-council (bridge dispatch)

deep-council ◄────────────────────────────── deep-* skills (escalation path)
  └── uses: bridge-claude
            bridge-gemini
            bridge-codex
            bridge-opencode
            debate-protocol (inline)
            parallel-workflow (for bridge dispatch)
```

---

## Routing Decision

Every deep skill performs a routing decision — either inline or by calling `context`. The routing determines which execution path to use.

```
Context analysis
  │
  ├─► Artifact type detected (code, financial, marketing, creative, research, mixed)
  ├─► Domains selected from domain-registry
  └─► Routing decided:

        Condition                              → Route
        ─────────────────────────────────────────────────────────────
        < 3 domains, no high-stakes signals   → parallel-workflow
        ≥ 3 domains OR high-stakes signals    → parallel-workflow + debate-protocol
        Explicit "multi-model" request        → deep-council
        intensity = "thorough"               → deep-council (recommended)
        User override                         → user choice wins
```

High-stakes signals include: security-critical changes, financial data, compliance requirements, production incidents, cryptographic systems.

---

## Execution Paths

### Path A: Parallel Workflow

Default path for most tasks. Independent sub-agents work in parallel; no inter-agent communication. Results reported back to coordinator.

```
deep-{skill}
  └── parallel-workflow
        ├── agent: {domain_1} expert
        ├── agent: {domain_2} expert
        └── agent: Integration Checker
              │
              └── synthesize → output
```

Best for: focused reviews, clear scope, < 3 domains, quick or standard intensity.

### Path B: Parallel Workflow + Debate

Adds a structured debate phase after parallel analysis. Domain experts challenge each other's findings through 3–5 rounds; a Devil's Advocate drives cross-examination.

```
deep-{skill}
  ├── parallel-workflow  (Phase 1: independent analysis)
  └── debate-protocol    (Phases 2–5: challenge, synthesis, verdict)
        ├── domain experts
        ├── Devil's Advocate (cross-challenges)
        └── Integration Checker
              │
              └── confirmed / withdrawn / disputed / merged findings
```

Best for: ≥ 3 domains, high-stakes changes, standard or thorough intensity.

### Path C: Deep Council (Multi-Model)

Dispatches the task to multiple AI runtimes in parallel. The architecture has **two debate layers**:

- **Layer 2 (intra-bridge):** Each bridge extracts maximum value from its own model family before reporting
- **Layer 1 (cross-bridge):** After all bridges report, a Debate Coordinator challenges the aggregated findings across model families

```
deep-council
  │
  ├── Layer 2: Each bridge runs independently in parallel
  │     ├── bridge-claude    → full 5-phase debate (DA + IC + domain experts)
  │     ├── bridge-gemini    → Post-Analysis Protocol rounds   ← SKIPPED if unavailable
  │     ├── bridge-codex     → Post-Analysis Protocol rounds   ← SKIPPED if unavailable
  │     └── bridge-opencode  → single-model: Post-Analysis rounds
  │                            multi-model:  N parallel models → mini-synthesis
  │                            (configured via .bridge-settings.json models array)
  │                                                            ← SKIPPED if unavailable
  │
  └── Layer 1: Cross-bridge synthesis (deep-council Step 6)
        Stage A: Mechanical deduplication (find overlapping findings)
        Stage B: Debate Coordinator Task agent
                 ├── DA challenges multi-model-confirmed findings
                 │   ("all bridges agreed — shared bias or genuine?")
                 ├── IC checks cross-bridge integration gaps
                 └── 2–3 challenge rounds (standard/thorough)
                       │
                       └── confirmed / downgraded / disputed / withdrawn
                           integration_findings (new — emerged from cross-bridge debate)
```

Best for: maximum confidence, multi-model verification, explicit user request, thorough intensity.

---

## Skill Routing Table

| Skill | Default path | Can escalate to | Notes |
|-------|-------------|----------------|-------|
| `deep-explorer` | parallel-workflow | — | Exploration only; no debate needed |
| `context` | single-agent | — | Classifier; always single-agent |
| `deep-review` | parallel-workflow | deep-council | Escalates on high-stakes or user request |
| `deep-audit` | parallel-workflow | deep-council | Escalates on compliance/security signals |
| `deep-verify` | parallel-workflow + debate-protocol | deep-council | Debate is default for verification |
| `deep-research` | parallel-workflow | deep-council | Multi-model adds perspective diversity |

---

## Bridge Availability and Fallback

Deep council is non-blocking — bridges that are unavailable are skipped and the council continues with whatever is available.

```
Executor is Claude Code    → bridge-claude available (Task tool accessible)
gemini CLI installed       → bridge-gemini available
Codex MCP configured
  OR codex CLI installed   → bridge-codex available
opencode serve running
  OR opencode CLI installed → bridge-opencode available
  + .bridge-settings.json models array has 2+ entries → multi-model dispatch

Minimum viable council: any single bridge that returns COMPLETED
Zero bridges complete → ABORTED (emitted by deep-council)
```

Bridge availability is not guaranteed for any bridge — all depend on the executor environment and installed tools. See bridge-commons for the two-layer debate architecture and `.bridge-settings.json` schema.

---

## Component Context Types

| Component | context | Invocable standalone? |
|-----------|---------|----------------------|
| `domain-registry` | — (pure reference) | No |
| `bridge-commons` | reference | No |
| `debate-protocol` | fork | Yes |
| `context` | fork | Yes |
| `bridge-claude` | reference | No |
| `bridge-gemini` | reference | No |
| `bridge-codex` | reference | No |
| `bridge-opencode` | reference | No |
| `parallel-workflow` | fork | Yes |
| `deep-council` | fork | Yes |
| `deep-explorer` | fork | Yes |
| `deep-review` | fork | Yes |
| `deep-audit` | fork | Yes |
| `deep-verify` | fork | Yes |
| `deep-research` | fork | Yes |
| `deepwiki` | fork | Yes |
| `brave-search` | fork | Yes |
| `perplexity` | fork | Yes |

`context: reference` skills are read via the `Read` tool and embedded into Task agent prompts. They are not invoked separately.

---

## Key Design Principles

1. **Non-blocking bridges** — A missing CLI never halts a session; it produces `SKIPPED`.
2. **Generic, not review-specific** — All components handle review, planning, implementation, analysis, and research.
3. **No hardcoded models** — Every bridge detects the latest available model at runtime.
4. **Progressive enhancement** — Multi-agent mode, debate, and multi-model council are additive. Each skill works with the minimum available capability.
5. **Composable** — Any skill can be used standalone or as part of a larger orchestration.
6. **Shared contract** — All bridges implement `bridge-commons` — one schema to learn, four runtimes.
