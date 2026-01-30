# Deep Review

Multi-agent quality improvement framework with constructive feedback.

## Overview

Deep Review provides actionable suggestions to improve your work through balanced expert analysis. Instead of pass/fail verdicts, it focuses on "how can this be better?"

**Philosophy:** Constructive improvement, not criticism.

## Key Features

- **Parallel Expert Reviews:** 4 specialized reviewers run simultaneously
- **Constructive Feedback:** Focused on improvement, not judgment
- **Actionable Suggestions:** Specific improvements you can implement
- **Balanced Perspective:** Includes what's good, not just what needs work
- **Domain-Agnostic:** Works for code, design, content, architecture, etc.
- **Prioritized:** High/Medium/Low priority for easy action planning
- **No Verdict:** Improvement suggestions only, no pass/fail

## Quick Start

```bash
# Install the skill
cp -r skills/deep-review ~/.claude/skills/

# Get review feedback
User: "I implemented OAuth2 authentication. Can you review it?"
/deep-review

# → Generates comprehensive review with improvement suggestions
```

## The Four Reviewers

### 1. Best Practices Expert (35%)
**Focus:** Industry standards and conventions

**Suggests:**
- Framework/language best practices
- Design principles (SOLID, DRY, KISS)
- Security standards
- Testing approaches
- Documentation practices

**Example:** "Consider using the Strategy pattern here instead of switch statements for better extensibility."

### 2. Code Quality Reviewer (30%)
**Focus:** Readability and maintainability

**Suggests:**
- Clearer naming
- Better code organization
- Improved documentation
- Reduced complexity
- DRY violations to fix

**Example:** "Extract this 50-line function into smaller, single-purpose functions for better readability."

### 3. Alternative Approaches Expert (20%)
**Focus:** Different solutions with trade-offs

**Suggests:**
- Different design patterns
- Alternative architectures
- Simpler solutions
- Different technology choices
- Pros/cons of each approach

**Example:** "Consider using Redis for caching instead of in-memory. Pros: Persistence, scalability. Cons: Network overhead, complexity."

### 4. Performance Optimizer (15%)
**Focus:** Speed and efficiency improvements

**Suggests:**
- Algorithm optimizations
- Database query improvements
- Caching opportunities
- Resource optimization
- Scalability enhancements

**Example:** "Replace this O(n²) nested loop with a hash map lookup for O(n) complexity."

## Use Cases

### Code Review
```
Scenario: Completed feature implementation
Action: /deep-review
Result: Suggestions for:
  - Best practices violations
  - Code quality improvements
  - Alternative approaches
  - Performance optimizations
```

### Design Review
```
Scenario: Created UI mockups
Action: /deep-review
Result: Suggestions for:
  - Design best practices
  - Accessibility improvements
  - Alternative layouts
  - Performance considerations
```

### Architecture Review
```
Scenario: Designed new microservice
Action: /deep-review
Result: Suggestions for:
  - Architecture patterns
  - Better separation of concerns
  - Alternative architectures
  - Scalability improvements
```

### Content Review
```
Scenario: Wrote documentation
Action: /deep-review
Result: Suggestions for:
  - Writing best practices
  - Clarity improvements
  - Alternative structures
  - Better examples
```

## Example Review Output

```markdown
# Deep Review Report

## Executive Summary

The OAuth2 implementation is functional and follows many best practices.
Key opportunities: improve error handling, add input validation, and
consider rate limiting for production.

**Overall Assessment:** Good with room for improvement

**Top 3 Recommendations:**
1. Add comprehensive input validation (HIGH priority)
2. Implement rate limiting for auth endpoints (HIGH priority)
3. Extract token validation into separate service (MEDIUM priority)

## High Priority Suggestions

### Security: Add Input Validation

**Suggested by:** Best Practices Expert, Code Quality Reviewer

**Current Approach:**
Directly using request parameters without validation

**Suggestion:**
Add schema validation using a library like Joi or Yup

**Rationale:**
Prevents injection attacks and ensures data integrity

**Example:**
```javascript
// Before
const { username, password } = req.body;

