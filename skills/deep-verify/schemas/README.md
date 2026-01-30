# Deep Verify Output Schemas

This directory contains JSON Schema specifications that define the required format for deep-verify outputs.

## Purpose

Enforce consistent, predictable output formats across all deep-verify executions to eliminate chaos and variation.

## Schemas

### verification-report-schema.json

Defines the required structure for verification report JSON outputs.

**Key Requirements:**

- **Verdict**: Must be exactly one of: `PASS`, `PASS_WITH_CONCERNS`, `FAIL`
- **Experts**: Minimum 3 experts (Devil's Advocate, Integration Checker, Third-Party)
- **Domains**: At least 1 domain must be analyzed
- **Risk Assessment**: At least 1 pre-mortem scenario required
- **Summary**: Must include all three dimensions (domain correctness, risk assessment, integration impact)

**Field Validation:**

- All enum fields strictly enforced (no typos, no variations)
- Required arrays cannot be empty where specified
- Timestamp must be ISO 8601 format
- Severity and impact levels use standardized values

## Usage

The validation gate (Step 5 in deep-verify) uses these schemas to verify:

1. **Structural compliance**: All required fields present
2. **Type correctness**: Fields match expected types
3. **Enum validity**: Values match allowed sets
4. **Data quality**: Minimum requirements met (e.g., at least 1 scenario)

## Benefits

**Before standardization:**
- Verdict could be "PASS", "Pass", "PASSED", "OK", "GOOD"
- Impact could be "High", "HIGH", "high", "Major", "Severe"
- Sections could be missing or renamed
- Reports varied wildly between runs

**After standardization:**
- Verdict is exactly "PASS", "PASS_WITH_CONCERNS", or "FAIL"
- Impact is exactly "LOW", "MEDIUM", "HIGH", or "CRITICAL"
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
Cross-check consistency
     ↓
PASS → Save as latest
FAIL → Report errors, request fixes
```

## Testing

To test the schema validation:

```bash
# Using a JSON Schema validator
ajv validate -s verification-report-schema.json -d ../../../.outputs/verification/latest-verification.json
```

## Schema Updates

When updating the schema:

1. Update the JSON Schema file
2. Update validators/output-validator.md with new validation criteria
3. Update SKILL.md Step 4 report template if structure changes
4. Test with both valid and invalid outputs
5. Document changes in this README

## Related Files

- `../validators/output-validator.md` - Validation logic and sub-agent prompt
- `../SKILL.md` (Step 4) - Report generation template
- `../SKILL.md` (Step 5) - Validation gate integration
