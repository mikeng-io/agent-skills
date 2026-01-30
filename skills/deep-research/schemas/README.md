# Deep Research Output Schemas

This directory contains JSON Schema specifications that define the required format for deep-research outputs.

## Purpose

Enforce consistent, predictable output formats across all deep-research executions to eliminate chaos and variation.

## Schemas

### research-report-schema.json

Defines the required structure for research report JSON outputs.

**Key Requirements:**

- **Validation Status**: Must be exactly one of: `VALIDATED`, `PARTIAL`, `PRELIMINARY`
- **Research Depth**: Must be exactly one of: `BRIEF`, `STANDARD`, `COMPREHENSIVE`
- **Sources**: Minimum 1 source required, <3 triggers validation warning
- **Domains**: At least 1 domain must be researched
- **Findings**: Each domain must have at least 1 finding with evidence and sources
- **Recommendations**: At least 1 recommendation required
- **Executive Summary**: Minimum 50 characters

**Field Validation:**

- All enum fields strictly enforced (no typos, no variations)
- Consensus levels: `STRONG`, `MODERATE`, `WEAK`, `DEBATE`
- Source credibility: `HIGH`, `MEDIUM`, `LOW`
- Source types: `academic`, `industry`, `blog`, `documentation`, `other`
- URLs must be valid format
- Required arrays cannot be empty where specified

**Quality Thresholds:**

- FAIL if >70% of sources are LOW credibility
- WARN if >50% of sources are LOW credibility
- FAIL if total sources < 3 (insufficient research)
- Recommend at least 30% HIGH credibility sources

## Usage

The validation gate (Step 7 in deep-research) uses these schemas to verify:

1. **Structural compliance**: All required fields present
2. **Type correctness**: Fields match expected types
3. **Enum validity**: Values match allowed sets
4. **Source quality**: Credibility distribution meets thresholds
5. **Data quality**: Minimum requirements met (e.g., at least 1 finding per domain)

## Benefits

**Before standardization:**
- Validation status could be "Done", "Complete", "Verified", "Validated"
- Consensus could be "Strong", "STRONG", "Mostly agree", "Generally accepted"
- Credibility could be "Good", "Reliable", "Trustworthy", "HIGH"
- Source counts and quality varied wildly
- Sections could be missing or renamed
- Reports varied between runs

**After standardization:**
- Validation status is exactly "VALIDATED", "PARTIAL", or "PRELIMINARY"
- Consensus is exactly "STRONG", "MODERATE", "WEAK", or "DEBATE"
- Credibility is exactly "HIGH", "MEDIUM", or "LOW"
- Source quality thresholds enforced
- All sections consistently present
- Reports have identical structure every time

## Validation Flow

```
Generate Report
     ↓
Validate JSON against schema
     ↓
Validate Markdown structure
     ↓
Verify source quality
     ↓
Cross-check consistency
     ↓
PASS → Save as latest
FAIL → Report errors, request fixes
```

## Source Quality Validation

Special attention to source quality:

- **Critical threshold**: >70% LOW credibility → FAIL
- **Warning threshold**: >50% LOW credibility → WARN
- **Minimum sources**: <3 total → FAIL
- **High credibility target**: Recommend ≥30% HIGH credibility

This ensures research reports are based on credible, diverse sources.

## Testing

To test the schema validation:

```bash
# Using a JSON Schema validator
ajv validate -s research-report-schema.json -d ../../../.outputs/research/latest-research.json
```

## Schema Updates

When updating the schema:

1. Update the JSON Schema file
2. Update validators/output-validator.md with new validation criteria
3. Update SKILL.md Step 6 report template if structure changes
4. Test with both valid and invalid outputs
5. Document changes in this README

## Related Files

- `../validators/output-validator.md` - Validation logic and sub-agent prompt
- `../SKILL.md` (Step 6) - Report generation template
- `../SKILL.md` (Step 7) - Validation gate integration
