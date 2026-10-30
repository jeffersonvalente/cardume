---
name: frontend-design
description: "Design principles for web UI: constraints, layout, color, typography, motion, anti-cliché checks. Use when choosing a visual direction or restyling a page or component."
allowed-tools: Read Write Edit Glob Grep Bash
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# Frontend Design System

> **Philosophy:** Every pixel has purpose. Restraint is luxury. User psychology drives decisions.
> **Core Principle:** Think, don't memorize. Ask, don't assume.

---

## Reference Files: Read Selectively

Start with `ux-psychology.md`; read the others only when the task touches their area, to keep context small.

| File | When to Read |
|------|--------------|
| [ux-psychology.md](ux-psychology.md) | First, for any design task |
| [color-system.md](color-system.md) | Color/palette decisions |
| [typography-system.md](typography-system.md) | Font selection/pairing |
| [visual-effects.md](visual-effects.md) | Glassmorphism, shadows, gradients |
| [animation-guide.md](animation-guide.md) | Animation needed |
| [motion-graphics.md](motion-graphics.md) | Lottie, GSAP, 3D |
| [decision-trees.md](decision-trees.md) | Context templates |

---

## Audit Scripts

Run these for audits (no need to read the source):

| Command | Purpose | Usage |
|---------|---------|-------|
| `cardume-ux-audit` | UX psychology & accessibility audit | `cardume-ux-audit <project_path>` |
| `cardume-accessibility-checker` | Accessibility checks | `cardume-accessibility-checker <project_path>` |

---

## Ask Before Assuming

If the request is open-ended, ask instead of falling back on favorite defaults — the defaults are what make AI-generated UI look the same.

### When the prompt is vague, ask

**Color not specified?**
> "What color palette do you prefer? (blue/green/orange/neutral/other?)"

**Style not specified?**
> "What style are you going for? (minimal/bold/retro/futuristic/organic?)"

**Layout not specified?**
> "Do you have a layout preference? (single column/grid/asymmetric/full-width?)"

### Default tendencies to avoid (anti-safe-harbor)

| AI Default Tendency | Why It's Bad | Think Instead |
|---------------------|--------------|---------------|
| **Bento Grids (Modern Cliché)** | Used in every AI design | Why does this content need a grid? |
| **Hero Split (Left/Right)** | Predictable | How about Massive Typography or Vertical Narrative? |
| **Mesh/Aurora Gradients** | The "new" lazy background | What's a bolder color pairing? |
| **Glassmorphism** | AI's idea of "premium" | How about solid, high-contrast flat? |
| **Deep Cyan / Fintech Blue** | Safe harbor from the purple ban | Why not Red, Black, or Neon Green? |
| **"Orchestrate / Empower"** | AI-generated copywriting | How would a human say this? |
| Dark background + neon glow | Overused, "AI look" | What does the brand actually need? |
| **Rounded everything** | Generic/Safe | Where can I use sharp, brutalist edges? |

> Each "safe" structure moves the result closer to a generic template, so take deliberate risks.

---

## 1. Constraint Analysis (first)

Before any design work, answer these or ask the user:

| Constraint | Question | Why It Matters |
|------------|----------|----------------|
| **Timeline** | How much time? | Determines complexity |
| **Content** | Ready or placeholder? | Affects layout flexibility |
| **Brand** | Existing guidelines? | May dictate colors/fonts |
| **Tech** | What stack? | Affects capabilities |
| **Audience** | Who exactly? | Drives all visual decisions |

### Audience → Design Approach

| Audience | Think About |
|----------|-------------|
| **Gen Z** | Bold, fast, mobile-first, authentic |
| **Millennials** | Clean, minimal, value-driven |
| **Gen X** | Familiar, trustworthy, clear |
| **Boomers** | Readable, high contrast, simple |
| **B2B** | Professional, data-focused, trust |
| **Luxury** | Restrained elegance, whitespace |

---

## 2. UX Psychology Principles

### Core Laws (Internalize These)

| Law | Principle | Application |
|-----|-----------|-------------|
| **Hick's Law** | More choices = slower decisions | Limit options, use progressive disclosure |
| **Fitts' Law** | Bigger + closer = easier to click | Size CTAs appropriately |
| **Miller's Law** | ~7 items in working memory | Chunk content into groups |
| **Von Restorff** | Different = memorable | Make CTAs visually distinct |
| **Serial Position** | First/last remembered most | Key info at start/end |

