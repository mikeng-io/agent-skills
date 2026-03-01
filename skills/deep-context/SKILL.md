---
name: deep-context
description: Analyze conversation context to classify what is being discussed, detect relevant domains from domain-registry, and determine optimal routing (parallel-workflow vs debate-protocol vs deep-council). Can be invoked directly or called by other skills as a pre-flight step.
location: managed
context: fork
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(ls *)
  - Task
  - Write
  - Bash(mkdir *)
---

# Deep Context: Artifact Classifier and Smart Router

Execute this skill to analyze conversation context, detect relevant domains, and determine the optimal review routing strategy.

## Execution Instructions

When invoked, analyze the current conversation and produce a context report.

---

## Step 1: Analyze Conversation

Extract from the conversation:

```yaml
conversation_signals:
  files_mentioned: []        # File paths referenced (e.g., "src/auth.go")
  artifacts_mentioned: []    # Other artifacts (Figma files, spreadsheets, docs)
  topics: []                 # Key topics discussed
  concerns: []               # What the user is worried about
  explicit_domains: []       # Domains explicitly named by user
  explicit_routing: ""       # If user said "multi-model", "debate", "thorough", etc.
  intent: ""                 # What the user wants to accomplish
```

---

## Step 2: Classify Artifact Type

Determine the primary artifact type from signals:

```yaml
artifact_type_rules:
  code:
    signals:
      - File extensions: .go, .py, .ts, .js, .rs, .java, .rb, .kt, .swift, .c, .cpp
      - Mentions of: function, class, module, API, endpoint, service, handler
      - Git references or diff mentions

  financial:
    signals:
      - Terms: P&L, revenue, profit, loss, budget, forecast, balance sheet, ROI, EBITDA
      - Spreadsheet files: .xlsx, .csv with financial column names
      - GAAP, IFRS, accounting mentions

  marketing:
    signals:
      - Terms: campaign, audience, conversion, CTR, CPC, funnel, brand, messaging, copywriting
      - Marketing channel names: email, social, PPC, SEO, content marketing

  research:
    signals:
      - Terms: literature, sources, evidence, citations, study, paper, methodology
      - Academic language patterns
      - Bibliography or reference mentions

  creative:
    signals:
      - Design files: .fig, .sketch, .psd, .ai, .xd
      - Terms: design, visual, layout, color, typography, UX, wireframe, mockup, copy

  mixed:
    signals:
      - Signals from 2+ categories above present simultaneously
```

Artifact type selection:
1. If signals from 2+ types → `mixed`
2. If dominant signals clearly point to one type → that type
3. Default → `code` (most common)

---

## Step 3: Select Domains from Domain-Registry

Read the domain-registry files to match detected signals:

```bash
# Read all three domain category files
Read: [skills-root]/domain-registry/domains/technical.md
Read: [skills-root]/domain-registry/domains/business.md
Read: [skills-root]/domain-registry/domains/creative.md
```

Where `[skills-root]` is the parent directory of the skill invoking this step. Resolve by navigating up from the current skill's location using `ls` or `Glob` if needed.

For each domain in the registry files:
- Check if any of the domain's `trigger_signals` appear in the conversation
- Match against: file names, topics, concerns, explicit mentions, technical terms
- Select ALL matching domains (minimum 1, no maximum)

If no domains match clearly:
- For `code` artifact type → default to `api` + `testing`
- For `financial` → default to `finance`
- For `marketing` → default to `marketing`
- For `research` → default to `content`
- For `creative` → default to `design` + `ux`

---

## Step 4: Determine Routing

Apply routing decision rules:

```yaml
routing_rules:
  parallel-workflow:
    conditions:
      - domains_count < 3
      - no high-stakes signals (production incident, financial risk, security breach)
      - no explicit "thorough" or "critical" in user request
    description: "Parallel independent sub-agents, no debate needed"

  debate-protocol:
    conditions_any:
      - domains_count >= 3
      - high_stakes_signals: [production, incident, breach, compliance, audit, lawsuit, financial risk]
      - explicit_signals: ["thorough", "critical", "high-stakes", "careful", "deep"]
    intensity_selection:
      thorough: explicit "thorough" or "critical" in request
      standard: default for debate-protocol routing
      quick: explicit "quick" or "fast" in request
    description: "Structured 5-phase adversarial debate across domains"

  deep-council:
    conditions_any:
      - explicit_signals: ["multi-model", "multiple models", "council", "cross-model"]
      - user explicitly requests multiple AI perspectives
      - intensity = thorough → deep-council (recommended — thorough analysis benefits from multi-model perspectives)
    description: "Multi-model review across Claude, Gemini, Codex, OpenCode bridges"
```

Routing priority: `deep-council` > `debate-protocol` > `parallel-workflow`

---

## Step 5: Determine Confidence

```yaml
confidence_levels:
  high:
    - Explicit domain mentions in conversation
    - Clear file types detected
    - Unambiguous artifact type

  medium:
    - Inferred domains from technical terms
    - Mixed signals with dominant pattern

  low:
    - Minimal conversation context
    - Highly ambiguous signals
    - New conversation with few messages
```

---

## Step 6: Produce Context Report

Output the context report:

```yaml
context_report:
  artifact_type: code | financial | marketing | creative | research | mixed
  topics: []                    # Key topics identified
  concerns: []                  # User concerns identified
  domains: []                   # Selected domain names from domain-registry
  domain_experts: []            # Corresponding expert_role values
  routing: parallel-workflow | debate-protocol | deep-council
  debate_intensity: quick | standard | thorough   # Only if routing = debate-protocol
  confidence: high | medium | low
  rationale: ""                 # Brief explanation of routing decision
  signals_detected:
    files: []
    topics: []
    explicit_mentions: []
```

Display this report to the user and/or return it to the calling skill.

---

## Step 7: Save Artifact

Save context report to `.outputs/context/{YYYYMMDD-HHMMSS}-context.md` with YAML frontmatter:

```yaml
---
skill: deep-context
timestamp: {ISO-8601}
artifact_type: {artifact_type}
domains: [{domain1}, {domain2}]
routing: {routing}
confidence: {confidence}
context_summary: "{brief description of what was analyzed}"
session_id: "{unique id}"
---
```

Also save JSON companion: `{YYYYMMDD-HHMMSS}-context.json`

**No symlinks.** To find the latest artifact:
```bash
ls -t .outputs/context/ | head -1
```

**QMD Integration (optional):**
```bash
qmd collection add .outputs/context/ --name "context-reports" --mask "**/*.md" 2>/dev/null || true
qmd update 2>/dev/null || true
```

---

## Notes

- **Pre-flight pattern**: Other skills can call this at the start to determine routing before spawning agents
- **Progressive enhancement**: If domain-registry is not found, fall back to basic artifact type detection
- **Non-blocking**: Always produces a result, even with low confidence
- **Model-agnostic**: Works in any Claude, Gemini, Codex, or OpenCode context
