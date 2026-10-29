#!/usr/bin/env python3
"""
PostToolUse hook (Edit|Write): fast syntax check of the file Claude just changed.

On a syntax error, exits 2 so the error is shown to Claude right away, before it moves on.
Only checks file types whose checker ships with the runtime (no project linters here; those run in
the Stop hook). Disable with CARDUME_SYNTAX_CHECK=0.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def check(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".py":
        # compile() checks syntax without writing __pycache__ into the project
        return [sys.executable, "-c", "import sys; compile(open(sys.argv[1], 'rb').read(), sys.argv[1], 'exec')", str(path)]
    if suffix in (".js", ".mjs", ".cjs") and shutil.which("node"):
        return ["node", "--check", str(path)]
    if suffix in (".sh", ".bash"):
        return ["bash", "-n", str(path)]
    if suffix == ".json":
        return [sys.executable, "-c", "import json,sys; json.load(open(sys.argv[1]))", str(path)]
    return None


def main() -> None:
    if os.environ.get("CARDUME_SYNTAX_CHECK") == "0":
        return
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    file_path = (payload.get("tool_input") or {}).get("file_path")
    if not file_path:
        return
    path = Path(file_path)
    cmd = check(path) if path.is_file() else None
    if not cmd:
        return
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[-1500:]
        print(f"Syntax error in {path}:\n{detail}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