// After
const schema = Joi.object({
  username: Joi.string().alphanum().min(3).max(30).required(),
  password: Joi.string().min(8).required()
});
const { username, password } = await schema.validateAsync(req.body);
```

**Impact:** Significantly improves security and data quality

---

## Alternative Approaches

### Alternative 1: Use Passport.js Library

**Pros:**
- Battle-tested OAuth2 implementation
- Handles edge cases
- Active community

**Cons:**
- Additional dependency
- Learning curve
- Less control

**When to Use:** For standard OAuth2 flows without custom requirements

## Performance Optimization Opportunities

### Optimization: Cache Token Validation

**Current Performance:** Every request validates token with database query

**Suggestion:** Use Redis to cache valid tokens for 5 minutes

**Expected Improvement:** 10x faster token validation, reduced DB load

**Trade-offs:** Need to handle cache invalidation on logout

## Positive Aspects

**What's Already Good:**
- Clean separation of concerns
- Comprehensive error handling
- Well-documented functions
- Good test coverage

## Next Steps

**Immediate (High Priority):**
- [ ] Add input validation with Joi
- [ ] Implement rate limiting

**Short Term (Medium Priority):**
- [ ] Extract token validation service
- [ ] Add more integration tests

**Long Term (Low Priority):**
- [ ] Consider migrating to Passport.js
- [ ] Add caching layer
```

## Review Categories

### Best Practices
- Industry standards
- Framework conventions
- Design principles
- Security practices
- Testing approaches

### Code Quality
- Readability
- Maintainability
- Organization
- Documentation
- Complexity

### Alternatives
- Design patterns
- Architectures
- Technologies
- Simpler solutions
- Trade-off analysis

### Performance
- Algorithm efficiency
- Database optimization
- Caching strategies
- Resource utilization
- Scalability

## Priority Levels

### HIGH Priority
- Security issues
- Critical best practice violations
- Major code quality problems
- Significant performance bottlenecks

### MEDIUM Priority
- Maintainability improvements
- Alternative approaches to consider
- Moderate performance gains
- Better organization

### LOW Priority
- Nice-to-have improvements
- Minor optimizations
- Style preferences
- Future considerations

## Output Format

```
.outputs/review/
├── 20260130-143000-review-report.md
├── 20260130-143000-review-report.json
├── latest-review.md → (symlink)
└── latest-review.json → (symlink)
```

## When to Use Deep Review

**Use when:**
- ✅ You want constructive feedback
- ✅ You want to improve quality
- ✅ You're open to alternatives
- ✅ You want actionable suggestions
- ✅ You need prioritized improvements

**Don't use when:**
- ❌ You want pass/fail verdict (use deep-verify)
- ❌ You want compliance checking (use deep-audit)
- ❌ You want codebase exploration (use deep-explorer)

## Configuration (Optional)

```yaml
# .outputs/review/config.yaml

review:
  weights:
    best_practices: 0.35
    code_quality: 0.30
    alternatives: 0.20
    performance: 0.15

  include_code_examples: true
  include_resources: true
  max_suggestions_per_category: 10
```

## Benefits

### Constructive
- Focus on improvement, not criticism
- Balanced perspective (positive + suggestions)
- Actionable recommendations

### Comprehensive
- Multiple expert perspectives
- Covers best practices, quality, alternatives, performance
- Prioritized for easy action planning

### Efficient
- Parallel reviewer execution
- Fast comprehensive analysis
- Domain-agnostic

### Actionable
- Specific suggestions with examples
- Before/after code samples
- Clear next steps

## Best Practices

### When to Run
- ✅ After completing features
- ✅ Before code review
- ✅ During design iterations
- ✅ When seeking improvement ideas

### How to Use Feedback
1. **Start with HIGH priority** - Address security and critical issues first
2. **Consider MEDIUM priority** - Improve maintainability and architecture
3. **Evaluate LOW priority** - Nice-to-haves when you have time
4. **Review alternatives** - Understand trade-offs before changing approach
5. **Maintain positives** - Don't lose what's already good

## Documentation

- **[SKILL.md](./SKILL.md)** - Technical implementation
- **[schemas/](./schemas/)** - Output format specifications
- **[examples/](./examples/)** - Example review reports

## License

MIT License - See repository LICENSE for details.
