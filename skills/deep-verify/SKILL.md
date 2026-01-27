---
name: deep-verify
description: Generic multi-agent verification framework with balanced expert analysis. Model-agnostic and domain-agnostic - verify any work through expert analysis.
location: managed
context: fork
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(git *)
  - Bash(ls *)
  - Task
---

# Deep Verify: Multi-Agent Verification Framework

Execute this skill to verify work through balanced expert analysis.

## Execution Instructions

When invoked, you will:

1. **Analyze the conversation context** to extract:
   - Files and artifacts mentioned
   - Topics discussed
   - Concerns raised
   - User's intent

2. **Generate expert agents** based on the extracted context:
   - Always spawn: Devil's Advocate, Integration Checker, Third-Party Reviewer
   - Dynamically spawn domain experts based on what was discussed

3. **Aggregate findings** from all experts with proper weighting

4. **Generate and save report** to `.outputs/verification/`

---

## Step 1: Analyze Conversation

Analyze the recent conversation to extract:

```yaml
conversation_analysis:
  files: []        # File paths mentioned (e.g., "src/auth.go")
  artifacts: []    # Other artifacts (e.g., "designs/mockup.fig")
  topics: []       # Key topics discussed (e.g., "OAuth2", "authentication")
  concerns: []     # What user is worried about (e.g., "token security")
  intent: ""       # What user is doing (e.g., "implementation", "design")
  domain_inference: []  # Domains detected from context
```

**Infer domains from:**
- Topics mentioned (e.g., "authentication" → Security)
- Artifacts referenced (e.g., "Figma" → Design)
- Concerns expressed (e.g., "GDPR" → Compliance)
- Language patterns used

**Examples for domain inference (NOT exhaustive):**
- Technical terms suggest technical domains
- Creative language suggests design/marketing domains
- Business language suggests business/finance domains
- Legal language suggests compliance/legal domains
- Any domain can be detected - analyze the conversation naturally

---

## Step 2: Spawn Expert Agents

Spawn experts in parallel using the Task tool. Always spawn the invariant experts, then spawn domain experts based on conversation analysis.

### Invariant Experts (Always Spawn)

#### Expert 1: Devil's Advocate
```
Weight: 40%
Purpose: Counter confirmation bias through pre-mortem analysis
Capability: highest

Use this prompt:

You are the DEVIL'S ADVOCATE. Your role is to BALANCE the verification by actively seeking what could go wrong, what we're not seeing, and what assumptions might be false.

## Your Mindset: Pre-Mortem
Imagine this work has already caused a failure 6 months from now. Work backwards: What went wrong? What did we miss?

## Focus Areas
- Hidden Assumptions: What are we assuming that might not be true?
- Failure Modes: If this fails, what happens? Who is affected?
- Silent Failures: Could this fail without anyone noticing?
- Edge Cases: What edge cases might we have missed?
- Rollback Reality: Can we undo this? How difficult?
- Negative Impacts: What does this break that we're not seeing?

## Context to Analyze
{conversation_context}

## Your Scope
{scope_description}

## Output Format (JSON)
{
  "agent": "devils-advocate",
  "pre_mortem_scenarios": [
    {
      "scenario": "What went wrong",
      "likelihood": "LOW | MEDIUM | HIGH",
      "impact": "LOW | MEDIUM | HIGH | CRITICAL",
      "evidence": "What suggests this could happen",
      "mitigation": "How to prevent (if anything)"
    }
  ],
  "hidden_assumptions": [
    {
      "assumption": "What we're assuming",
      "risk_if_false": "What happens if wrong"
    }
  ]
}
```

#### Expert 2: Integration Checker
```
Weight: 15%
Purpose: Assess system-wide impact
Capability: high

Use this prompt:

You are the INTEGRATION CHECKER. Your role is to assess the system-wide impact of the proposed changes.

## Focus Areas
- What other components/systems are affected?
- What coordination is needed?
- What dependencies exist?
- What could break elsewhere?

## Context
{conversation_context}

## Output Format (JSON)
{
  "agent": "integration",
  "affected_components": ["list of affected areas"],
  "dependencies": ["list of dependencies"],
  "coordination_required": ["what needs to be coordinated"],
  "risks": [{"area": "affected area", "risk": "description"}]
}
```

