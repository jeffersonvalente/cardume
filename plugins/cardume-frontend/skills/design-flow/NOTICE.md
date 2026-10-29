# NOTICE — design-flow

The `design-flow` skill in this repository is a port of **Impeccable** by Paul Bakaus
(https://impeccable.style, Apache License 2.0). The design methodology, reference files,
anti-pattern detection engine, and scripts are derived works of Impeccable.

Changes made in this port: user-facing strings rebranded `impeccable` → `design-flow`;
packaged as a Claude Code plugin with script paths routed through the `cardume-design-flow` launcher;
the `pin`/`unpin` commands and the network update-check were removed (the update-check code was deleted outright in Cardume); the live server was hardened (local-only CORS, Host check, tokenized `/live.js`, safe `/source`, opt-in CLI copy agents); the runtime sidecar
directory was renamed `.impeccable/` → `.design-flow/`, environment variables use the
`DESIGN_FLOW_` prefix, and live-mode markers/attributes use the `design-flow-` prefix. Internal
script identifiers (detector overlay classes and messages, for example) still reference the
original `impeccable` name and are covered by the attribution below.

Impeccable itself builds on Anthropic's original frontend-design skill. Original NOTICE follows.

---
# Notice

Impeccable
Copyright 2025-2026 Paul Bakaus

## Anthropic frontend-design Skill

The `impeccable` skill in this project builds on Anthropic's original frontend-design skill.

**Original work:** https://github.com/anthropics/skills/tree/main/skills/frontend-design
**Original license:** Apache License 2.0
**Copyright:** 2025 Anthropic, PBC

This project extends the original with:
- 7 domain-specific reference files (typography, color-and-contrast, spatial-design, motion-design, interaction-design, responsive-design, ux-writing)
- 23 commands
- Expanded patterns and anti-patterns

## Typecraft Guide Skill

The `typography.md` reference in this project incorporates a set of tactical additions merged in from ehmo's `typecraft-guide-skill` at the author's request: dark-mode weight/tracking compensation, `font-display: optional` vs `swap`, preload-critical-weight-only guidance, variable fonts for 3+ weights, `clamp()` max-to-min ratio bound, responsive measure/container coupling, `text-wrap: balance` / `pretty`, `font-optical-sizing: auto`, ALL-CAPS tracking quantification, and the paragraph-rhythm rule (space OR indent, never both).

**Original work:** https://github.com/ehmo/typecraft-guide-skill
**Original license:** see upstream repo
**Author:** ehmo
