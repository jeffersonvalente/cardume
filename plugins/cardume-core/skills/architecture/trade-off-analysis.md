# Trade-off Analysis

> Make the cost of each option visible before choosing, so the decision can be defended later.

Use this for decisions that pass the `adr` skill's filter (expensive to reverse, or someone will ask
"why is it like this?"). Small, reversible choices do not need a table. Record the outcome with the
`adr` skill in `docs/adr/ADR-NNN-slug.md`; this file is the analysis that feeds it, so link or
summarize it there instead of keeping a second ADR format.

## Analysis framework

```markdown
### Context
- **Problem**: [What problem are we solving?]
- **Constraints**: [Team size, scale, timeline, budget]

### Options Considered

| Option | Pros | Cons | Complexity | When Valid |
|--------|------|------|------------|-----------|
| Option A | Benefit 1 | Cost 1 | Low | [Conditions] |
| Option B | Benefit 2 | Cost 2 | High | [Conditions] |

### Rationale
1. [Reason 1 - tied to constraints]
2. [Reason 2 - tied to requirements]

### Trade-offs Accepted
- [What we're giving up]
- [Why this is acceptable]
- **Mitigation**: [How we'll address the negatives]

### Revisit Trigger
- [The observation that reopens the decision, e.g. "write volume > 5k/s" or "second team needs it"]
```

The "When Valid" column and the revisit trigger are the parts most often skipped and most useful
later: they say under which conditions the losing option would have won.
