---
name: debate-protocol
description: Generic 5-phase structured adversarial analysis protocol. Model-agnostic and domain-agnostic. Works for review, audit, research synthesis, planning, creative critique, or any task requiring multi-perspective examination. Can be used standalone or embedded by any orchestrating skill. Produces verdict with confirmed/withdrawn/disputed/merged/discovered findings.
location: managed
context: fork
allowed-tools:
  - Read
  - Task
  - Write
  - Bash(mkdir *)
---

# Debate Protocol: Generic 5-Phase Adversarial Analysis

Execute this skill to run a structured adversarial analysis among domain experts and structural challengers, producing high-confidence findings through iterative challenge and synthesis.

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

Spawn all participants in parallel using Task tool. Each receives the same `scope` and `context_summary` but NO communication with other participants.

### Participant Roster

| Role | Count | Source |
|------|-------|--------|
| Domain expert | One per domain in `debate_input.domains` | domain-registry Lookup Protocol — exact match, adapted match, or session-based virtual expert |
| Devil's Advocate | 1 (always) | `debate-protocol/experts/devils-advocate.md` |
| Integration Checker | 1 (always) | `debate-protocol/experts/integration-checker.md` |

Domain experts are the primary roster. DA and Integration Checker are structural roles that always accompany them.

### Task Prompt Template

```
You are a {expert_role}.

Task: {context_summary}
Scope: {scope}
Domains in scope: {domains}

## Phase 1: Independent Investigation

Analyze independently. Do NOT coordinate with other participants.

Focus areas: {focus_areas}
Standards: {standards}

## Output Format (JSON)

{
  "participant": "{role-name}",
  "findings": [
    {
      "id": "F001",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "Short finding title",
      "description": "Detailed description",
      "evidence": "Specific evidence or reference",
      "recommendation": "What to do about it",
      "domains": ["{domain}"]
    }
  ],
  "phase": 1
}
```

For Devil's Advocate and Integration Checker: apply the role-specific instructions from their expert files.

---

## Phase 2: Finding Publication

Collect all Phase 1 findings. As coordinator:

1. Assign unique IDs to all findings (F001, F002, ...)
2. Broadcast complete finding list to all participants
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
2. Spawn all other participants with challenges directed at them
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

All participants submit final positions.

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
timestamp: {ISO-8601}
artifact_type: debate
domains: [{domain1}, {domain2}]
verdict: PASS | FAIL | CONCERNS
intensity: quick | standard | thorough
review_id: "{unique id}"
context_summary: "{brief description of the task}"
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
