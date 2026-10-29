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

RULES = [
    # Infrastructure
    (r"\bterraform\s+(apply|destroy)\b", "terraform apply/destroy changes real infrastructure"),
    (r"\bterraform\s+state\s+(rm|push|mv)\b", "terraform state surgery can orphan resources"),
    (r"\b(tofu|terragrunt)\b" + ARGS + r"\b(apply|destroy)\b", "apply/destroy changes real infrastructure"),
    (r"\bkubectl\b" + ARGS + r"\b(delete|drain|cordon|replace\s+--force)\b", "kubectl delete/drain affects the cluster"),
    (r"\bhelm\s+(uninstall|delete|rollback)\b", "helm uninstall/rollback changes a release"),
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


# A dry run of a publish/release command uploads nothing, so it needs no confirmation.
DRY_RUN = r"\s(--dry-run|--dryrun|-n)(\s|$)|\s--snapshot\b"
DRY_RUN_SAFE = {reason for pattern, reason in RULES
                if "publish" in reason or "release" in reason or "registry" in reason}


def main() -> None:
    if os.environ.get("CARDUME_GUARD_BASH") == "0":
        return
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    command = (payload.get("tool_input") or {}).get("command", "")
    dry_run = re.search(DRY_RUN, command) is not None
    for pattern, reason in RULES:
        if dry_run and reason in DRY_RUN_SAFE:
            continue
        if re.search(pattern, command, re.IGNORECASE):
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
