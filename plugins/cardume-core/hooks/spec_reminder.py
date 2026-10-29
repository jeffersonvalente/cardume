#!/usr/bin/env python3
"""
Stop hook (non-blocking): reminds the user when a large change has no spec, PRD or ADR alongside it.

"Large" = at least MIN_FILES changed source files or MIN_LINES changed lines versus HEAD, ignoring
docs/ and .cardume/. Silent when the diff already touches docs/specs, docs/prd or docs/adr, and shown
once per change set. Disable with CARDUME_SPEC_REMINDER=0.
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

MIN_FILES = 8
MIN_LINES = 400
DOC_DIRS = ("docs/specs/", "docs/prd/", "docs/adr/")


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ""


def main() -> None:
    if os.environ.get("CARDUME_SPEC_REMINDER") == "0":
        return
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    cwd = Path(payload.get("cwd") or os.getcwd())
    status = git(cwd, "status", "--porcelain", "--untracked-files=all")
    paths = [line[3:].split(" -> ")[-1].strip('"') for line in status.splitlines()]
    if not paths or any(p.startswith(DOC_DIRS) for p in paths):
        return
    source = [p for p in paths if not p.startswith(("docs/", ".cardume/"))]
    changed_lines = 0
    for line in git(cwd, "diff", "HEAD", "--numstat").splitlines():
        added, removed, *_ = line.split("\t")
        if added.isdigit() and removed.isdigit():
            changed_lines += int(added) + int(removed)
    for line in status.splitlines():
        if line.startswith("??"):
            untracked = cwd / line[3:].strip('"')
            if untracked.is_file():
                try:
                    changed_lines += sum(1 for _ in untracked.open(encoding="utf-8", errors="ignore"))
                except OSError:
                    pass
    if len(source) < MIN_FILES and changed_lines < MIN_LINES:
        return

    state = cwd / ".cardume" / "spec-reminder.json"
    fingerprint = hashlib.sha256("\n".join(sorted(source)).encode()).hexdigest()
    try:
        if json.loads(state.read_text()).get("shown") == fingerprint:
            return
    except (OSError, json.JSONDecodeError):
        pass
    state.parent.mkdir(exist_ok=True)
    state.write_text(json.dumps({"shown": fingerprint}))

    print(json.dumps({"systemMessage": (
        f"Cardume: large change ({len(source)} files, {changed_lines} lines) with no spec, PRD or ADR. "
        "If this is level-2/3 work, ask Claude to record the spec (spec skill) or the decisions (adr skill)."
    )}))


if __name__ == "__main__":
    main()
