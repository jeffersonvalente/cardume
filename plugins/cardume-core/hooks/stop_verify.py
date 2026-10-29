#!/usr/bin/env python3
"""
Stop hook: before Claude finishes a turn that changed code, run the blocking checks
(`cardume-checklist . --critical-only --files <changed files>`: security scan + lint) on the
changed files only, so problems that already existed elsewhere in the project never block. If they
fail, exit 2 so Claude sees the failures and keeps working instead of declaring the task done.

Skips when: not a git repo, nothing changed, the same changes already passed, or
CARDUME_STOP_VERIFY=0. After MAX_BLOCKS blocks on the same set of changed files it lets Claude stop
and leaves the decision to the user; the budget resets when the set of changed files changes (new
work) or in a new session. State lives in <project>/.cardume/.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MAX_BLOCKS = 3
CHECK_TIMEOUT = 280
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def changed_files(cwd: Path):
    """Return (fingerprint, existing changed paths) or None when nothing changed."""
    status = git(cwd, "status", "--porcelain", "--untracked-files=all")
    if status.returncode != 0:
        return None
    lines = [l for l in status.stdout.splitlines() if not l[3:].startswith(".cardume/")]
    paths = [l[3:].split(" -> ")[-1].strip('"') for l in lines]
    paths = [p for p in paths if (cwd / p).is_file()]
    if not paths:
        return None
    digest = hashlib.sha256(git(cwd, "diff", "HEAD").stdout.encode())
    for line in sorted(lines):
        digest.update(line.encode())
        if line.startswith("??"):
            untracked = cwd / line[3:]
            if untracked.is_file():
                digest.update(str(untracked.stat().st_mtime_ns).encode())
    return digest.hexdigest(), paths


def load_state(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(state))


def main() -> None:
    if os.environ.get("CARDUME_STOP_VERIFY") == "0":
        return
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    cwd = Path(payload.get("cwd") or os.getcwd())
    changes = changed_files(cwd)
    if changes is None:
        return
    fingerprint, paths = changes
    paths = ["./" + p if p.startswith("-") else p for p in paths]

    state_path = cwd / ".cardume" / "stop-verify.json"
    state = load_state(state_path)
    if state.get("passed") == fingerprint:
        return
    session = payload.get("session_id", "")
    files_key = hashlib.sha256("\n".join(sorted(paths)).encode()).hexdigest()
    same_work = state.get("session") == session and state.get("files") == files_key
    blocks = state.get("blocks", 0) if same_work else 0
    if blocks >= MAX_BLOCKS:
        print(json.dumps({"systemMessage": f"Cardume: checks still failing after {MAX_BLOCKS} attempts; "
                                           "run `cardume-checklist .` to see them."}))
        return

    plugin_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    checklist = plugin_root / "bin" / "cardume-checklist"
    try:
        result = subprocess.run([str(checklist), str(cwd), "--critical-only", "--files", *paths], cwd=cwd,
                                capture_output=True, text=True, timeout=CHECK_TIMEOUT)
    except subprocess.TimeoutExpired:
        return

    if result.returncode == 0:
        save_state(state_path, {"passed": fingerprint})
        return

    save_state(state_path, {"session": session, "files": files_key, "blocks": blocks + 1})
    output = ANSI_RE.sub("", result.stdout + result.stderr).strip().splitlines()
    print("Cardume Stop check: blocking checks failed on your changes. Fix them (or explain to the "
          "user why they cannot be fixed) before finishing.\n\n" + "\n".join(output[-40:]),
          file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
