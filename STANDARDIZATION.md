# Output Format Standardization

## Summary

Implemented strict output format validation for both `deep-verify` and `deep-research` skills to eliminate chaotic format variations and ensure consistent, predictable outputs.

## Implementation Date

January 30, 2026

## Problem Statement

Both skills were generating verification and research files in varying formats across different executions:

**Before Standardization:**
- Verdict could be: "PASS", "Pass", "PASSED", "OK", "GOOD", "Looking good", etc.
- Impact could be: "High", "HIGH", "high", "Major", "Severe", "Critical", etc.
- Consensus could be: "Strong", "STRONG", "Mostly agree", "Generally accepted", etc.
- Sections could be missing, renamed, or reordered
- Reports were unpredictable and difficult to parse programmatically

This created **chaos** and made automated processing impossible.

## Solution Architecture

### Two-Part Solution

1. **Formal JSON Schemas**
   - Defined exact structure for verification and research reports
   - Specified all required fields and types
   - Enforced standardized enum values
   - Created validation-ready specifications

2. **Validation Gates**
   - Added sub-agent validators to both skills
   - Validates outputs before finalization
   - Blocks completion on critical format violations
   - Provides clear error messages and suggestions

## Implementation Details

### Deep Verify

**Files Created:**
- `skills/deep-verify/schemas/verification-report-schema.json` - JSON Schema specification
- `skills/deep-verify/schemas/README.md` - Schema documentation
- `skills/deep-verify/validators/output-validator.md` - Validation logic and sub-agent prompt

**Changes to SKILL.md:**
- Added Step 5: "Validate Output Format"
- Renumbered Step 5 "Save Report" to Step 6
- Added validation gate sub-agent invocation
- Defined failure handling procedures

**Validation Criteria:**
- Verdict must be exactly: `PASS`, `PASS_WITH_CONCERNS`, or `FAIL`
- Impact levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- Severity levels: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
- Likelihood levels: `LOW`, `MEDIUM`, `HIGH`
- All required sections must be present
- JSON and markdown must be consistent

### Deep Research

**Files Created:**
- `skills/deep-research/schemas/research-report-schema.json` - JSON Schema specification
- `skills/deep-research/schemas/README.md` - Schema documentation
- `skills/deep-research/validators/output-validator.md` - Validation logic and sub-agent prompt

**Changes to SKILL.md:**
- Added Step 7: "Validate Output Format"
- Renumbered Step 7 "Save Report" to Step 8
- Added validation gate sub-agent invocation
- Defined failure handling procedures

**Validation Criteria:**
- Validation status: `VALIDATED`, `PARTIAL`, `PRELIMINARY`
- Research depth: `BRIEF`, `STANDARD`, `COMPREHENSIVE`
- Consensus levels: `STRONG`, `MODERATE`, `WEAK`, `DEBATE`
- Source credibility: `HIGH`, `MEDIUM`, `LOW`
- Source types: `academic`, `industry`, `blog`, `documentation`, `other`
- Minimum 3 sources required
- Source quality thresholds enforced (FAIL if >70% LOW credibility)
- All required sections must be present
- JSON and markdown must be consistent

## Results

**After Standardization:**
- ✅ Verdict is exactly "PASS", "PASS_WITH_CONCERNS", or "FAIL"
- ✅ Impact is exactly "LOW", "MEDIUM", "HIGH", or "CRITICAL"
- ✅ Consensus is exactly "STRONG", "MODERATE", "WEAK", or "DEBATE"
- ✅ All sections consistently present
- ✅ Reports have identical structure every time
- ✅ Easy to parse programmatically
- ✅ Source quality thresholds enforced
- ✅ Format violations caught before completion

## Validation Flow

```
Generate Report
     ↓
Validate JSON against schema
     ↓
Validate Markdown structure
     ↓
Verify source quality (research only)
     ↓
Cross-check consistency
     ↓
PASS → Save as latest
FAIL → Report errors, request fixes
```

## Example Validation Output

