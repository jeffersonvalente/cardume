---
name: spec-property-invariant
tags: [trigger, spec]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Let's specify the new discount engine for our Python checkout service before building it: line discounts (percentage or fixed), a cart-level coupon applied after line discounts, and totals rounded to cents. The order total must never go below zero and must always equal the sum of discounted lines minus the coupon. Write the spec.
