---
name: design-flow-landing-hero
plugins: ["../..", "../../../cardume-core"]
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our landing page hero looks bland and generic. Redesign it so it feels like a real product, not a template. It's for a time-tracking tool for freelance designers.

```html
<section class="hero">
  <h1>Welcome to TimeApp</h1>
  <p>The best time tracking solution for everyone. Track your time easily.</p>
  <button>Get Started</button>
  <button>Learn More</button>
</section>
<style>
.hero { text-align:center; padding:50px; background: linear-gradient(90deg,#667eea,#764ba2); color:white; }
.hero button { padding:10px 20px; margin:5px; border-radius:20px; }
</style>
```
