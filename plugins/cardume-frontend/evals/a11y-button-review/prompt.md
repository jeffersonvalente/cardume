---
name: a11y-button-review
plugins: ["../..", "../../../cardume-core"]
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this React component for accessibility and UX problems and list concrete fixes:

```tsx
export function Save({ onSave }) {
  return <div className="btn" onClick={onSave}><img src="/disk.svg" /></div>;
}
```
