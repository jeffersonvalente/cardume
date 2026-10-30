#!/usr/bin/env python3
"""
PreToolUse hook (Bash): asks the user before destructive or public commands.

Claude still proposes the command; the user approves or rejects it in the permission prompt.
Disable with CARDUME_GUARD_BASH=0.
"""

import json
import os
import re
import sys

# Text between a tool and its verb (flags, -r, -w pkg, --filter …) without crossing a shell operator.
ARGS = r"[^|;&\n]*?"
# Flags before a subcommand, as in `kubectl -n prod --context=x get`. Flags that take a value are listed, so
# the namespace in `kubectl -n logs delete` is not read as a subcommand. Shell expansions and quotes match
# nothing here on purpose: a line this can't parse falls through to the broad rule, which asks.
PLAIN = r"[^\s$\"'`()|;&]+"
VALUE_FLAG = r"(?:-n|-s|--namespace|--context|--kube-context|--cluster|--user|--kubeconfig|--server|--token|--as)"
FLAGS = r"(?:\s+(?:" + VALUE_FLAG + r"\s+" + PLAIN + r"|(?!" + VALUE_FLAG + r"\s)-" + PLAIN + r"))*\s+"


def unless(reads: str) -> str:
    """Text up to the verb, for a tool call whose subcommand isn't one of `reads`."""
    return r"(?!" + FLAGS + r"(?:" + reads + r")(?![\w-]))" + ARGS


# Reads, plus exec, cp and attach: what those do depends on the command inside them.
KUBECTL_READS = (r"get|describe|logs|top|events|explain|diff|wait|version|config|kustomize|options|completion|help|plugin"
                 r"|api-resources|api-versions|cluster-info|exec|cp|attach|port-forward|auth\s+(?:can-i|whoami)"
                 r"|apply\s+view-last-applied|rollout" + FLAGS + r"(?:status|history)")
HELM_READS = (r"list|ls|status|history|get|show|inspect|template|lint|diff|search|repo|plugin|dependency|dep|registry"
              r"|pull|fetch|package|create|push|test|verify|version|env|completion|help")

