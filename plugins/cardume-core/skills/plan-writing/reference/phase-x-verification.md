# Phase X Verification Commands (project-planner)

Full command set for the final verification phase of a plan. Pick only the checks relevant to the project type (see plan-writing Principle 4).

## 1. Run All Verifications (RECOMMENDED)

```bash
# SINGLE COMMAND - Runs all checks in priority order:
cardume-verify-all . --url http://localhost:3000

# Priority Order:
# P0: Security Scan (vulnerabilities, secrets)
# P1: Color Contrast (WCAG AA accessibility)
# P1.5: UX Audit (Psychology laws, Fitts, Hick, Trust)
# P2: Touch Target (mobile accessibility)
# P3: Lighthouse Audit (performance, SEO)
# P4: Playwright Tests (E2E)
```

## 2. Or Run Individually

```bash
# P0: Lint & Type Check
npm run lint && npx tsc --noEmit

# P0: Security Scan
cardume-security-scan .

# P1: UX Audit
cardume-ux-audit .

# P3: Lighthouse (requires running server)
cardume-lighthouse-audit http://localhost:3000

# P4: Playwright E2E (requires running server)
cardume-playwright-runner http://localhost:3000 --screenshot
```

## 3. Build Verification
```bash
# For Node.js projects:
npm run build
# → IF warnings/errors: Fix before continuing
```

## 4. Runtime Verification
```bash
# Start dev server and test:
npm run dev

# Optional: Run Playwright tests if available
cardume-playwright-runner http://localhost:3000 --screenshot
```

## 5. Rule Compliance (Manual Check)
- [ ] No purple/violet hex codes
- [ ] No standard template layouts
- [ ] Clarifying questions were asked and answered

## 6. Phase X Completion Marker
```markdown
# Add this to the plan file after all checks pass:
## ✅ PHASE X COMPLETE
- Lint: ✅ Pass
- Security: ✅ No critical issues
- Build: ✅ Success
- Date: [Current Date]
```

> The Phase X marker belongs in the plan file before the project counts as complete.

---

