# Deep Research Output Validator

This validator ensures that deep-research output files conform to the required format specification.

## Purpose

Validate both markdown and JSON outputs from deep-research against the formal schema to ensure:
- All required sections are present
- Field types and values match specifications
- Report structure is consistent across runs
- No chaotic format variations

## Validation Criteria

### JSON Validation
Validate against `schemas/research-report-schema.json`:

**Required top-level fields:**
- `topic`: String describing the research topic
- `generated`: ISO 8601 timestamp
- `research_duration`: String (e.g., "45 minutes")
- `domains_analyzed`: Array with at least 1 domain
- `sources_consulted`: Integer ≥ 1
- `validation_status`: Must be "VALIDATED", "PARTIAL", or "PRELIMINARY"
- `executive_summary`: String with at least 50 characters
- `research_intent`: Object with primary_question, primary_domains, secondary_domains, research_depth
- `key_findings_by_domain`: Array with at least 1 domain's findings
- `cross_domain_insights`: Array of cross-domain connections
- `synthesis`: Object with key_patterns array
- `recommendations`: Array with at least 1 recommendation
- `quality_assessment`: Object with validation method and credibility distribution
- `sources_bibliography`: Array with at least 1 domain's sources

**Research Intent:**
- `research_depth`: Must be "BRIEF", "STANDARD", or "COMPREHENSIVE"
- `primary_domains`: Array of strings
- `secondary_domains`: Array of strings

**Key Findings by Domain:**
- Each domain must have at least 1 finding
- Each finding must have: topic, consensus (STRONG/MODERATE/WEAK/DEBATE), evidence array, sources array
- Each source must have: url, title, credibility (HIGH/MEDIUM/LOW), type, key_points array

**Recommendations:**
- Each must have: recommendation, rationale, confidence (HIGH/MEDIUM/LOW), supporting_evidence array
- At least 1 recommendation required

**Quality Assessment:**
- Must include source_credibility_distribution with high/medium/low counts
- Must include cross_domain_validation_percentage (0-100)

### Markdown Validation

**Required sections (in order):**
1. Title: `# Deep Research Report: {Topic}`
2. Metadata block with: Generated, Research Duration, Domains Analyzed, Sources Consulted, Validation Status
3. `## Executive Summary` with 3-5 sentence overview
4. `## Research Intent & Scope` with primary question, scope details
5. `## Key Findings by Domain` with subsections for each domain
6. `## Cross-Domain Insights` (if applicable)
7. `## Synthesis & Patterns` with key patterns, contradictions, gaps
8. `## Recommendations` with numbered actionable recommendations
9. `## Research Quality Assessment` with validation metrics
10. `## Sources Bibliography` organized by domain
11. `## Appendix: Research Methodology` (optional but recommended)

**Validation Status format:**
- Must be one of: VALIDATED, PARTIAL, PRELIMINARY
- Must appear after "**Validation Status:**"

**Timestamp format:**
- ISO 8601 or human-readable format
- Must be consistent with JSON

**Domain consistency:**
- Domains in metadata must match key findings sections
- Each domain in domains_analyzed must have findings and sources sections
- Primary vs secondary domain distinction should be clear

**Source formatting:**
- Each source must be: `[Title](URL) - credibility - date`
- URLs must be valid
- Credibility must be HIGH, MEDIUM, or LOW

## Validation Process

When invoked as a sub-agent, this validator:

1. **Locate output files** in `.outputs/research/`
2. **Load JSON schema** from `schemas/research-report-schema.json`
3. **Validate JSON output** against schema
4. **Validate markdown output** for required sections
5. **Cross-check consistency** between JSON and markdown
6. **Verify source quality** (credibility distribution, URL validity)
7. **Generate validation report**

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
  "source_quality_check": {
    "status": "PASS" | "FAIL",
    "total_sources": 0,
    "credibility_distribution": {
      "high": 0,
      "medium": 0,
      "low": 0
    },
    "issues": ["source quality issues"],
    "warnings": ["source quality warnings"]
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

This validator is called at **Step 7** of deep-research workflow:
- After report generation
- Before saving as "latest"
- Before reporting completion to user

## Validator Sub-Agent Prompt Template

```
You are an OUTPUT VALIDATOR for deep-research reports. Your role is to ensure format compliance.

## Files to Validate
- Markdown: {markdown_file_path}
- JSON: {json_file_path}

## Validation Tasks
1. Load and parse JSON schema: skills/deep-research/schemas/research-report-schema.json
2. Validate JSON against schema using a JSON Schema validator
3. Parse markdown and check for required sections
4. Verify source quality and credibility distribution
5. Cross-validate consistency between JSON and markdown
6. Generate validation report

## Required Tools
- Read: To load files and schema
- JSON Schema validation (use available libraries or manual validation)

## Validation Criteria
{content from "Validation Criteria" section above}

## Output Format
{JSON format from "Output Format" section above}

## Strictness Level
- CRITICAL errors: Missing required fields, invalid enums, type mismatches, source quality issues
- WARNINGS: Formatting inconsistencies, optional fields missing, low-credibility source overuse
- FAIL validation if ANY critical errors exist

## Source Quality Thresholds
- FAIL if >70% of sources are LOW credibility
- WARN if >50% of sources are LOW credibility
- FAIL if total sources < 3 (insufficient research)
- WARN if validation_status is PRELIMINARY with <50% cross-domain validation

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
      "Missing required field: research_intent.research_depth",
      "Missing required field: recommendations"
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
      "validation_status: 'IN_PROGRESS' is not valid. Must be one of: VALIDATED, PARTIAL, PRELIMINARY",
      "consensus: 'SOMEWHAT' is not valid. Must be one of: STRONG, MODERATE, WEAK, DEBATE"
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
      "## Executive Summary",
      "## Research Quality Assessment"
    ]
  }
}
```

**Source quality issues:**
```json
{
  "validation_status": "FAIL",
  "source_quality_check": {
    "status": "FAIL",
    "total_sources": 10,
    "credibility_distribution": {
      "high": 1,
      "medium": 1,
      "low": 8
    },
    "issues": [
      "80% of sources are LOW credibility (threshold: 70%)",
      "Only 1 HIGH credibility source (recommended: at least 30%)"
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
      "JSON lists 15 sources but markdown bibliography only has 12",
      "JSON domains_analyzed includes 'Ethics' but no Ethics section in key findings"
    ]
  }
}
```

**Insufficient research depth:**
```json
{
  "validation_status": "FAIL",
  "source_quality_check": {
    "status": "FAIL",
    "total_sources": 2,
    "issues": [
      "Only 2 sources consulted (minimum: 3 for credible research)"
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
- Poor source quality (too many LOW credibility)
- Insufficient total sources
- Mismatched domains between JSON and markdown
- Well-formed output (should PASS)
