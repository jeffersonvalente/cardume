---
name: webapp-testing
description: "E2E strategy, Playwright scripts, and visual and accessibility checks. Use when testing a web app in a browser or auditing a deployed URL."
allowed-tools: Read Write Edit Glob Grep Bash
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# Web App Testing

> Discover and test everything. Leave no route untested.

## 🔧 Runtime Scripts

**Execute these for automated browser testing:**

| Script | Purpose | Usage |
|--------|---------|-------|
| `cardume-playwright-runner` (wraps `scripts/playwright_runner.py`) | Basic browser test | `cardume-playwright-runner https://example.com` |
| | With screenshot | `cardume-playwright-runner <url> --screenshot` |
| | Accessibility check | `cardume-playwright-runner <url> --a11y` |

**Requires:** `pip install playwright && playwright install chromium`

---

## 1. Deep Audit Approach

### Discovery First

| Target | How to Find |
|--------|-------------|
| Routes | Scan app/, pages/, router files |
| API endpoints | Grep for HTTP methods |
| Components | Find component directories |
| Features | Read documentation |

### Systematic Testing

1. **Map** - List all routes/APIs
2. **Scan** - Verify they respond
3. **Test** - Cover critical paths

---

## 2. Testing Pyramid for Web

```
        /\          E2E (Few)
       /  \         Critical user flows
      /----\
     /      \       Integration (Some)
    /--------\      API, data flow
   /          \
  /------------\    Component (Many)
                    Individual UI pieces
```

---

## 3. E2E Test Principles

### What to Test

| Priority | Tests |
|----------|-------|
| 1 | Happy path user flows |
| 2 | Authentication flows |
| 3 | Critical business actions |
| 4 | Error handling |

### E2E Best Practices

| Practice | Why |
|----------|-----|
| Role-based locators (`getByRole`, `getByLabel`, `getByText`) | Resilient, user-facing, accessibility-aware |
| `getByTestId` as fallback | When no role/text locator fits (not user-facing) |
| Avoid CSS/XPath selectors | DOM changes break them |
| Wait for elements | Avoid flaky tests |
| Clean state | Independent tests |
| Avoid implementation details | Test user behavior |

---

## 4. Playwright Principles

### Core Concepts

| Concept | Use |
|---------|-----|
| Page Object Model | Encapsulate page logic |
| Fixtures | Reusable test setup |
| Assertions | Built-in auto-wait |
| Trace Viewer | Debug failures |
| Aria snapshots | `expect(locator).toMatchAriaSnapshot(...)` asserts the accessibility tree as YAML; update with `npx playwright test -u` |

### Configuration

| Setting | Recommendation |
|---------|----------------|
| Retries | 2 on CI |
| Trace | on-first-retry |
| Screenshots | on-failure |
| Video | retain-on-failure |

### AI-Assisted Testing

| Tool | What it does |
|------|--------------|
| **Playwright test agents** (`npx playwright init-agents --loop=claude`) | **planner** explores the app and writes a Markdown plan in `specs/`; **generator** turns plans into test files, verifying selectors live; **healer** runs failing tests and repairs them. Uses a `seed.spec.ts` for setup. Re-run `init-agents` after upgrading Playwright. |
| **Playwright MCP** (`@playwright/mcp`) | MCP server for browser automation via the accessibility tree (not screenshots). Claude Code: `claude mcp add playwright npx @playwright/mcp@latest` |

> Review agent-generated tests like any other code: check that assertions test behavior, not just that the page loaded.

---

## 5. Visual Testing

### When to Use

| Scenario | Value |
|----------|-------|
| Design system | High |
| Marketing pages | High |
| Component library | Medium |
| Dynamic content | Lower |

### Strategy

- Baseline screenshots
- Compare on changes
- Review visual diffs
- Update intentional changes

---

## 6. API Testing Principles

### Coverage Areas

| Area | Tests |
|------|-------|
| Status codes | 200, 400, 404, 500 |
| Response shape | Matches schema |
| Error messages | User-friendly |
| Edge cases | Empty, large, special chars |

---

## 7. Test Organization

### File Structure

```
tests/
├── e2e/           # Full user flows
├── integration/   # API, data
├── component/     # UI units
└── fixtures/      # Shared data
```

### Naming Convention

| Pattern | Example |
|---------|---------|
| Feature-based | `login.spec.ts` |
| Descriptive | `user-can-checkout.spec.ts` |

---

## 8. CI Integration

### Pipeline Steps

1. Install dependencies
2. Install browsers
3. Run tests
4. Upload artifacts (traces, screenshots)

### Parallelization

| Strategy | Use |
|----------|-----|
| Per file | Playwright default |
| Sharding | Large suites |
| Workers | Multiple browsers |

---

## 9. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Test implementation | Test behavior |
| Hardcode waits | Use auto-wait |
| Skip cleanup | Isolate tests |
| Ignore flaky tests | Fix root cause |

---

> **Remember:** E2E tests are expensive. Use them for critical paths only.
