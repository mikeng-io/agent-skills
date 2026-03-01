---
name: debate-protocol
description: Generic 5-phase structured debate protocol for multi-agent review. Model-agnostic and domain-agnostic. Can be used standalone or called by deep-council, deep-verify, and any orchestrating skill. Produces verdict with confirmed/withdrawn/disputed/merged/discovered findings.
location: managed
context: fork
allowed-tools:
  - Read
  - Task
  - Write
  - Bash(mkdir *)
---

# Debate Protocol: Generic 5-Phase Multi-Agent Review

Execute this skill to run a structured debate among expert reviewers, producing high-confidence findings through adversarial challenge.

## Execution Instructions

When invoked, accept the following input (from conversation context or caller):

```yaml
debate_input:
  review_id: ""          # Unique ID for this debate session (generate UUID if not provided)
  review_scope: ""       # What is being reviewed (files, topics, description)
  domains: []            # Domains selected (from domain-registry or caller)
  intensity: "standard"  # quick | standard | thorough
  context_summary: ""    # What the conversation/task is about
```

---

## Intensity Modes

```yaml
quick:
  phases: [1, 2, 5]      # Skip challenge and synthesis
  max_rounds: 0
  budget: "reviewer_count + 5 tasks"

standard:
  phases: [1, 2, 3, 4, 5]  # All phases
  max_rounds: 3
  budget: "3 * reviewer_count + 10 tasks"

thorough:
  phases: [1, 2, 3, 4, 5]  # All phases, extended
  max_rounds: 5
  budget: "5 * reviewer_count + 10 tasks"
```

---

## Parameter Presets

```yaml
default:
  da_weight: 0.40           # Devil's Advocate finding weight
  consensus_threshold: 0.50  # Fraction needed for "confirmed"
  security_threshold: 0.67   # Higher bar for security findings

security-elevated:
  da_weight: 0.50
  consensus_threshold: 0.67
  security_threshold: 0.75
```

---

## Phase 1: Independent Investigation (Parallel)

Spawn all reviewers in parallel using Task tool. Each receives the same `review_scope` and `context_summary` but NO communication with other reviewers.

### Reviewer Roster

Always spawn:
- **Devil's Advocate** — pre-mortem failure analysis, cross-domain synthesis
- **Integration Checker** — cross-component impacts, implicit contracts
- **Test Architect** — test coverage gaps, assertion quality

For each selected domain (from `domains` list), spawn the corresponding domain expert from domain-registry.

### Task Prompt Template for Each Reviewer

```
You are a [ROLE] reviewing: [review_scope]

Context: [context_summary]
Domains in scope: [domains]

## Phase 1: Independent Investigation

Analyze independently. Do NOT coordinate with other reviewers.

Focus areas for your role:
[role-specific focus areas from domain-registry]

## Output Format (JSON)

{
  "reviewer": "[role-name]",
  "findings": [
    {
      "id": "F001",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "Short finding title",
      "description": "Detailed description",
      "evidence": "Specific evidence or code reference",
      "remediation": "How to fix",
      "domains": ["domain1"]
    }
  ],
  "phase": 1
}
```

---

## Phase 2: Finding Publication

Collect all Phase 1 findings. As coordinator:

1. Assign unique IDs to all findings (F001, F002, ...)
2. Broadcast complete finding list to all reviewers
3. No responses yet — publication only

Finding inventory at this point:
```yaml
all_findings:
  - id: F001
    origin: devil-advocate
    severity: HIGH
    title: "..."
    ...
```

---

## Phase 3: Challenge Round (standard + thorough only)

Run challenge rounds up to `max_rounds`. Each round:

### Devil's Advocate Obligations

**MUST challenge** every CRITICAL/HIGH finding not originated by DA.
**SHOULD challenge** MEDIUM findings when pattern detected.
**Cross-domain synthesis** — DA discovers new findings from cross-domain patterns.

### Challenge Message Format

Send via Task agent communication (embed in follow-up Task prompts):

```json
{
  "type": "challenge",
  "from": "devil-advocate",
  "to": "target-reviewer",
  "finding_id": "F002",
  "challenge": "This assumes X, but what if Y?",
  "severity_challenge": "MEDIUM not HIGH because..."
}
```

### Response Types

- **defense**: Reviewer defends finding with additional evidence
- **withdrawal**: Reviewer withdraws finding (insufficient evidence)
- **corroboration**: Another reviewer confirms the finding
- **cross-challenge**: Reviewer challenges a different finding
- **discovery**: New finding discovered during debate
- **merge-proposal**: Two similar findings proposed for merging

### Challenge Loop

Repeat for up to `max_rounds` rounds:
1. Spawn DA Task agent with all current findings + challenge obligations
2. Spawn all other reviewers with challenges directed at them
3. Collect responses
4. Update finding states

---

## Phase 4: Synthesis (standard + thorough only)

Identify merge opportunities:
- Findings with >70% description overlap → propose merge
- Merged findings inherit highest severity
- Both origin reviewers must agree to merge

Update finding states:
- `confirmed` — defended and/or corroborated by ≥ consensus_threshold of reviewers
- `withdrawn` — reviewer withdrew after challenge
- `disputed` — challenged but not resolved
- `merged` — two findings consolidated
- `discovered` — emerged during challenge rounds

---

## Phase 5: Final Verdict

All reviewers submit final positions.

### Verdict Logic

```yaml
FAIL:
  - Any CRITICAL confirmed finding
  - 3+ HIGH confirmed findings
  - Any confirmed security finding with domain security-elevated preset

CONCERNS:
  - 1-2 HIGH confirmed findings
  - Multiple MEDIUM confirmed findings
  - Any disputed CRITICAL/HIGH finding

PASS:
  - No confirmed CRITICAL/HIGH findings
  - Only confirmed MEDIUM/LOW/INFO
```

---

## Fallback Mode

If TeamCreate fails (not available in context):
- Spawn independent Task sub-agents (no debate, no cross-challenge)
- Collect findings independently
- Skip Phases 3 and 4
- Run Phase 5 synthesis directly
- Mark output with `"type": "debate-protocol-fallback"`

---

## Artifact Output

Save to `.outputs/debate/{YYYYMMDD-HHMMSS}-debate-{review_id}.md` with YAML frontmatter:

```yaml
---
skill: debate-protocol
version: 2.0
timestamp: {ISO-8601}
artifact_type: debate
domains: [{domain1}, {domain2}]
verdict: PASS | FAIL | CONCERNS
intensity: quick | standard | thorough
review_id: "{unique id}"
context_summary: "{brief description of what was reviewed}"
---
```

Also save JSON companion: `{YYYYMMDD-HHMMSS}-debate-{review_id}.json`

**No symlinks.** To find the latest artifact:
```bash
ls -t .outputs/debate/ | head -1
```

**QMD Integration (optional):**
```bash
qmd collection add .outputs/debate/ --name "debate-artifacts" --mask "**/*.md" 2>/dev/null || true
qmd update 2>/dev/null || true
```
