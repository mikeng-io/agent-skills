# Deep Verify Output Validator

This validator ensures that deep-verify output files conform to the required format specification.

## Purpose

Validate both markdown and JSON outputs from deep-verify against the formal schema to ensure:
- All required sections are present
- Field types and values match specifications
- Report structure is consistent across runs
- No chaotic format variations

## Validation Criteria

### JSON Validation
Validate against `schemas/verification-report-schema.json`:

**Required top-level fields:**
- `verdict`: Must be "PASS", "PASS_WITH_CONCERNS", or "FAIL"
- `generated`: ISO 8601 timestamp
- `domains_analyzed`: Array with at least 1 domain
- `experts_consulted`: Integer ≥ 3
- `summary`: Object with domain_correctness, risk_assessment, integration_impact
- `risk_assessment`: Object with scenarios and hidden_assumptions arrays
- `domain_findings`: Array of domain findings
- `integration_impact`: Object with affected_components, dependencies, coordination_required, risks
- `third_party_perspective`: Object with clarity_score, questions, suggestions

**Risk Assessment Scenarios:**
- Each must have: scenario, likelihood (LOW/MEDIUM/HIGH), impact (LOW/MEDIUM/HIGH/CRITICAL), evidence, mitigation
- At least 1 scenario required

**Domain Findings:**
- Each domain must have array of findings
- Each finding must have: severity (CRITICAL/HIGH/MEDIUM/LOW), description, evidence
- Optional: fix

**Integration Impact:**
- Arrays can be empty but must exist
- Risks array items must have: area, risk

### Markdown Validation

**Required sections (in order):**
1. Title: `# Deep Verify Report`
2. Metadata block with: Verdict, Generated, Domains Analyzed, Experts Consulted
3. `## Summary` with table containing Domain Correctness, Risk Assessment, Integration Impact
4. `## Risk Assessment (Devil's Advocate)` with at least one risk scenario
5. `## Domain Expert Findings` with findings from each domain
6. `## Integration Impact` with affected components, dependencies, coordination
7. `## Third-Party Perspective` with clarity score, questions, suggestions

**Verdict format:**
- Must be one of: PASS, PASS_WITH_CONCERNS, FAIL
- Must appear in bold after "**Verdict:**"

**Timestamp format:**
- ISO 8601 or human-readable format
- Must be consistent with JSON

**Domain consistency:**
- Domains listed in metadata must match domain findings sections
- Each domain in domains_analyzed must have a finding section

## Validation Process

When invoked as a sub-agent, this validator:

1. **Locate output files** in `.outputs/verification/`
2. **Load JSON schema** from `schemas/verification-report-schema.json`
3. **Validate JSON output** against schema
4. **Validate markdown output** for required sections
5. **Cross-check consistency** between JSON and markdown
6. **Generate validation report**

## Output Format

Return validation result as JSON:

```json
{
  "validation_status": "PASS" | "FAIL",
  "json_validation": {
    "status": "PASS" | "FAIL",
    "errors": ["list of schema validation errors"],
    "warnings": ["list of warnings"]
  },
  "markdown_validation": {
    "status": "PASS" | "FAIL",
    "missing_sections": ["sections not found"],
    "errors": ["structural errors"],
    "warnings": ["formatting issues"]
  },
  "consistency_check": {
    "status": "PASS" | "FAIL",
    "mismatches": ["differences between JSON and markdown"]
  },
  "summary": "Overall validation summary"
}
```

## Failure Handling

If validation fails:

1. **DO NOT** delete or overwrite the output files
2. **REPORT** all specific violations with line/field references
3. **SUGGEST** corrections for each violation
4. **BLOCK** completion until issues are resolved
5. **ALLOW** user to override if intentional

## Integration Point

This validator is called at **Step 5** of deep-verify workflow:
- After report generation
- Before saving as "latest"
- Before reporting completion to user

## Validator Sub-Agent Prompt Template

```
You are an OUTPUT VALIDATOR for deep-verify reports. Your role is to ensure format compliance.

## Files to Validate
- Markdown: {markdown_file_path}
- JSON: {json_file_path}

## Validation Tasks
1. Load and parse JSON schema: skills/deep-verify/schemas/verification-report-schema.json
2. Validate JSON against schema using a JSON Schema validator
3. Parse markdown and check for required sections
4. Cross-validate consistency between JSON and markdown
5. Generate validation report

## Required Tools
- Read: To load files and schema
- JSON Schema validation (use available libraries or manual validation)

## Validation Criteria
{content from "Validation Criteria" section above}

## Output Format
{JSON format from "Output Format" section above}

## Strictness Level
- CRITICAL errors: Missing required fields, invalid enums, type mismatches
- WARNINGS: Formatting inconsistencies, optional fields missing
- FAIL validation if ANY critical errors exist

Return your validation report as JSON.
```

## Example Validation Failures

**Missing required field:**
```json
{
  "validation_status": "FAIL",
  "json_validation": {
    "status": "FAIL",
    "errors": [
      "Missing required field: risk_assessment.scenarios",
      "Missing required field: summary.risk_assessment"
    ]
  }
}
```

**Invalid enum value:**
```json
{
  "validation_status": "FAIL",
  "json_validation": {
    "status": "FAIL",
    "errors": [
      "verdict: 'PARTIALLY_PASS' is not valid. Must be one of: PASS, PASS_WITH_CONCERNS, FAIL"
    ]
  }
}
```

**Missing markdown section:**
```json
{
  "validation_status": "FAIL",
  "markdown_validation": {
    "status": "FAIL",
    "missing_sections": [
      "## Risk Assessment (Devil's Advocate)",
      "## Integration Impact"
    ]
  }
}
```

**Consistency mismatch:**
```json
{
  "validation_status": "FAIL",
  "consistency_check": {
    "status": "FAIL",
    "mismatches": [
      "JSON lists 3 domains ['Security', 'Performance', 'UX'] but markdown only has sections for ['Security', 'Performance']"
    ]
  }
}
```

## Testing the Validator

To test the validator:

1. Create intentionally malformed outputs
2. Run validator sub-agent
3. Verify it catches all violations
4. Verify it provides clear error messages
5. Verify it allows well-formed outputs

Test cases:
- Missing required JSON fields
- Invalid enum values
- Missing markdown sections
- Mismatched domains between JSON and markdown
- Well-formed output (should PASS)
