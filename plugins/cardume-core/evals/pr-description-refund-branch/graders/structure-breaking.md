---
type: regex
pattern: "breaking|BREAKING CHANGE|refunds/sync"
flags: i
target: last_message
---

The removal of the poller and its admin endpoint must be called out as breaking.