RULES = [
    # Infrastructure
    (r"\bterraform\s+(apply|destroy)\b", "terraform apply/destroy changes real infrastructure"),
    (r"\bterraform\s+state\s+(rm|push|mv)\b", "terraform state surgery can orphan resources"),
    (r"\b(tofu|terragrunt)\b" + ARGS + r"\b(apply|destroy)\b", "apply/destroy changes real infrastructure"),
    (r"\bkubectl\b" + unless(KUBECTL_READS) + r"\b(annotate|apply|auth|autoscale|certificate|cordon|create|debug|delete|drain|"
     r"edit|expose|label|patch|replace|rollout|run|scale|set|taint|uncordon)\b", "kubectl changes the live cluster"),
    (r"\bhelm\b" + unless(HELM_READS) + r"\b(install|upgrade|uninstall|delete|rollback)\b",
     "helm changes a release on the live cluster"),
    (r"\bgcloud\b" + ARGS + r"\s(delete|remove-iam-policy-binding)\b", "gcloud delete removes cloud resources"),
    (r"\baws\b" + ARGS + r"\s(delete-[a-z-]+|terminate-instances|rb)\b", "aws delete/terminate removes cloud resources"),
    (r"\baz\b" + ARGS + r"\sdelete\b", "az delete removes cloud resources"),
    (r"\b(gsutil|gcloud\s+storage)\s+(rm|rb)\b|\baws\s+s3\s+rm\b", "removes objects or buckets from storage"),
    # Data
    (r"\bbq\s+rm\b", "bq rm deletes BigQuery datasets or tables"),
    (r"\b(DROP|TRUNCATE)\s+(TABLE|SCHEMA|DATABASE|VIEW)\b", "DROP/TRUNCATE deletes data"),
    (r"\bDELETE\s+FROM\s+\S+\s*(;|$|\"|')", "DELETE without WHERE removes every row"),
    # Filesystem
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*\s+(/|~|\$HOME)(\s|$)", "recursive delete of a root or home directory"),
    # Git history and tags
    (r"\bgit\s+push\b" + ARGS + r"(\s--force\b|\s--force-with-lease\b|\s-f(\s|$)|\s\+\S)", "force push rewrites shared history"),
    (r"\bgit\s+push\b" + ARGS + r"(\s--tags\b|\s--follow-tags\b|\s--mirror\b|\s--all\b|\srefs/tags/|\s:?v?\d+\.\d+\.\d+\S*(\s|$))",
     "pushing tags or all refs publishes releases"),
    # Releases
    (r"\bgh\s+release\s+(create|delete|edit|upload|delete-asset)\b", "GitHub releases are public"),
    (r"\bgh\s+workflow\s+run\b", "dispatching a workflow may deploy or publish"),
    (r"\b(goreleaser\s+release|semantic-release|changeset\s+publish|release-please\s+release-pr)\b",
     "release automation publishes versions"),
    # Package registries
    (r"\b(npm|pnpm|yarn|bun)\b" + ARGS + r"\b(publish|unpublish|deprecate|dist-tag)\b",
     "publishing or changing a package release is public and hard to undo"),
    (r"\b(uv|poetry|hatch|flit)\s+publish\b|\btwine\s+upload\b", "publishing a Python package is public"),
    (r"\bcargo\s+(publish|yank)\b|\bgem\s+(push|yank)\b|\bdotnet\s+nuget\s+push\b",
     "publishing a package is public and hard to undo"),
    (r"\bmvn\b" + ARGS + r"\bdeploy\b|\bgradlew?\b" + ARGS + r"\bpublish\w*\b", "publishing artifacts is public"),
    (r"\b(vsce|ovsx)\s+publish\b", "publishing an extension is public"),
    # Containers and charts
    (r"\bdocker\s+push\b|\bdocker\s+buildx\b" + ARGS + r"\s--push\b|\b(podman|crane)\s+push\b",
     "pushing an image publishes it to a registry"),
    (r"\bhelm\s+push\b", "pushing a chart publishes it"),
]


# A dry run of a publish, release or cluster command changes nothing, so it needs no confirmation.
# The last flag wins, and `=none` is a real run. `-n` means dry run only for git push and cargo publish:
# for helm and kubectl it is the namespace, for gh the notes, for poetry and twine non-interactive mode.
DRY_RUN_FLAG = r"\s--dry-?run(?:=(\S*))?(?=\s|$)"
DRY_RUN_VALUES = {"", "client", "server", "true"}
DRY_RUN_TOOL = r"^(git\s+push|cargo\s+publish)\b.*\s-n(\s|$)|^goreleaser\b.*\s--snapshot\b"
DRY_RUN_SAFE = {reason for pattern, reason in RULES
                if "publish" in reason or "release" in reason or "registry" in reason or "cluster" in reason}
QUOTED = r"\"(?:\\.|[^\"\\])*\"|'[^']*'"
COMMAND_END = r"[|;&\n()`]|\s#|\s--(?=\s|$)"


def is_dry_run(unquoted: str, start: int) -> bool:
    """The flag must belong to this command, not to a note, a comment or another command on the same line."""
    words = re.split(COMMAND_END, unquoted[start:], maxsplit=1)[0]
    flags = re.findall(DRY_RUN_FLAG, words)
    return (bool(flags) and flags[-1] in DRY_RUN_VALUES) or re.search(DRY_RUN_TOOL, words) is not None


def main() -> None:
    if os.environ.get("CARDUME_GUARD_BASH") == "0":
        return
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    command = (payload.get("tool_input") or {}).get("command", "").replace("\\\n", " ")
    unquoted = re.sub(QUOTED, lambda quoted: " " * len(quoted[0]), command)  # same length, so offsets still match
    for pattern, reason in RULES:
        for match in re.finditer(pattern, command, re.IGNORECASE):
            if reason in DRY_RUN_SAFE and is_dry_run(unquoted, match.start()):
                continue
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": f"Cardume guard: {reason}. Confirm before running.",
                }
            }))
            return


if __name__ == "__main__":
    main()
