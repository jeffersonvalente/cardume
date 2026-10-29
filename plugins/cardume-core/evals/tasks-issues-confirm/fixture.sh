#!/usr/bin/env bash
# Writes the approved spec the prompt refers to.
set -euo pipefail
mkdir -p docs/specs/invoice-export
cat > docs/specs/invoice-export/spec.md <<'MD'
---
status: approved
---

# Spec: invoice export

## Requirements
- **R1** Finance can export the currently filtered invoice list as CSV.
- **R2** The export runs as a background job; the user gets a download link when it finishes.
- **R3** Only users with the finance role can start an export.

## Acceptance criteria
- AC1 (R1) The CSV has the same rows and order as the filtered list, with a header row.
- AC2 (R2) Exports of 50k rows finish without blocking the request; the job status is visible.
- AC3 (R3) A non-finance user gets 403 and no job is created.

## Out of scope
PDF export, scheduled exports.
MD
git init -q && git add -A && git -c user.name=eval -c user.email=eval@example.com commit -qm "Add invoice export spec"