#### Expert 3: Third-Party Reviewer
```
Weight: 5%
Purpose: Fresh-eyes perspective
Capability: standard

Use this prompt:

You are a THIRD-PARTY REVIEWER seeing this for the first time. Provide fresh, unbiased feedback.

## Focus Areas
- Is the intent clear?
- Are there obvious gaps or confusion?
- What questions would a newcomer ask?

## Context
{conversation_context}

## Output Format (JSON)
{
  "agent": "third-party",
  "clarity_score": "HIGH | MEDIUM | LOW",
  "questions": ["questions a newcomer would ask"],
  "suggestions": ["constructive suggestions"]
}
```

### Domain Experts (Spawn Based on Conversation)

For each domain detected in the conversation, generate a domain expert prompt:

```
Weight: 40% (shared across all domain experts)
Capability: high

Prompt Template:

You are a {DOMAIN} expert. Analyze the following work from a {DOMAIN} perspective.

## Context
{conversation_context}

## Your Focus
Identify issues, risks, and improvements specific to {DOMAIN}.

## Output Format (JSON)
{
  "agent": "{domain}",
  "findings": [
    {
      "severity": "CRITICAL | HIGH | MEDIUM | LOW",
      "description": "Issue or observation",
      "evidence": "Reference to specific content",
      "fix": "Recommendation if applicable"
    }
  ]
}
```

**Spawn domain experts for each unique domain detected.** Examples:
- "authentication" discussed → Spawn Security Expert
- "Figma design" mentioned → Spawn Design Expert
- "email campaign" discussed → Spawn Marketing Expert
- "policy update" discussed → Spawn HR/Legal Expert

Any domain can be detected - analyze the conversation and spawn appropriate experts.

---

## Step 3: Aggregate Findings

After all experts complete, aggregate their findings:

### Determine Verdict
- **FAIL**: Critical risks or blocking issues found
- **PASS_WITH_CONCERNS**: High risks identified
- **PASS**: No significant issues

### Build Summary Table
| Dimension | Result |
|-----------|--------|
| Domain Correctness | ✅ PASS / ⚠️ CONCERNS |
| Risk Assessment | Based on Devil's Advocate findings |
| Integration Impact | Based on Integration Checker findings |

---

## Step 4: Generate Report

Generate a markdown report with this structure:

```markdown
# Deep Verify Report

**Verdict:** {PASS | PASS_WITH_CONCERNS | FAIL}
**Generated:** {timestamp}
**Domains Analyzed:** {list of domains}
**Experts Consulted:** {count} experts

## Summary

| Dimension | Result |
|-----------|--------|
| Domain Correctness | {result} |
| Risk Assessment | {result} |
| Integration Impact | {result} |

---

## Risk Assessment (Devil's Advocate)

### {IMPACT} Risk: {scenario}

**Pre-mortem:** {failure scenario}
**Likelihood:** {likelihood}
**Impact:** {impact}
**Evidence:** {evidence}
**Mitigation:** {mitigation}

{repeat for each scenario}

---

## Domain Expert Findings

### {Domain Name}

{findings from domain expert}

{repeat for each domain}

---

## Integration Impact

**Affected:** {affected components}
**Dependencies:** {dependencies}
**Coordination:** {coordination needed}

---

## Third-Party Perspective

**Clarity:** {clarity score}
**Questions:** {questions raised}
**Suggestions:** {suggestions}
```

---

## Step 5: Save Report

Save the report to:

1. Create directory: `.outputs/verification/`
2. Save with timestamp: `YYYYMMDD-HHMMSS-verification-report.md`
3. Save JSON version: `YYYYMMDD-HHMMSS-verification-report.json`
4. Update symlink: `latest-report.md` → most recent report

---

## Configuration (Optional)

The system uses these defaults unless overridden:

**Expert Weights:**
- Devil's Advocate: 40%
- Integration Checker: 15%
- Third-Party Reviewer: 5%
- Domain Experts: 40% (shared pool)

**Output Directory:** `.outputs/verification/`

These can be overridden via:
- Environment variables (e.g., `DEEP_VERIFY_OUTPUT_DIR`)
- Config files in `.outputs/verification/config.yaml`
- Command-line arguments

---

## Notes

- **Model-agnostic**: Uses capability levels ("highest", "high", "standard") not specific model names
- **Domain-agnostic**: Works for any domain detected in conversation
- **Conversation-driven**: All context extracted from what was discussed
- **No triggers/keywords**: Analyzes conversation naturally, doesn't match patterns
- **Balanced**: Devil's Advocate weight equals all domain experts combined to counter confirmation bias
