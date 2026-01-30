# Deep Audit

Multi-agent standards and compliance auditing framework with formal pass/fail verdicts.

## Overview

Deep Audit checks your work against established standards and compliance requirements, providing formal pass/fail verdicts with detailed violation reports.

**Philosophy:** Formal compliance checking, not suggestions.

## Key Features

- **Parallel Auditor Execution:** 5 specialist auditors run simultaneously
- **Formal Verdicts:** PASS, PASS_WITH_WARNINGS, or FAIL
- **Standards-Based:** Checks against OWASP, WCAG, GDPR, PEP8, etc.
- **Violation Reports:** Detailed findings with remediation steps
- **Compliance Tracking:** Regulatory and legal requirement checking
- **Severity Levels:** CRITICAL, HIGH, MEDIUM, LOW
- **Blocking Issues:** CRITICAL violations prevent deployment

## Quick Start

```bash
# Install the skill
cp -r skills/deep-audit ~/.claude/skills/

# Run compliance audit
User: "Audit this code for security and accessibility"
/deep-audit

# → Generates formal audit report with pass/fail verdict
```

## The Five Auditors

### 1. Security Auditor (30%)
**Checks:** OWASP Top 10, CWE, security vulnerabilities

**Standards:**
- SQL injection (OWASP A03)
- XSS vulnerabilities (OWASP A03)
- Authentication/authorization
- Input validation
- Data encryption
- Secrets management

**Verdict Criteria:**
- FAIL: Any CRITICAL vulnerability
- PASS: No CRITICAL/HIGH vulnerabilities

### 2. Accessibility Auditor (25%)
**Checks:** WCAG 2.1 compliance (A, AA, AAA)

**Standards:**
- Semantic HTML
- ARIA attributes
- Keyboard navigation
- Screen reader compatibility
- Color contrast ratios
- Focus management

**Verdict Criteria:**
- FAIL: Any WCAG Level A violation
- PASS: Meets WCAG 2.1 Level AA

### 3. Code Standards Auditor (20%)
**Checks:** Language-specific standards and linting rules

**Standards:**
- PEP8 (Python)
- ESLint rules (JavaScript/TypeScript)
- Google Style Guide
- Prettier formatting
- Test coverage thresholds
- Documentation requirements

**Verdict Criteria:**
- FAIL: <80% test coverage (if required)
- PASS: All linting rules pass

### 4. Regulatory Auditor (15%)
**Checks:** Legal and regulatory compliance