### Successful Validation
```json
{
  "validation_status": "PASS",
  "json_validation": {
    "status": "PASS",
    "errors": [],
    "warnings": []
  },
  "markdown_validation": {
    "status": "PASS",
    "missing_sections": [],
    "errors": [],
    "warnings": []
  },
  "consistency_check": {
    "status": "PASS",
    "mismatches": []
  },
  "summary": "All validation checks passed. Report conforms to schema."
}
```

### Failed Validation (Example)
```
❌ Validation FAILED

JSON Errors:
- Missing required field: risk_assessment.scenarios
- Invalid verdict value: 'MAYBE' (must be PASS, PASS_WITH_CONCERNS, or FAIL)
- executive_summary only 35 characters (minimum: 50)

Markdown Errors:
- Missing required section: ## Integration Impact
- Domain 'Security' listed in metadata but no findings section found

Source Quality Issues (research only):
- Only 2 sources consulted (minimum: 3)
- 80% of sources are LOW credibility (threshold: 70%)

Suggestions:
1. Add risk_assessment.scenarios array with at least one scenario
2. Change verdict to PASS, PASS_WITH_CONCERNS, or FAIL
3. Expand executive_summary to at least 50 characters
4. Add ## Integration Impact section
5. Add ## Security findings section or remove from domains_analyzed
6. Conduct more research - consult at least 3 sources total
7. Include more HIGH credibility sources (academic papers, official docs)
```

## Benefits

### Consistency
- Same structure every time
- No format variations
- Predictable output

### Automation-Friendly
- Easy to parse JSON
- Standardized enum values
- Consistent field names

### Quality Assurance
- Required sections enforced
- Source quality validated (research)
- Format violations caught early

### Developer Experience
- Clear error messages
- Specific suggestions for fixes
- No guessing about format requirements

## Testing

### Test Cases Recommended

**For both skills:**
1. Missing required fields → Should FAIL
2. Invalid enum values → Should FAIL
3. Missing required sections → Should FAIL
4. Inconsistencies between JSON and markdown → Should FAIL
5. Well-formed output → Should PASS

**Additional for deep-research:**
6. Insufficient sources (<3) → Should FAIL
7. Poor source quality (>70% LOW credibility) → Should FAIL
8. Executive summary too short (<50 chars) → Should FAIL

### Running Tests

Tests can be run by:
1. Creating intentionally malformed outputs
2. Invoking validator sub-agent
3. Verifying it catches violations
4. Verifying clear error messages
5. Testing well-formed outputs pass

## Configuration

Both validators support configuration via:

**Deep Verify:**
```bash
export DEEP_VERIFY_OUTPUT_DIR=".outputs/verification/"
```

**Deep Research:**
```bash
export DEEP_RESEARCH_OUTPUT_DIR=".outputs/research/"
```

## Future Improvements

Potential enhancements:
1. Add auto-fix suggestions (not just error messages)
2. Create validation CLI tool for testing
3. Add validation metrics to reports
4. Support custom validation rules
5. Generate validation reports with statistics

## Documentation

**Deep Verify:**
- `skills/deep-verify/schemas/README.md` - Schema documentation
- `skills/deep-verify/validators/output-validator.md` - Validation logic
- `skills/deep-verify/SKILL.md` (Step 5) - Validation gate integration

**Deep Research:**
- `skills/deep-research/schemas/README.md` - Schema documentation
- `skills/deep-research/validators/output-validator.md` - Validation logic
- `skills/deep-research/SKILL.md` (Step 7) - Validation gate integration

## Commits

1. `adbe4e2` - Add standardized output formats and validation gates for deep-verify and deep-research
2. `29d9e1b` - Update repository README to highlight output format standardization

## Credits

Implemented following TDD principles from `writing-skills` skill:
- RED phase: Documented baseline behavior
- GREEN phase: Created schemas and validators
- REFACTOR phase: Integrated validation gates into workflow

This standardization ensures both skills produce consistent, predictable, and parseable outputs for reliable automation and integration.