### Emotional Design Levels

```
VISCERAL (instant)  → First impression: colors, imagery, overall feel
BEHAVIORAL (use)    → Using it: speed, feedback, efficiency
REFLECTIVE (memory) → After: "I like what this says about me"
```

### Trust Building

- Security indicators on sensitive actions
- Social proof where relevant
- Clear contact/support access
- Consistent, professional design
- Transparent policies

---

## 3. Layout Principles

### Golden Ratio (φ = 1.618)

```
Use for proportional harmony:
├── Content : Sidebar = roughly 62% : 38%
├── Each heading size = previous × 1.618 (for dramatic scale)
├── Spacing can follow: sm → md → lg (each × 1.618)
```

### 8-Point Grid Concept

```
All spacing and sizing in multiples of 8:
├── Tight: 4px (half-step for micro)
├── Small: 8px
├── Medium: 16px
├── Large: 24px, 32px
├── XL: 48px, 64px, 80px
└── Adjust based on content density
```

### Key Sizing Principles

| Element | Consideration |
|---------|---------------|
| **Touch targets** | Minimum comfortable tap size |
| **Buttons** | Height based on importance hierarchy |
| **Inputs** | Match button height for alignment |
| **Cards** | Consistent padding, breathable |
| **Reading width** | 45-75 characters optimal |

---

## 4. Color Principles

### 60-30-10 Rule

```
60% → Primary/Background (calm, neutral base)
30% → Secondary (supporting areas)
10% → Accent (CTAs, highlights, attention)
```

### Color Psychology (For Decision Making)

| If You Need... | Consider Hues | Avoid |
|----------------|---------------|-------|
| Trust, calm | Blue family | Aggressive reds |
| Growth, nature | Green family | Industrial grays |
| Energy, urgency | Orange, red | Passive blues |
| Luxury, creativity | Deep Teal, Gold, Emerald | Cheap-feeling brights |
| Clean, minimal | Neutrals | Overwhelming color |

### Selection Process

1. **What's the industry?** (narrows options)
2. **What's the emotion?** (picks primary)
3. **Light or dark mode?** (sets foundation)
4. **Ask the user** if not specified

For detailed color theory: [color-system.md](color-system.md)

---

## 5. Typography Principles

### Scale Selection

| Content Type | Scale Ratio | Feel |
|--------------|-------------|------|
| Dense UI | 1.125-1.2 | Compact, efficient |
| General web | 1.25 | Balanced (most common) |
| Editorial | 1.333 | Readable, spacious |
| Hero/display | 1.5-1.618 | Dramatic impact |

### Pairing Concept

```
Contrast + Harmony:
├── Different enough for hierarchy
├── Similar enough for cohesion
└── Usually: display + neutral, or serif + sans
```

### Readability Rules

- **Line length**: 45-75 characters optimal
- **Line height**: 1.4-1.6 for body text
- **Contrast**: Check WCAG requirements
- **Size**: 16px+ for body on web

For detailed typography: [typography-system.md](typography-system.md)

---

## 6. Visual Effects Principles

### Glassmorphism (When Appropriate)

```
Key properties:
├── Semi-transparent background
├── Backdrop blur
├── Subtle border for definition
└── Note: standard blue/white glassmorphism is a modern cliché. Use it boldly or not at all.
```

### Shadow Hierarchy

```
Elevation concept:
├── Higher elements = larger shadows
├── Y-offset > X-offset (light from above)
├── Multiple layers = more realistic
└── Dark mode: may need glow instead
```

### Gradient Usage

```
Harmonious gradients:
├── Adjacent colors on wheel (analogous)
├── OR same hue, different lightness
├── Avoid harsh complementary pairs
├── Avoid mesh/aurora gradients (floating blobs)
└── Vary strongly from project to project
```

For complete effects guide: [visual-effects.md](visual-effects.md)

---

## 7. Animation Principles

### Timing Concept

```
Duration based on:
├── Distance (further = longer)
├── Size (larger = slower)
├── Importance (critical = clear)
└── Context (urgent = fast, luxury = slow)
```