**Standards:**
- GDPR (data privacy)
- HIPAA (healthcare)
- SOC2 (security controls)
- PCI-DSS (payment cards)
- COPPA (children's privacy)

**Verdict Criteria:**
- FAIL: Any regulatory violation
- PASS: All applicable regulations met

### 5. Performance Auditor (10%)
**Checks:** Performance benchmarks and SLAs

**Standards:**
- Core Web Vitals (LCP, FID, CLS)
- API response times
- Database query performance
- Load time requirements
- Resource usage limits

**Verdict Criteria:**
- FAIL: Critical performance regression
- PASS: Meets all SLA targets

## Verdict Levels

### ❌ FAIL
**Criteria:**
- Any CRITICAL violation
- 3+ HIGH severity violations
- Any regulatory violation

**Action:** Must fix before deployment

### ⚠️  PASS_WITH_WARNINGS
**Criteria:**
- 1-2 HIGH severity violations
- Multiple MEDIUM violations

**Action:** Should fix this sprint

### ✅ PASS
**Criteria:**
- No CRITICAL or HIGH violations
- Only MEDIUM/LOW violations

**Action:** Can deploy, fix warnings when convenient

## Severity Levels

### CRITICAL (Blocks Deployment)
- Security vulnerabilities (SQL injection, XSS)
- WCAG Level A violations
- Regulatory violations
- Critical performance failures

### HIGH (Should Fix)
- WCAG Level AA violations
- Code standard violations
- Performance SLA misses
- Missing security controls

### MEDIUM (Recommended Fix)
- Code style violations
- Minor performance issues
- WCAG AAA violations
- Documentation gaps

### LOW (Nice to Fix)
- Style preferences
- Optional optimizations
- Nice-to-have improvements

## Use Cases

### Security Audit
```
Scenario: Pre-deployment security check
Action: /deep-audit
Result: OWASP Top 10 compliance check
  ✅ No SQL injection
  ✅ No XSS vulnerabilities
  ❌ CRITICAL: Exposed API keys
  Verdict: FAIL
```

### Accessibility Audit
```
Scenario: WCAG 2.1 AA compliance check
Action: /deep-audit
Result: Accessibility compliance report
  ✅ Semantic HTML
  ❌ HIGH: Missing alt text on images
  ⚠️  MEDIUM: Color contrast too low
  Verdict: PASS_WITH_WARNINGS
```

### Regulatory Audit
```
Scenario: GDPR compliance verification
Action: /deep-audit
Result: Regulatory compliance check
  ✅ Consent mechanism implemented
  ✅ Data encryption at rest
  ❌ CRITICAL: Missing data deletion API
  Verdict: FAIL
```

### Code Standards Audit
```
Scenario: Pre-merge linting check
Action: /deep-audit
Result: Code standards compliance
  ✅ ESLint rules pass
  ✅ Test coverage 85% (>80% required)
  ⚠️  MEDIUM: 5 missing docstrings
  Verdict: PASS_WITH_WARNINGS
```

## Example Audit Report

```markdown
# Deep Audit Report

## Overall Verdict: FAIL

**Audit Score:** 72/100

**Summary:**
- ❌ 2 CRITICAL violations → BLOCKS DEPLOYMENT
- ⚠️  3 HIGH violations → SHOULD FIX
- ⚠️  8 MEDIUM violations → RECOMMENDED FIX
- ℹ️  15 LOW violations → NICE TO FIX

**Blocking Issues:** 2 violations prevent passing

## Audit Summary

| Auditor | Verdict | Critical | High | Medium | Low | Score |
|---------|---------|----------|------|--------|-----|-------|
| Security | FAIL | 1 | 1 | 2 | 3 | 65/100 |
| Accessibility | FAIL | 1 | 2 | 4 | 8 | 68/100 |
| Code Standards | PASS | 0 | 0 | 2 | 4 | 92/100 |
| Regulatory | PASS | 0 | 0 | 0 | 0 | 100/100 |
| Performance | PASS | 0 | 0 | 0 | 0 | 95/100 |

## Critical Violations (Must Fix)

### ❌ Security: SQL Injection Vulnerability

**Severity:** CRITICAL
**Standard:** OWASP A03:2021 - Injection
**Auditor:** Security Auditor

**Violation:**
User input directly concatenated into SQL query without parameterization

**Location:**
`src/api/users.ts:45`

**Evidence:**
```typescript
const query = `SELECT * FROM users WHERE id = ${userId}`;
```

**Impact:**
Allows attackers to execute arbitrary SQL commands

**Remediation:**
```typescript
const query = `SELECT * FROM users WHERE id = ?`;
db.execute(query, [userId]);
```

### ❌ Accessibility: Missing Alt Text

**Severity:** CRITICAL
**Standard:** WCAG 2.1.1 (Level A)
**Auditor:** Accessibility Auditor

**Violation:**
Images missing alt attributes

**Location:**
`src/components/Gallery.tsx:23`

**Evidence:**
```tsx
<img src={photo.url} />
```

**Remediation:**
```tsx
<img src={photo.url} alt={photo.description} />
```

## Remediation Plan

**Immediate (CRITICAL - Must fix before deployment):**
- [ ] Fix SQL injection in src/api/users.ts
- [ ] Add alt text to all images

**Short Term (HIGH - Should fix this sprint):**
- [ ] Implement HTTPS redirect
- [ ] Add keyboard navigation
- [ ] Fix color contrast issues

**Estimated Effort:** 8-12 hours for CRITICAL fixes

## Re-Audit Recommendation

**Re-audit required after fixing:**
- All CRITICAL violations
- All HIGH violations (recommended)
```

## Standards Checked

### Security
- OWASP Top 10 (2021)
- CWE (Common Weakness Enumeration)
- SANS Top 25
- Security best practices

### Accessibility
- WCAG 2.1 Level A (minimum)
- WCAG 2.1 Level AA (target)
- WCAG 2.1 Level AAA (optional)
- ARIA Authoring Practices

### Code Standards
- Language-specific (PEP8, PSR, etc.)
- Framework conventions
- Linting rules (ESLint, Pylint, RuboCop)
- Formatting (Prettier, Black, Gofmt)
- Test coverage thresholds

### Regulatory
- GDPR (EU data privacy)
- HIPAA (US healthcare)
- SOC2 (security controls)
- PCI-DSS (payment cards)
- COPPA (children's privacy)
- CCPA (California privacy)

### Performance
- Core Web Vitals
- Response time SLAs
- Database query benchmarks
- Load time requirements
- Resource usage limits

## Output Format

```
.outputs/audit/
├── 20260130-143000-audit-report.md
├── 20260130-143000-audit-report.json
├── latest-audit.md → (symlink)
└── latest-audit.json → (symlink)
```

## When to Use Deep Audit

**Use when:**
- ✅ Need formal compliance verification
- ✅ Pre-deployment security check
- ✅ Regulatory audit required
- ✅ Standards conformance needed
- ✅ Want pass/fail verdict

**Don't use when:**
- ❌ Want improvement suggestions (use deep-review)
- ❌ Want risk assessment (use deep-verify)
- ❌ Want codebase exploration (use deep-explorer)

## Configuration (Optional)

```yaml
# .outputs/audit/config.yaml

audit:
  weights:
    security: 0.30
    accessibility: 0.25
    code_standards: 0.20
    regulatory: 0.15
    performance: 0.10

  fail_on:
    critical: 1    # Fail if any CRITICAL
    high: 3        # Fail if 3+ HIGH

  standards:
    accessibility: ["WCAG 2.1 AA"]
    security: ["OWASP Top 10"]
    regulatory: ["GDPR", "HIPAA"]
```

## Benefits

### Formal Compliance
- Official pass/fail verdicts
- Standards-based checking
- Regulatory compliance tracking

### Detailed Reports
- Specific violations with locations
- Evidence and remediation steps
- Resource links for each violation

### Risk Mitigation
- Catches critical issues before deployment
- Regulatory violation prevention
- Security vulnerability detection

### Actionable
- Clear remediation plans
- Prioritized by severity
- Estimated effort included

## Best Practices

### When to Run
- ✅ Before every deployment
- ✅ After major changes
- ✅ Quarterly compliance checks
- ✅ Pre-release audits

### How to Handle Results
1. **FAIL:** Fix all CRITICAL before deploying
2. **PASS_WITH_WARNINGS:** Fix HIGH this sprint
3. **PASS:** Address MEDIUM/LOW when convenient
4. **Re-audit:** After fixing violations

## Documentation

- **[SKILL.md](./SKILL.md)** - Technical implementation
- **[schemas/](./schemas/)** - Output format specifications
- **[examples/](./examples/)** - Example audit reports

## License

MIT License - See repository LICENSE for details.
