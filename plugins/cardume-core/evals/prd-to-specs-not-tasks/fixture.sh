#!/usr/bin/env bash
# Writes the approved PRD the prompt refers to.
set -euo pipefail
mkdir -p docs/prd
cat > docs/prd/PHASE-2.md <<'MD'
# PRD: Phase 2 — card payments

Status: approved (2026-10-20)

## Problem
Customers can only pay invoices by bank transfer, so payments arrive late and finance reconciles by hand.

## Capabilities
- **C1** Customers can pay an open invoice by card from the invoice page.
- **C2** A receipt is emailed to the customer within 1 minute of a successful payment.
- **C3** The finance dashboard shows paid vs unpaid invoices, filterable by month.

## Out of scope
Refunds, partial payments, saved cards.

## Success metric
70% of invoices paid within 7 days of issue (today: 35%).
MD
git init -q && git add -A && git -c user.name=eval -c user.email=eval@example.com commit -qm "Add phase 2 PRD"
