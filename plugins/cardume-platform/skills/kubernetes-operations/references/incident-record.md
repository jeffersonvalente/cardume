# Incident Record

Keep notes while working, not afterwards. A running record lets someone else pick up the
incident and turns into the postmortem with little extra work, as recommended in Google's SRE
guidance on incident management.

## During the incident

Keep a single timeline (in the chat or in `.cardume/reports/incident-YYYYMMDD-NAME.md`):

```text
HH:MM UTC  observed   search-indexer workers restarting, 4/4 pods with restarts > 10 (get pods -n search)
HH:MM UTC  evidence   Last State OOMKilled, exit 137; usage hits the 512Mi limit during bulk reindex
HH:MM UTC  decision   user approved raising the memory limit to 1Gi via the manifest repo
HH:MM UTC  change     PR merged in the manifest repo; Argo CD synced deploy/search-indexer -n search
HH:MM UTC  verified   new pods running, 0 restarts in 30 min, reindex queue draining
```

Mitigate first, root-cause second: restoring service (a rollback, or a limit raised through the
normal change path) is a good outcome even before you know why it failed. Keep evidence that the
mitigation will destroy (previous logs, describe output) before applying it.

## Postmortem

Blameless: describe what the system and process allowed, not who made a mistake.

```markdown
# Postmortem: <short title>

**Date / duration:** <start>–<end> UTC (<minutes>)
**Impact:** <who was affected, how, how many; SLO budget consumed if known>
**Detection:** <alert, user report, dashboard; time from start to detection>

## Summary
<Three or four sentences: what happened, why, how it was fixed.>

## Timeline
<From the running record.>

## Root cause and trigger
<The underlying weakness, and the change or event that exposed it.>

## What went well / what was hard
<Detection, tooling, access, documentation, communication.>

## Action items
| Action | Type (prevent / detect / mitigate) | Owner | Due |
| :--- | :--- | :--- | :--- |
```

Action items that change manifests, charts, alerts, or pipelines go to their owners
(`devops-engineer` for delivery and infra code, `observability-engineer` for alerts and SLOs).
