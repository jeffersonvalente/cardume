# Frontend Design Playbook (frontend-specialist)

Detailed design-process material for the `frontend-specialist` agent. Read it when doing visual/UI design work (not for pure logic/architecture tasks). Core rules (ask before assuming, no default UI library, purple ban, anti-safe-harbor) live in the agent body and `frontend-design/SKILL.md`.

## Deep Design Thinking (before any design)

Complete this analysis before designing; skipping it is the main reason output ends up generic.

### Step 1: Self-Questioning (internal — don't show to user)

**Answer these in your thinking:**

```
🔍 CONTEXT ANALYSIS:
├── What is the sector? → What emotions should it evoke?
├── Who is the target audience? → Age, tech-savviness, expectations?
├── What do competitors look like? → What should I NOT do?
└── What is the soul of this site/app? → In one word?

🎨 DESIGN IDENTITY:
├── What will make this design memorable?
├── What unexpected element can I use?
├── How do I avoid standard layouts?
├── Modern cliché check: Am I using Bento Grid or Mesh Gradient? (If yes → reconsider)
└── Will I remember this design in a year?

📐 LAYOUT HYPOTHESIS:
├── How can the Hero be different? (Asymmetry? Overlay? Split?)
├── Where can I break the grid?
├── Which element can be in an unexpected place?
└── Can the Navigation be unconventional?

🎭 EMOTION MAPPING (from ux-psychology.md):
├── Primary emotion: [Trust/Energy/Calm/Luxury/Fun]
├── Color implication: [Blue/Orange/Green/Black-Gold/Bright]
├── Typography character: [Serif=Classic, Sans=Modern, Display=Bold]
└── Animation mood: [Subtle=Professional, Dynamic=Energetic]
```

- **Decide to break conventions yourself:** As a senior UI architect, reject safe topologies without waiting to be told. A "Standard Split" delivered out of caution is a missed opportunity.
- **Subvert expectations:** In every new layout, aim to place elements somewhere other than where the user (or your own habits) would expect them.

---

### Deep Design Thinking — Phase 1 output

Before writing CSS, document your thought process along this flow:

#### 1. Modern cliché scan (anti-safe-harbor)

- "Am I defaulting to 'Left Text / Right Visual' because it feels balanced?" → Choose a different structure.
- "Am I using Bento Grids to organize content safely?" → Break the grid.
- "Am I using standard SaaS fonts and 'safe' color pairs?" → Rethink the palette.

#### 2. Topological hypothesis

Pick a direction and commit:

- **[ ] FRAGMENTATION:** Break the page into overlapping layers with no strict vertical/horizontal logic.
- **[ ] TYPOGRAPHIC BRUTALISM:** Text is 80% of the visual weight; images are artifacts behind content.
- **[ ] ASYMMETRIC TENSION (90/10):** Create visual conflict by pushing everything to an extreme corner.
- **[ ] CONTINUOUS STREAM:** No sections, just a flowing narrative of fragments.

---

### Design Commitment (output)

_Present this block to the user before code._

```markdown
🎨 DESIGN COMMITMENT: [RADICAL STYLE NAME]

- **Topological Choice:** (How did I move away from the 'Standard Split' habit?)
- **Risk Factor:** (What did I do that might be considered 'too far'?)
- **Readability Conflict:** (Did I intentionally challenge the eye for artistic merit?)
- **Cliché Liquidation:** (Which 'Safe Harbor' elements did I explicitly remove?)
```

### Step 2: Dynamic User Questions (based on analysis)

**After self-questioning, ask the user specific questions:**

```
❌ WRONG (Generic):
- "Do you have a color preference?"
- "What kind of design would you like?"

✅ CORRECT (Based on context analysis):
- "For [Sector], [Color1] or [Color2] are typical.
   Does one of these fit your vision, or should we take a different direction?"
- "Your competitors use [X layout].
   To differentiate, we could try [Y alternative]. What do you think?"
- "[Target audience] usually expects [Z feature].
   Should we include this or stick to a more minimal approach?"
```

### Step 3: Design Hypothesis & Style Commitment

**After the user answers, declare your approach. Avoid "Modern SaaS" as a style — it is the default you are trying to move past.**

```
🎨 DESIGN COMMITMENT (ANTI-SAFE HARBOR):
- Selected Radical Style: [Brutalist / Neo-Retro / Swiss Punk / Liquid Digital / Bauhaus Remix]
- Why this style? → How does it break sector clichés?
- Risk Factor: [What unconventional decision did I take? e.g., No borders, Horizontal scroll, Massive Type]
- Modern Cliché Scan: [Bento? No. Mesh Gradient? No. Glassmorphism? No.]
- Palette: [e.g., High Contrast Red/Black - NOT Cyan/Blue]
```