### Easing Selection

| Action | Easing | Why |
|--------|--------|-----|
| Entering | Ease-out | Decelerate, settle in |
| Leaving | Ease-in | Accelerate, exit |
| Emphasis | Ease-in-out | Smooth, deliberate |
| Playful | Bounce | Fun, energetic |

### Performance

- Animate only transform and opacity
- Respect reduced-motion preference
- Test on low-end devices

For animation patterns: [animation-guide.md](animation-guide.md), for advanced: [motion-graphics.md](motion-graphics.md)

---

## 8. "Wow Factor" Checklist

### Premium Indicators

- [ ] Generous whitespace (luxury = breathing room)
- [ ] Subtle depth and dimension
- [ ] Smooth, purposeful animations
- [ ] Attention to detail (alignment, consistency)
- [ ] Cohesive visual rhythm
- [ ] Custom elements (not all defaults)

### Trust Builders

- [ ] Security cues where appropriate
- [ ] Social proof / testimonials
- [ ] Clear value proposition
- [ ] Professional imagery
- [ ] Consistent design language

### Emotional Triggers

- [ ] Hero that evokes intended emotion
- [ ] Human elements (faces, stories)
- [ ] Progress/achievement indicators
- [ ] Moments of delight

---

## 9. Anti-Patterns (What NOT to Do)

### ❌ Lazy Design Indicators

- Default system fonts without consideration
- Stock imagery that doesn't match
- Inconsistent spacing
- Too many competing colors
- Walls of text without hierarchy
- Inaccessible contrast

### ❌ AI Tendency Patterns (avoid)

- **Same colors every project**
- **Dark + neon as default**
- **Purple/violet everything (Purple Ban)**
- **Bento grids for simple landing pages**
- **Mesh Gradients & Glow Effects**
- **Same layout structure / Vercel clone**
- **Not asking user preferences**

### ❌ Dark Patterns (Unethical)

- Hidden costs
- Fake urgency
- Forced actions
- Deceptive UI
- Confirmshaming

---

## 10. Decision Process Summary

```
For every design task:

1. CONSTRAINTS
   └── What's the timeline, brand, tech, audience?
   └── If unclear → ask

2. CONTENT
   └── What content exists?
   └── What's the hierarchy?

3. STYLE DIRECTION
   └── What's appropriate for context?
   └── If unclear → ask (don't default)

4. EXECUTION
   └── Apply principles above
   └── Check against anti-patterns

5. REVIEW
   └── "Does this serve the user?"
   └── "Is this different from my defaults?"
   └── "Would I be proud of this?"
```

---

## Reference Files

For deeper guidance on specific areas:

- [color-system.md](color-system.md) - Color theory and selection process
- [typography-system.md](typography-system.md) - Font pairing and scale decisions
- [visual-effects.md](visual-effects.md) - Effects principles and techniques
- [animation-guide.md](animation-guide.md) - Motion design principles
- [motion-graphics.md](motion-graphics.md) - Advanced: Lottie, GSAP, SVG, 3D, Particles
- [decision-trees.md](decision-trees.md) - Context-specific templates
- [ux-psychology.md](ux-psychology.md) - User psychology deep dive

---

## Related Skills

| Skill | When to Use |
|-------|-------------|
| **frontend-design** (this) | Before coding - Learn design principles (color, typography, UX psychology) |
| **design-flow** (`/cardume-frontend:design-flow`) | The main UI flow — shape, craft, critique, audit, polish |
| **[web-design-guidelines](../web-design-guidelines/SKILL.md)** | After coding - Audit for accessibility, performance, and best practices |

## Post-Design Workflow

After implementing your design, run the audit:

```
1. DESIGN   → Read frontend-design principles ← (this skill)
2. CODE     → Implement the design
3. AUDIT    → Run web-design-guidelines review
4. FIX      → Address findings from audit
```

> **Next Step:** After coding, use the `web-design-guidelines` skill to audit your implementation for accessibility, focus states, animations, and performance issues.

---

> **Remember:** Design is thinking, not copying. Every project deserves fresh consideration based on its context and users — avoid the Modern SaaS safe harbor.
