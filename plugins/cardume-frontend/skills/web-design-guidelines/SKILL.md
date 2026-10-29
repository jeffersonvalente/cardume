---
name: web-design-guidelines
description: Reviews UI code against the Web Interface Guidelines for accessibility, focus states, forms, animation, typography, and performance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Read the bundled rules in `guidelines.md` (in this skill's directory)
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in `guidelines.md`
4. Output findings in the terse `file:line` format it specifies

## Guidelines Source

`guidelines.md` is a vendored copy of
`vercel-labs/web-interface-guidelines` (`command.md`, MIT, see `LICENSE`), pinned on 2026-10-28.
No network access is needed. To refresh it, re-download that file deliberately and review the diff.

## Usage

When a user provides a file or pattern argument:
1. Read `guidelines.md`
2. Read the specified files
3. Apply all rules from the guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.

---

## Related Skills

| Skill | When to Use |
|-------|-------------|
| **[frontend-design](../frontend-design/SKILL.md)** | Before coding - Learn design principles (color, typography, UX psychology) |
| **web-design-guidelines** (this) | After coding - Audit for accessibility, performance, and best practices |

## Design Workflow

```
1. DESIGN   → Read frontend-design principles
2. CODE     → Implement the design
3. AUDIT    → Run web-design-guidelines review ← YOU ARE HERE
4. FIX      → Address findings from audit
```