### The Modern SaaS "Safe Harbor" (avoid as defaults)

AI-generated designs tend to fall back on these popular elements. Don't use them as defaults:

1. **The "Standard Hero Split"**: Left content / right image or animation. It is the most overused layout.
2. **Bento Grids**: Use only for genuinely complex data, not as the default for landing pages.
3. **Mesh/Aurora Gradients**: Avoid floating colored blobs in the background.
4. **Glassmorphism**: Blur + thin border is not automatically "premium"; it reads as an AI cliché.
5. **Deep Cyan / Fintech Blue**: The "safe" escape palette for fintech. Consider bolder options like red, black, or neon green.
6. **Generic Copy**: Avoid words like "Orchestrate", "Empower", "Elevate", or "Seamless".

> A predictable layout structure is the clearest sign the design fell back to a template.

---

### Layout Diversification

**Move past the "Split Screen" habit. Alternative structures:**

- **Massive Typographic Hero**: Center the headline, make it 300px+, and build the visual _behind_ or _inside_ the letters.
- **Experimental Center-Staggered**: Every element (H1, P, CTA) has a different horizontal alignment (e.g., L-R-C-L).
- **Layered Depth (Z-axis)**: Visuals overlap the text, making it partially obscured but artistically deep.
- **Vertical Narrative**: No "above the fold" hero; the story starts immediately with a vertical flow of fragments.
- **Extreme Asymmetry (90/10)**: Compress everything to one edge, leaving 90% of the screen as negative space for tension.

---

### No Standard / Cliché Designs

Aim for designs that don't look like every other website: standard templates, typical layouts, common color schemes, and overused patterns are what to avoid.

**No memorized patterns:**

- Don't reuse structures straight from training data
- Don't default to "what you've seen before"
- Create a fresh design for each project

**Visual style variety:**

- Don't use soft, rounded shapes by default for everything.
- Explore sharp, geometric, and minimalist edges.
- **Avoid the "safe boredom" zone (4px–8px radius):**
    - Applying `rounded-md` (6–8px) to everything looks generic.
    - Commit to an end of the range:
        - **0px–2px** for Tech, Luxury, Brutalist (sharp/crisp).
        - **16px–32px** for Social, Lifestyle, Bento (friendly/soft).
    - _Make a choice rather than sitting in the middle._
- Don't shy away from aggressive, sharp, or technical styles when they fit.
- Give each project its own geometry: one sharp, one rounded, one organic, one brutalist.

**Active animation & visual depth:**

- A fully static design feels lifeless; the UI should feel alive through movement.
- **Layered animations:**
    - **Reveal:** Sections and main elements get scroll-triggered (staggered) entrance animations.
    - **Micro-interactions:** Clickable/hoverable elements give physical feedback (`scale`, `translate`, `glow-pulse`).
    - **Spring physics:** Prefer organic, spring-like motion over linear easing.
- **Visual depth:**
    - Go beyond flat colors/shadows: use overlapping elements, parallax layers, and grain textures.
    - Avoid mesh gradients and glassmorphism unless the user requests them.
- **Performance constraints for motion:**
    - Animate only GPU-accelerated properties (`transform`, `opacity`).
    - Use `will-change` strategically for heavy animations.
    - Always support `prefers-reduced-motion` — some users get motion sickness.

**Every design should achieve this trinity:**

1. Sharp/clean geometry (committed, not middling)
2. Bold color palette (no purple)
3. Fluid animation & modern effects (premium feel)

### Phase 2: Design Decision

Declare your design choices before coding.

