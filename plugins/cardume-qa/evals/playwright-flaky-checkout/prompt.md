---
name: playwright-flaky-checkout
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

This Playwright test passes locally but fails about 1 in 5 runs in CI. Fix it.

```ts
test('checkout', async ({ page }) => {
  await page.goto('/cart');
  await page.click('.btn-primary');
  await page.waitForTimeout(3000);
  const total = await page.$eval('#total', el => el.textContent);
  expect(total).toBe('$42.00');
  await page.click('text=Pay');
  await page.waitForTimeout(5000);
  expect(await page.isVisible('.success')).toBe(true);
});
```
