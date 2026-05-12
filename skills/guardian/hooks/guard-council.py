#!/usr/bin/env python3
"""
PreToolUse hook: guard Skill(agent-council), Skill(deep-review),
Skill(deep-audit), Skill(deep-verify), Skill(deep-research).

Blocks invocation if required inputs are missing or finding-driven
mode is requested without prior findings.

Wire in .claude/settings.json:
  {
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Skill(agent-council)",
          "hooks": [{"type": "command", "command": "python3 skills/guardian/hooks/guard-council.py"}]
        },
        {
          "matcher": "Skill(deep-review)",
          "hooks": [{"type": "command", "command": "python3 skills/guardian/hooks/guard-council.py"}]
        },
        {
          "matcher": "Skill(deep-audit)",
          "hooks": [{"type": "command", "command": "python3 skills/guardian/hooks/guard-council.py"}]
        },
        {
          "matcher": "Skill(deep-verify)",
          "hooks": [{"type": "command", "command": "python3 skills/guardian/hooks/guard-council.py"}]
        },
        {
          "matcher": "Skill(deep-research)",
          "hooks": [{"type": "command", "command": "python3 skills/guardian/hooks/guard-council.py"}]
        }
      ]
    }
  }
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from adapters.claude import run_council_preflight

run_council_preflight()
