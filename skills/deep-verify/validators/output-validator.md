# Output Validator: deep-verify

This document defines the validation procedure for deep-verify output artifacts.
Sub-agents spawned for output validation should follow these steps.

## Required Fields Check

Verify the verification report contains all required fields:

- `skill`: must be "deep-verify"
- `verdict`: must be one of PASS | CONCERNS | FAIL
- `timestamp`: must be valid ISO-8601
- `domains`: must be a non-empty array
- `findings`: must be present (may be empty array for PASS)
- `review_id` or `session_id`: must be present

## Verdict Consistency Check

1. If verdict = FAIL: at least one finding must have severity CRITICAL or HIGH
2. If verdict = CONCERNS: findings should include at least one MEDIUM or higher
3. If verdict = PASS: no CRITICAL or HIGH findings should be present

Report inconsistencies as validation warnings, not hard failures.

## Finding Schema Check

Each finding in the `findings` array must have:
- `id`: string (e.g., "F001")
- `severity`: one of CRITICAL | HIGH | MEDIUM | LOW | INFO
- `title`: non-empty string
- `description`: non-empty string

Optional but expected: `evidence`, `recommendation`, `domains`

## Output

Return a validation summary:
```json
{
  "valid": true | false,
  "warnings": ["list of non-blocking issues"],
  "errors": ["list of blocking issues — these mean the report is invalid"]
}
```
