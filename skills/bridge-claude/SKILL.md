---
name: bridge-claude
description: Reference adapter for Claude Code sub-agent dispatch. Read by deep-council via Read tool. Defines how to spawn Claude sub-agents as internal reviewers and collect consolidated findings. NOT invocable standalone — context: reference.
location: managed
context: reference
---

# Bridge: Claude Sub-Agent Adapter

This file is a REFERENCE DOCUMENT. It is read by `deep-council` via the `Read` tool and its instructions are embedded directly into Task agent prompts. Do not invoke it as a standalone skill.

## Bridge Identity

```yaml
bridge: claude
model_family: anthropic/claude
availability: always   # No CLI check needed — Claude is the native executor
connection: task-tool  # Task tool dispatch, no external CLI
```

## Input Format

When deep-council embeds this bridge in a Task agent prompt, it provides:

```json
{
  "bridge_input": {
    "review_id": "...",
    "review_scope": "Files and/or description of what to review",
    "domains": ["domain1", "domain2"],
    "context_summary": "What the conversation/task is about",
    "intensity": "quick | standard | thorough"
  }
}
```

## Execution Instructions

The Claude bridge executor (a Task sub-agent) follows these steps:

### Step 1: Spawn Domain Expert Sub-Agents in Parallel

For each domain in `bridge_input.domains`, spawn a Task sub-agent using the corresponding `expert_role` from domain-registry.

Always additionally spawn:
- **Devil's Advocate sub-agent**
- **Integration Checker sub-agent**

All sub-agents run in parallel via the Task tool.

### Step 2: Domain Expert Task Prompt Template

```
You are a {expert_role} reviewing: {review_scope}

Context: {context_summary}
Intensity: {intensity}

## Your Focus Areas
{focus_areas from domain-registry for this domain}

## Relevant Standards
{standards from domain-registry for this domain}

## Your Task

Perform a thorough {intensity} review focused on your domain.

1. Read any files mentioned in the scope
2. Analyze for issues relevant to your domain
3. Apply the standards listed above
4. Classify each finding by severity: CRITICAL | HIGH | MEDIUM | LOW | INFO

## Output Format (JSON)

{
  "reviewer": "{expert_role}",
  "domain": "{domain}",
  "bridge": "claude",
  "findings": [
    {
      "id": "",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "Short finding title",
      "description": "Detailed description",
      "evidence": "Specific reference or code location",
      "remediation": "How to fix"
    }
  ],
  "overall_assessment": "Brief summary",
  "confidence": "high | medium | low"
}
```

### Step 3: Devil's Advocate Task Prompt

```
You are a Devil's Advocate reviewer. Your job is to challenge assumptions
and find failure modes.

Reviewing: {review_scope}
Context: {context_summary}
Intensity: {intensity}

## Your Focus
- Pre-mortem analysis: What could go wrong?
- Assumptions: What is taken for granted that might be wrong?
- Edge cases: What unusual but valid scenarios are unhandled?
- Cross-domain risks: What issues arise from combining multiple concerns?

## Output Format (JSON)
{same structure as domain expert, domain: "cross-domain"}
```

### Step 4: Integration Checker Task Prompt

```
You are an Integration Checker. Your job is to find cross-component issues.

Reviewing: {review_scope}
Context: {context_summary}

## Your Focus
- Interface mismatches between components
- Implicit contracts that aren't documented
- Missing error propagation across boundaries
- Timing and ordering dependencies

## Output Format (JSON)
{same structure as domain expert, domain: "integration"}
```

### Step 5: Collect and Aggregate

After all sub-agents complete:
1. Assign unique finding IDs (F001, F002, ...)
2. Deduplicate near-identical findings (keep highest severity)
3. Apply severity classification consistency check
4. Calculate overall bridge verdict

### Step 6: Severity Classification

```yaml
CRITICAL: Security vulnerabilities, data loss risks, system-breaking issues
HIGH:     Significant quality issues, performance blockers, important gaps
MEDIUM:   Moderate issues, best practice violations, maintainability concerns
LOW:      Minor improvements, style issues, nice-to-have changes
INFO:     Observations, context, non-actionable notes
```

## Output Format

```json
{
  "bridge": "claude",
  "model_family": "anthropic/claude",
  "review_id": "...",
  "domains_covered": ["domain1", "domain2", "cross-domain", "integration"],
  "findings": [
    {
      "id": "F001",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "...",
      "description": "...",
      "evidence": "...",
      "remediation": "...",
      "domain": "...",
      "reviewer": "..."
    }
  ],
  "verdict": "PASS | FAIL | CONCERNS",
  "agents_spawned": 4,
  "confidence": "high"
}
```

### Verdict Logic

```yaml
FAIL:     Any CRITICAL finding
CONCERNS: 1+ HIGH findings, or 3+ MEDIUM findings
PASS:     No CRITICAL/HIGH, only MEDIUM/LOW/INFO
```

## Notes

- Claude bridge is always available — no CLI check needed
- Uses Task tool for sub-agent dispatch (not Bash)
- All sub-agents read files directly with Read tool
- Parallel execution for all domain experts + DA + Integration Checker
- Bridge is never blocking — always returns a report
