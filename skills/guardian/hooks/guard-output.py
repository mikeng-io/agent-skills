#!/usr/bin/env python3
"""
PreToolUse hook: guard Write / Edit on .outputs/ paths.

Blocks direct writes to .outputs/ — all council artifacts must be written
via the council-state script (which sets GUARDIAN_OUTPUT_AUTHORITY=1).

Wire in .claude/settings.json:
  {
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Write(*.outputs/*)",
          "hooks": [{"type": "command", "command": "python3 skills/guardian/hooks/guard-output.py"}]
        },
        {
          "matcher": "Edit(*.outputs/*)",
          "hooks": [{"type": "command", "command": "python3 skills/guardian/hooks/guard-output.py"}]
        }
      ]
    }
  }
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from adapters.claude import run_output_guard

run_output_guard()
