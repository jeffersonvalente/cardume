---
type: llm
focus: last_message
weight: 2
---

PASS if it removes the fixed waitForTimeout sleeps and replaces them with web-first auto-retrying assertions (`await expect(locator).toHaveText(...)`, `toBeVisible()`) and/or waiting on the relevant network response; replaces brittle CSS selectors (.btn-primary, text=Pay) with role/label/test-id locators (getByRole, getByTestId); explains why the one-shot `$eval`/`isVisible` checks race in CI; and addresses test isolation (seeded cart state via API/fixture rather than depending on previous state). It should mention CI diagnostics such as trace on first retry.
FAIL if it just increases timeouts or keeps waitForTimeout, or keeps the non-retrying isVisible assertion.