**Think through these decisions (don't copy from templates):**

1. **What emotion/purpose?** → Finance=Trust, Food=Appetite, Fitness=Power
2. **What geometry?** → Sharp for luxury/power, Rounded for friendly/organic
3. **What colors?** → Based on ux-psychology.md emotion mapping (no purple)
4. **What makes it unique?** → How does this differ from a template?

**Format to use in your thought process:**

> 🎨 **DESIGN COMMITMENT:**
>
> - **Geometry:** [e.g., Sharp edges for premium feel]
> - **Typography:** [e.g., Serif Headers + Sans Body]
>     - _Ref:_ Scale from `typography-system.md`
> - **Palette:** [e.g., Teal + Gold - Purple Ban ✅]
>     - _Ref:_ Emotion mapping from `ux-psychology.md`
> - **Effects/Motion:** [e.g., Subtle shadow + ease-out]
>     - _Ref:_ Principle from `visual-effects.md`, `animation-guide.md`
> - **Layout uniqueness:** [e.g., Asymmetric 70/30 split, NOT centered hero]

**Rules:**

1. **Stick to the recipe:** If you pick "Futuristic HUD", don't add soft rounded corners.
2. **Commit fully:** Don't mix five styles.
3. **No defaulting:** Pick concrete values rather than falling back to defaults.
4. **Cite sources:** Check your choices against the rules in the `frontend-design` color/typography/effects reference files instead of guessing.

Apply decision trees from the `frontend-design` skill for logic flow.

### Phase 3: The Maestro Auditor (final self-audit)

Run this self-audit before reporting the task complete. If any trigger applies, rework the affected part.

| Rejection Trigger    | Description (Why it fails)                          | Corrective Action                                                    |
| :------------------- | :-------------------------------------------------- | :------------------------------------------------------------------- |
| **The "Safe Split"** | Using `grid-cols-2` or 50/50, 60/40, 70/30 layouts. | Switch to `90/10`, `100% Stacked`, or `Overlapping`.                 |
| **The "Glass Trap"** | Using `backdrop-blur` without raw, solid borders.   | Remove blur. Use solid colors and raw borders (1px/2px).             |
| **The "Glow Trap"**  | Using soft gradients to make things "pop".          | Use high-contrast solid colors or grain textures.                    |
| **The "Bento Trap"** | Organizing content in safe, rounded grid boxes.     | Fragment the grid. Break alignment intentionally.                    |
| **The "Blue Trap"**  | Using any shade of default blue/teal as primary.    | Switch to Acid Green, Signal Orange, or Deep Red.                    |

> **Maestro rule:** If the layout could come straight from a Tailwind UI template, it needs another pass.

---

### Phase 4: Verification & Handover

- [ ] **Miller's Law** → Info chunked into 5-9 groups?
- [ ] **Von Restorff** → Key element visually distinct?
- [ ] **Cognitive Load** → Is the page overwhelming? Add whitespace.
- [ ] **Trust Signals** → Will new users trust this? (logos, testimonials, security)
- [ ] **Emotion-Color Match** → Does color evoke the intended feeling?

### Phase 4b: Execute

Build layer by layer:

1. HTML structure (semantic)
2. CSS/Tailwind (8-point grid)
3. Interactivity (states, transitions)

### Phase 5: Reality Check

Checking boxes is not the same as meeting the intent of the rules. Verify honestly before delivering.

**The "Template Test":**

| Question | Fail Answer | Pass Answer |
|----------|-------------|-------------|
| "Could this be a Vercel/Stripe template?" | "Well, it's clean..." | "No, this is unique to this brand." |
| "Would I scroll past this on Dribbble?" | "It's professional..." | "I'd stop and think 'how did they do that?'" |
| "Can I describe it without saying 'clean' or 'minimal'?" | "It's... clean corporate." | "It's brutalist with aurora accents and staggered reveals." |

**Self-deception patterns to avoid:**

- ❌ "I used a custom palette" → But it's still blue + white + orange (every SaaS ever)
- ❌ "I have hover effects" → But they're just `opacity: 0.8`
- ❌ "I used Inter font" → That's the default, not a choice
- ❌ "The layout is varied" → But it's still a 3-column equal grid
- ❌ "Border-radius is 16px" → Did you measure it or guess?

**Honest reality check:**

1. **Screenshot Test:** Would a designer say "another template" or "that's interesting"?
2. **Memory Test:** Will users remember this design tomorrow?
3. **Differentiation Test:** Can you name 3 things that make this different from competitors?
4. **Animation Proof:** Do things move, or is it static?
5. **Depth Proof:** Is there actual layering (shadows, overlap, texture) or is it flat?

> If you find yourself defending checklist compliance while the design looks generic, the design isn't done. The checklist serves the goal; the goal is something memorable.

---

### Spirit Over Checklist

Passing the checklist is not enough; the intent of the rules matters more.

| ❌ Self-Deception                                   | ✅ Honest Assessment         |
| --------------------------------------------------- | ---------------------------- |
| "I used a custom color" (but it's still blue-white) | "Is this palette memorable?" |
| "I have animations" (but just fade-in)              | "Would a designer say wow?"  |
| "Layout is varied" (but 3-column grid)              | "Could this be a template?"  |
