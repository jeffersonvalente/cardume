#!/usr/bin/env bash
# Builds the history the prompt describes (tag v0.3.0, then six commits) and writes the approved gate
# report as an uncommitted file, so `git log v0.3.0..` shows exactly those six commits.
set -euo pipefail
G="git -c user.name=eval -c user.email=eval@example.com"
git init -q
printf '# Changelog\n\n## [0.3.0] - 2026-09-30\n- First playable release.\n' > CHANGELOG.md
$G add -A && $G commit -qm "chore: release v0.3.0" && git tag v0.3.0
for msg in "feat: scenario editor exports levels as JSON (#41)" "feat: add seeded replay files (#43)" \
           "fix: replay desync after pausing (#44)" "fix: crash when a level has no exits (#46)" \
           "refactor: move physics step into sim module (#45)" "docs: explain level file format (#47)"; do
  $G commit -q --allow-empty -m "$msg"
done
mkdir -p docs/gates
cat > docs/gates/GATE-2.md <<'MD'
# Gate 2 report

Criteria: all phase 2 acceptance criteria met, CI green, no open P1 bugs.

| Criterion | Evidence | Result |
| --- | --- | --- |
| Level export and replay features done | specs verified, `docs/specs/*/verify.md` | pass |
| CI green on main | run 812, all jobs passed | pass |
| No open P1 bugs | issue tracker query, 0 results | pass |

Recommendation: approve.
Decision: approved by Ana, 2026-10-27.
Condition: none.
MD
