#!/usr/bin/env python3
"""
PreToolUse hook (Write|Edit|NotebookEdit|Bash): keeps verifier agents independent.

When the tool call comes from the qa-gatekeeper subagent, file writes are allowed only under
docs/gates/ and .cardume/reports/, and Bash commands that change files or git state are denied
(it can still run tests, builds and read-only commands). A verifier that edits the code it checks
becomes its author. Calls from the main session and other agents are untouched.
"""

import json
import os
import re
import sys
from pathlib import Path

VERIFIER_AGENTS = ("qa-gatekeeper",)
ALLOWED_DIRS = ("docs/gates", ".cardume/reports")
CMD = r"[^|;&\n]*"
# git, optionally followed by global options such as `-C dir` or `--no-pager`.
GIT = r"\bgit\b(?:\s+-[cC]\s+\S+|\s+--?[a-zA-Z-]+(?:=\S+)?)*\s+"
# Shell commands that modify files or repository state. Quoted strings are removed before matching,
# so `grep -n '=>'` or `grep 'git add' docs` are not mistaken for writes. Output redirection is
# allowed only to /dev/null, file descriptors, or the report folders. This is best-effort: an
# interpreter can still write files (python -c ...), which the agent instructions forbid.
BASH_WRITE_PATTERNS = [
    r"(?<![&<])>>?\s*(?!/dev/null|&|\.cardume/reports/|docs/gates/)[^\s>&]",
    r"\bsed\b" + CMD + r"\s-[a-zA-Z]*i",
    r"\bperl\b" + CMD + r"\s-[a-zA-Z]*i",
    r"\btee\b",
    r"\b(rm|mv|cp|truncate|chmod|chown|ln|mkdir|touch|patch|dd)\s",
    r"\bfind\b" + CMD + r"\s-(delete|exec\s+(rm|mv|sed))\b",
    GIT + r"(commit|checkout|switch|reset|restore|apply|am|merge|rebase|cherry-pick|push|add|rm|mv|clean)\b",
    GIT + r"stash\b(?!\s+(list|show)\b)",
    GIT + r"tag\s+(?!-l\b|--list\b|-n\d*\b|--contains\b|--points-at\b|--sort\b)[^\s]",
    GIT + r"branch\s+(-[dDmMcC]\b|--(delete|move|copy)\b)",
    r"\b(npm|pnpm|yarn|bun|pip|uv|poetry)\s+(install|i|add|remove|uninstall|update|upgrade|sync|ci)\b",
    r"\bnpx\s+\S+\s+install\b",
]
QUOTED = [re.compile(r"'[^']*'"), re.compile(r'"(?:\\.|[^"\\])*"')]


def without_quotes(command: str) -> str:
    for pattern in QUOTED:
        command = pattern.sub("''", command)
    return command


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def is_verifier(agent_type: str) -> bool:
    return any(agent_type == name or agent_type.endswith(":" + name) for name in VERIFIER_AGENTS)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    if not is_verifier(payload.get("agent_type") or ""):
        return
    tool_input = payload.get("tool_input") or {}
    if payload.get("tool_name") == "Bash":
        command = without_quotes(tool_input.get("command", ""))
        if any(re.search(p, command) for p in BASH_WRITE_PATTERNS):
            deny("qa-gatekeeper runs read-only commands (tests, builds, linters, git log/diff). "
                 "This command changes files or repository state; report the problem instead.")
        return
    target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
    resolved = (cwd / target).resolve() if target else cwd
    allowed = any(resolved.is_relative_to(cwd / d) for d in ALLOWED_DIRS)
    if allowed:
        return
    deny("qa-gatekeeper only writes reports (docs/gates/, .cardume/reports/). "
         "Report the problem instead of changing the code you are verifying.")


if __name__ == "__main__":
    main()
