# Deep Skills Suite - Comprehensive Guide

A complete reference for the five complementary skills that form a comprehensive codebase analysis and quality framework.

## Table of Contents

- [Overview](#overview)
- [The Five Skills](#the-five-skills)
- [Key Distinctions](#key-distinctions)
- [Decision Matrix](#decision-matrix)
- [Workflow Patterns](#workflow-patterns)
- [Output Format Comparison](#output-format-comparison)
- [Integration Strategies](#integration-strategies)
- [Best Practices](#best-practices)

---

## Overview

The Deep Skills Suite provides five specialized tools for different stages of software development:

| Skill | Purpose | Output Type | Verdict |
|-------|---------|-------------|---------|
| **deep-explorer** | Understand codebase | Insights, patterns | None |
| **deep-review** | Improve quality | Suggestions, alternatives | None |
| **deep-audit** | Check compliance | Violations, remediation | PASS/FAIL |
| **deep-verify** | Assess risks | Risk scenarios, analysis | PASS/FAIL |
| **deep-research** | Research topics | Evidence, sources | None |

**Core principle:** Each skill answers a different question:

- **deep-explorer:** "How does this work?"
- **deep-review:** "How can this be better?"
- **deep-audit:** "Does this meet standards?"
- **deep-verify:** "What could go wrong?"
- **deep-research:** "What should I know?"

---

## The Five Skills

### 1. deep-explorer

**Question:** "How does this work?"

**Purpose:** Understand codebase structure, architecture, patterns, and changes

**When to use:**
- New to a codebase
- Need to understand architecture
- Want to see what changed since last exploration
- Learning how systems interact

**Output:** Architecture insights, patterns, technology stack, workflows

**Key features:**
- Git-based delta tracking
- 5 parallel exploration agents
- Full exploration or delta mode
- Works with uncommitted changes
- Baseline metadata storage

**Example:**
```
User: "I need to understand how the authentication system works"
/deep-explorer

→ Returns: Architecture diagram, flow analysis, pattern identification
```

---

### 2. deep-review

**Question:** "How can this be better?"

**Purpose:** Get actionable suggestions to improve quality (no judgment)

**When to use:**
- After implementing a feature
- Want improvement ideas
- Seeking alternative approaches
- Looking for optimization opportunities

**Output:** Prioritized suggestions, alternatives with trade-offs, positive aspects

**Key features:**
- 4 parallel expert reviewers
- Constructive feedback only
- HIGH/MEDIUM/LOW priorities
- Alternative approaches included
- No pass/fail verdict

**Example:**
```
User: "I implemented OAuth2. Can you review it?"
/deep-review

→ Returns: Improvement suggestions, alternative patterns, performance tips
```

---

### 3. deep-audit

**Question:** "Does this meet standards?"

**Purpose:** Check work against established standards and compliance

**When to use:**
- Pre-deployment compliance check
- Need formal certification
- Regulatory requirements
- Security audits
- Accessibility validation

**Output:** Pass/fail verdict, violation reports, remediation plans

**Key features:**
- 5 parallel specialist auditors
- Formal PASS/FAIL/PASS_WITH_WARNINGS verdicts
- Standards-based (OWASP, WCAG, GDPR, HIPAA, etc.)
- Severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- Blocking violations prevent deployment

**Example:**
```
User: "Audit this code for security and accessibility"
/deep-audit

→ Returns: FAIL verdict, 2 CRITICAL violations, remediation plan
```

---

### 4. deep-verify

**Question:** "What could go wrong?"

**Purpose:** Verify work through multi-dimensional expert analysis with risk assessment

**When to use:**
- After making changes
- Worried about edge cases
- Need risk assessment
- Want expert verification
- Pre-deployment confidence check

**Output:** Risk scenarios, expert analysis, verdict with concerns

**Key features:**
- 3-tier expert system (Invariant + Domain + Dynamic)
- Devil's Advocate counters confirmation bias
- Risk scenario analysis
- Balanced verification
- Domain-agnostic

**Example:**
```
User: "I changed the payment flow. Worried about edge cases."
/deep-verify

→ Returns: Risk scenarios, expert concerns, verification verdict
```

---

### 5. deep-research

**Question:** "What should I know?"

**Purpose:** Comprehensive research on any topic with evidence

**When to use:**
- Learning new technologies
- Researching best practices
- Need evidence-based decisions
- Exploring implementation options
- Due diligence

**Output:** Evidence-based findings, sources, cross-domain insights

**Key features:**
- MCP tool discovery
- Browser automation (Playwright, agent-browser)
- Multi-method research
- Domain-aware effort allocation
- Clickable source URLs

**Example:**
```
User: "Research event sourcing with Kafka for microservices"
/deep-research

→ Returns: Patterns, best practices, trade-offs, source references
```

---

## Key Distinctions

### Verdict vs No Verdict

**With Verdict (Formal Assessment):**
- **deep-audit:** PASS/FAIL/PASS_WITH_WARNINGS - "Does it meet standards?"
- **deep-verify:** PASS/PASS_WITH_CONCERNS/FAIL - "Is it safe to deploy?"

**No Verdict (Guidance):**
- **deep-explorer:** Insights - "Here's how it works"
- **deep-review:** Suggestions - "Here's how to improve"
- **deep-research:** Findings - "Here's what I found"

### Compliance vs Quality

**Compliance (Rules-Based):**
- **deep-audit:** Checks against established standards (OWASP, WCAG, GDPR)
- Violations are objective (either meets standard or doesn't)
- Blocking violations prevent deployment

**Quality (Judgment-Based):**
- **deep-review:** Suggests improvements based on best practices
- Recommendations are subjective (multiple valid approaches)
- Nothing blocks deployment

### Understanding vs Verification

**Understanding:**
- **deep-explorer:** Analyzes existing code to understand it
- **deep-research:** Gathers external information

**Verification:**
- **deep-verify:** Validates your work against risks
- **deep-audit:** Validates your work against standards

---

## Decision Matrix

### By Development Stage

| Stage | Skill | Why |
|-------|-------|-----|
| **Joining project** | deep-explorer | Understand codebase first |
| **Planning feature** | deep-research | Research best practices |
| **After coding** | deep-review | Get improvement ideas |
| **Pre-commit** | deep-audit | Check compliance |
| **Pre-deployment** | deep-verify | Verify no risks |

### By Question Type

| Question | Skill |
|----------|-------|
| "How does X work?" | deep-explorer |
| "What's the best way to do X?" | deep-research |
| "How can I improve this?" | deep-review |
| "Does this meet security standards?" | deep-audit |
| "Will this cause problems?" | deep-verify |

### By Output Needed

| Need | Skill |
|------|-------|
| Architecture diagram | deep-explorer |
| Improvement suggestions | deep-review |
| Compliance report | deep-audit |
| Risk assessment | deep-verify |
| Research findings | deep-research |

### By Formality

| Formality | Skills |
|-----------|--------|
| **Informal guidance** | deep-explorer, deep-review, deep-research |
| **Formal assessment** | deep-audit, deep-verify |

---

## Workflow Patterns

### Pattern 1: New Feature Development

```bash
# 1. Research phase
User: "I need to implement OAuth2 authentication"
/deep-research              # Research best practices

# 2. Understand existing code
User: "How does current auth work?"
/deep-explorer              # Understand existing patterns

# 3. Implement feature
# ... write code ...

# 4. Get improvement feedback
User: "Review my OAuth2 implementation"
/deep-review                # Get suggestions

# 5. Check compliance
/deep-audit                 # Must pass security standards

# 6. Verify safety
/deep-verify                # Verify no risks

# Deploy if audit and verify both pass
```

### Pattern 2: Legacy Codebase Investigation

```bash
# 1. Understand structure
/deep-explorer              # Full exploration

# 2. Research modernization approaches
User: "Research microservices migration patterns"
/deep-research

# 3. Plan changes
# ... design refactoring ...

# 4. After changes, check delta
/deep-explorer              # Delta exploration to see changes

# 5. Get quality feedback
/deep-review                # Suggestions for improvements

# 6. Compliance check
/deep-audit                 # Ensure standards met
```

### Pattern 3: Pre-Deployment Checklist

```bash
# Required before deployment
/deep-audit                 # Must return PASS
/deep-verify                # Must return PASS

# Optional quality improvements
/deep-review                # Implement HIGH priority suggestions

# If audit or verify fail:
# 1. Fix CRITICAL violations
# 2. Re-run audit and verify
# 3. Deploy only when both pass
```

### Pattern 4: Code Review Workflow

```bash
# Before code review
/deep-audit                 # Fix violations before review
/deep-review                # Address HIGH priority items

# During code review
# ... reviewer feedback ...

# After addressing feedback
/deep-verify                # Verify changes work correctly
/deep-audit                 # Ensure still compliant
```

### Pattern 5: Incremental Exploration

```bash
# First session: full exploration
User: "Understand this new codebase"
/deep-explorer              # Full exploration, creates baseline

# Later sessions: delta exploration
# ... make changes ...
/deep-explorer              # Delta mode, shows what changed

# Git tracks: committed + uncommitted + untracked changes
```

---

## Output Format Comparison

### Directory Structure

All skills follow consistent output patterns:

```
.outputs/
├── exploration/
│   ├── 20260130-143000-exploration-report.md
│   ├── 20260130-143000-exploration-report.json
│   └── latest-exploration.md → (symlink)
│
├── review/
│   ├── 20260130-143000-review-report.md
│   ├── 20260130-143000-review-report.json
│   └── latest-review.md → (symlink)
│
├── audit/
│   ├── 20260130-143000-audit-report.md
│   ├── 20260130-143000-audit-report.json
│   └── latest-audit.md → (symlink)
│
├── verification/
│   ├── 20260130-143000-verification-report.md
│   ├── 20260130-143000-verification-report.json
│   └── latest-verification.md → (symlink)
│
└── research/
    ├── 20260130-143000-research-report.md
    ├── 20260130-143000-research-report.json
    └── latest-research.md → (symlink)
```

### Format Validation

Skills with JSON schemas enforce strict format validation:

| Skill | JSON Schema | Validation Gate |
|-------|-------------|-----------------|
| deep-explorer | ✅ | ✅ |
| deep-review | ✅ | ✅ |
| deep-audit | ✅ | ✅ |
| deep-verify | ✅ | ✅ |
| deep-research | ✅ | ✅ |

**Benefits:**
- Consistent enum values (PASS not "Pass" or "PASSED")
- Required fields always present
- Programmatic parsing guaranteed
- Cross-tool compatibility

---

## Integration Strategies

### CI/CD Pipeline Integration

```yaml
# .github/workflows/quality-gate.yml
name: Quality Gate

on: [pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run compliance audit
        run: claude-code /deep-audit
      - name: Check audit passed
        run: |
          VERDICT=$(jq -r '.overall_verdict' .outputs/audit/latest-audit.json)
          if [ "$VERDICT" != "PASS" ]; then
            echo "Audit failed with verdict: $VERDICT"
            exit 1
          fi

  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run verification
        run: claude-code /deep-verify
      - name: Check verification passed
        run: |
          VERDICT=$(jq -r '.overall_verdict' .outputs/verification/latest-verification.json)
          if [ "$VERDICT" == "FAIL" ]; then
            echo "Verification failed"
            exit 1
          fi
```

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running quality checks..."

# Run audit
/deep-audit

# Check result
AUDIT_VERDICT=$(jq -r '.overall_verdict' .outputs/audit/latest-audit.json)

if [ "$AUDIT_VERDICT" == "FAIL" ]; then
  echo "❌ Audit FAILED - fix CRITICAL violations before committing"
  jq -r '.violation_summary.by_severity.critical' .outputs/audit/latest-audit.json
  exit 1
fi

echo "✅ Audit passed"
```

### Automated Documentation

```bash
#!/bin/bash
# scripts/update-architecture-docs.sh

# Explore codebase
/deep-explorer

# Extract insights to docs
jq -r '.architecture_insights' .outputs/exploration/latest-exploration.json > docs/ARCHITECTURE.md

# Commit if changed
git add docs/ARCHITECTURE.md
git commit -m "Update architecture documentation [skip ci]"
```

---

## Best Practices

### 1. Use Skills in Sequence

Don't run all skills at once. Follow logical progression:

```bash
# ❌ Bad: Random order
/deep-verify
/deep-explorer
/deep-research

# ✅ Good: Logical flow
/deep-explorer      # Understand first
/deep-research      # Research options
/deep-review        # Get suggestions
/deep-audit         # Check compliance
/deep-verify        # Verify safety
```

### 2. Address Blocking Issues First

Priority order for fixing issues:

1. **CRITICAL violations** (deep-audit) - Block deployment
2. **FAIL verdict** (deep-verify) - Risk assessment
3. **HIGH priority** (deep-review) - Important improvements
4. **PASS_WITH_WARNINGS** (deep-audit) - Should fix
5. **MEDIUM/LOW** (deep-review) - Nice to have

### 3. Use Delta Exploration Efficiently

```bash
# Full exploration: first time or major changes
/deep-explorer

# Delta exploration: incremental changes
# ... make changes ...
/deep-explorer      # Shows only what changed

# Baseline is stored in report metadata:
# "baseline_commit": "abc123"
# "baseline_timestamp": "2026-01-30T14:30:00Z"
```

### 4. Combine Review and Audit

```bash
# Get suggestions first
/deep-review        # Improvement ideas

# Implement high-priority suggestions
# ... fix code ...

# Then check compliance
/deep-audit         # Formal standards check

# This order ensures you fix quality before compliance
```

### 5. Research Before Implementation

```bash
# ❌ Bad: Implement first, research later
# ... implement OAuth2 ...
/deep-research "OAuth2 best practices"

# ✅ Good: Research first
/deep-research "OAuth2 best practices"
# ... implement based on findings ...
/deep-review        # Verify implementation matches research
```

### 6. Trust the Verdicts

If deep-audit or deep-verify return FAIL:

- ❌ **Don't:** Deploy anyway
- ✅ **Do:** Fix violations, re-run, deploy when passing

### 7. Use Explorer for Onboarding

```bash
# New team member workflow
/deep-explorer              # Understand codebase

# Read the report to learn:
# - Architecture patterns
# - Technology stack
# - Workflow conventions
# - Dependency structure
```

### 8. Automate Compliance Gates

```bash
# In CI/CD, make audit/verify required
- name: Quality Gate
  run: |
    /deep-audit && /deep-verify || exit 1

# In pre-commit hook
/deep-audit || exit 1
```

---

## Common Scenarios

### Scenario: "I Don't Know Where to Start"

```bash
# Step 1: Understand what you have
/deep-explorer

# Step 2: Research what you need
User: "How should I implement feature X?"
/deep-research

# Step 3: Get feedback on your approach
# ... implement ...
/deep-review

# Step 4: Ensure it meets standards
/deep-audit
/deep-verify
```

### Scenario: "Security Audit Required"

```bash
# Run security audit
/deep-audit

# If FAIL:
# 1. Check violation_summary.by_severity.critical
# 2. Read remediation section
# 3. Fix each CRITICAL violation
# 4. Re-run audit
# 5. Repeat until PASS
```

### Scenario: "Code Review Comments"

```bash
# After receiving feedback
/deep-review        # Get additional suggestions

# Compare reviewer comments with deep-review
# Address both sets of feedback

# Verify changes
/deep-verify        # Ensure no new risks

# Check compliance
/deep-audit         # Ensure still meets standards
```

### Scenario: "Major Refactoring"

```bash
# Before refactoring
/deep-explorer      # Creates baseline

# Research patterns
/deep-research "refactoring patterns for [your context]"

# After refactoring
/deep-explorer      # Delta shows changes
/deep-review        # Suggestions for improvements
/deep-audit         # Check still compliant
/deep-verify        # Verify no regressions
```

---

## Troubleshooting

### "Which skill do I use?"

Ask yourself:
- **Understanding?** → deep-explorer
- **Learning?** → deep-research
- **Improving?** → deep-review
- **Compliance?** → deep-audit
- **Safety?** → deep-verify

### "Audit keeps failing"

1. Check severity levels: `jq '.violation_summary.by_severity' latest-audit.json`
2. Fix CRITICAL first
3. Fix HIGH next
4. Re-run after each fix
5. Don't skip violations

### "Too many suggestions from review"

Focus on priorities:
1. Implement HIGH priority
2. Consider MEDIUM if time permits
3. Skip LOW unless easy wins

### "Exploration is too slow"

Use delta mode:
```bash
# First time: full exploration (slower)
/deep-explorer

# Later: delta exploration (faster, shows only changes)
/deep-explorer
```

---

## Summary

### Quick Reference

| Need | Skill | Output |
|------|-------|--------|
| Understand code | deep-explorer | Architecture insights |
| Improve quality | deep-review | Suggestions |
| Check compliance | deep-audit | PASS/FAIL + violations |
| Assess risks | deep-verify | PASS/FAIL + scenarios |
| Research topics | deep-research | Findings + sources |

### Recommended Workflow

```
1. deep-explorer    → Understand
2. deep-research    → Learn
3. [Implementation]
4. deep-review      → Improve
5. deep-audit       → Comply
6. deep-verify      → Verify
7. [Deploy if 5&6 pass]
```

### Key Principles

1. **Sequence matters** - Understand before improving, improve before auditing
2. **Verdicts are gates** - FAIL means don't deploy
3. **Fix blocking issues first** - CRITICAL > HIGH > MEDIUM > LOW
4. **Use delta efficiently** - Full exploration once, delta for changes
5. **Research before implementing** - Learn best practices first

---

## Additional Resources

- **[deep-explorer README](./skills/deep-explorer/README.md)** - Codebase exploration
- **[deep-review README](./skills/deep-review/README.md)** - Quality improvement
- **[deep-audit README](./skills/deep-audit/README.md)** - Compliance auditing
- **[deep-verify README](./skills/deep-verify/README.md)** - Risk verification
- **[deep-research README](./skills/deep-research/README.md)** - Topic research
- **[STANDARDIZATION.md](./STANDARDIZATION.md)** - Output format standards
- **[BROWSER_AUTOMATION.md](./BROWSER_AUTOMATION.md)** - Browser automation guide

---

## License

MIT License - See [LICENSE](./LICENSE) for details.
