#!/usr/bin/env python3
"""
UserPromptSubmit hook (non-blocking): adds a one-paragraph routing reminder to Claude's context, so the
matching skill or agent gets used on ordinary requests. Plain stdout from this event becomes context.

Silent for slash commands, where the user already chose what runs, and on unreadable input. Disable
with CARDUME_ROUTING_NUDGE=0. hooks.json runs it with `|| true`, because exit code 2 on this event would
block the prompt and a reminder must never do that.
"""

import json
import os
import re
import sys

REMINDER = (
    "Cardume routing check: if this project uses work levels, state the level in one line first and keep "
    "that line in your final reply. Then decide whether a Cardume skill or agent covers this request. If one "
    "does, load the skill with the Skill tool or dispatch the agent with the Agent tool before answering, and "
    "say in one line which one you are using and why. When several apply, process skills (spec, debugging, "
    "TDD) come before implementation skills. Skip all of this for trivial requests (typos, one-line questions)."
)
SLASH_COMMAND_RE = re.compile(r"\s*/[\w:.-]+(\s|$)")


def main() -> None:
    if os.environ.get("CARDUME_ROUTING_NUDGE") == "0":
        return
    try:
        prompt = json.load(sys.stdin).get("prompt")
    except (ValueError, AttributeError, RecursionError):
        return
    if not isinstance(prompt, str) or SLASH_COMMAND_RE.match(prompt):
        return
    print(REMINDER)


if __name__ == "__main__":
    main()
