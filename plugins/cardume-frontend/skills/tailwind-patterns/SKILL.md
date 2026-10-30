---
name: tailwind-patterns
description: "Tailwind CSS v4 with @theme tokens, container queries and dark mode. Use when writing Tailwind styles, migrating from v3 or setting up a Tailwind design system."
allowed-tools: Read Write Edit Glob Grep
---

# Tailwind CSS Patterns (v4)

> Modern utility-first CSS with CSS-native configuration.

---

## 1. Tailwind v4 Architecture

### What Changed from v3

| v3 (Legacy) | v4 (Current) |
|-------------|--------------|
| `@tailwind base/components/utilities` | Single `@import "tailwindcss";` |
| `tailwind.config.js` (required) | CSS-first `@theme`; JS config optional via `@config` (compat) |
| `content: [...]` globs | Automatic source detection (+ `@source` for extras) |
| `tailwindcss` PostCSS plugin | `@tailwindcss/postcss` (PostCSS) or `@tailwindcss/vite` (Vite) |
| `plugins: [...]` in config | `@plugin "pkg";` in CSS (compat for JS plugins) |
| `addUtilities()` in a plugin | `@utility name { ... }` in CSS |
| `darkMode: 'class'` | `@custom-variant dark (...)` in CSS |
| `@container-queries` plugin | Container queries built in |
| `@apply` directive | Still works; prefer components |

### v4 Core Concepts

| Concept | Description |
|---------|-------------|
| **CSS-first** | Configuration in CSS, not JavaScript |
| **New engine** | Ground-up rewrite; much faster full and incremental builds |
| **Build integrations** | Vite plugin (`@tailwindcss/vite`), PostCSS plugin (`@tailwindcss/postcss`), or CLI |
| **CSS Variables** | All theme tokens exposed as `--*` vars |

### Core Directives

| Directive | Purpose |
|-----------|---------|
| `@import "tailwindcss";` | Load Tailwind (replaces the three `@tailwind` lines) |
| `@theme { ... }` | Define design tokens (colors, fonts, breakpoints) |
| `@source "../path";` | Add sources automatic detection misses |
| `@utility name { ... }` | Custom utility that works with variants (`hover:`, `lg:`) |
| `@custom-variant name (...);` | Custom variant (e.g. class-based `dark:`) |
| `@variant dark { ... }` | Apply a variant inside your own CSS |
| `@reference "../app.css";` | Use `@apply` in CSS modules / component `<style>` without duplicating output |
| `@plugin "pkg";` / `@config "file";` | Load legacy JS plugins / config (v3 compatibility) |

### Setup

```
/* app.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";

@utility tab-4 {
  tab-size: 4;
}
```

- **Vite:** add `tailwindcss()` from `@tailwindcss/vite` to `plugins`
- **PostCSS** (Next.js, etc.): `postcss.config.mjs` → `plugins: { "@tailwindcss/postcss": {} }`

---

## 2. CSS-Based Configuration

### Theme Definition

```
@import "tailwindcss";

@theme {
  /* Colors - use semantic names */
  --color-primary: oklch(0.7 0.15 250);
  --color-surface: oklch(0.98 0 0);
  --color-surface-dark: oklch(0.15 0 0);
  
  /* Spacing scale */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 2rem;
  
  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

### When to Extend vs Override

| Action | Use When |
|--------|----------|
| **Extend** | Adding new values alongside defaults |
| **Override** | Replacing default scale entirely |
| **Semantic tokens** | Project-specific naming (primary, surface) |

---

## 3. Container Queries (v4 Native)

### Breakpoint vs Container

| Type | Responds To |
|------|-------------|
| **Breakpoint** (`md:`) | Viewport width |
| **Container** (`@container`) | Parent element width |

### Container Query Usage

| Pattern | Classes |
|---------|---------|
| Define container | `@container` on parent |
| Container breakpoint | `@sm:`, `@md:`, `@lg:` on children |
| Named containers | `@container/card` for specificity |

### When to Use

| Scenario | Use |
|----------|-----|
| Page-level layouts | Viewport breakpoints |
| Component-level responsive | Container queries |
| Reusable components | Container queries (context-independent) |

---

## 4. Responsive Design

### Breakpoint System

| Prefix | Min Width | Target |
|--------|-----------|--------|
| (none) | 0px | Mobile-first base |
| `sm:` | 640px | Large phone / small tablet |
| `md:` | 768px | Tablet |
| `lg:` | 1024px | Laptop |
| `xl:` | 1280px | Desktop |
| `2xl:` | 1536px | Large desktop |

### Mobile-First Principle

1. Write mobile styles first (no prefix)
2. Add larger screen overrides with prefixes
3. Example: `w-full md:w-1/2 lg:w-1/3`

---

## 5. Dark Mode

### Configuration Strategies

| Method | Behavior | Use When |
|--------|----------|----------|
| Default (`prefers-color-scheme`) | Follows system preference, no config | No user control |
| Class | `@custom-variant dark (&:where(.dark, .dark *));` | Manual theme switcher (`<html class="dark">`) |
| Data attribute | `@custom-variant dark (&:where([data-theme=dark], [data-theme=dark] *));` | Multi-theme setups |

> v4 has no `darkMode` config key: override the `dark` variant in CSS with `@custom-variant` (after `@import "tailwindcss";`).

### Dark Mode Pattern

| Element | Light | Dark |
|---------|-------|------|
| Background | `bg-white` | `dark:bg-zinc-900` |
| Text | `text-zinc-900` | `dark:text-zinc-100` |
| Borders | `border-zinc-200` | `dark:border-zinc-700` |

---

## 6. Modern Layout Patterns

### Flexbox Patterns

| Pattern | Classes |
|---------|---------|
| Center (both axes) | `flex items-center justify-center` |
| Vertical stack | `flex flex-col gap-4` |
| Horizontal row | `flex gap-4` |
| Space between | `flex justify-between items-center` |
| Wrap grid | `flex flex-wrap gap-4` |

### Grid Patterns

| Pattern | Classes |
|---------|---------|
| Auto-fit responsive | `grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))]` |
| Asymmetric (Bento) | `grid grid-cols-3 grid-rows-2` with spans |
| Sidebar layout | `grid grid-cols-[auto_1fr]` |

> **Note:** Prefer asymmetric/Bento layouts over symmetric 3-column grids.

---

## 7. Modern Color System

### OKLCH vs RGB/HSL

| Format | Advantage |
|--------|-----------|
| **OKLCH** | Perceptually uniform, better for design |
| **HSL** | Intuitive hue/saturation |
| **RGB** | Legacy compatibility |

### Color Token Architecture

| Layer | Example | Purpose |
|-------|---------|---------|
| **Primitive** | `--blue-500` | Raw color values |
| **Semantic** | `--color-primary` | Purpose-based naming |
| **Component** | `--button-bg` | Component-specific |

---

## 8. Typography System

### Font Stack Pattern

| Type | Recommended |
|------|-------------|
| Sans | `'Inter', 'SF Pro', system-ui, sans-serif` |
| Mono | `'JetBrains Mono', 'Fira Code', monospace` |
| Display | `'Outfit', 'Poppins', sans-serif` |

### Type Scale

| Class | Size | Use |
|-------|------|-----|
| `text-xs` | 0.75rem | Labels, captions |
| `text-sm` | 0.875rem | Secondary text |
| `text-base` | 1rem | Body text |
| `text-lg` | 1.125rem | Lead text |
| `text-xl`+ | 1.25rem+ | Headings |

---

## 9. Animation & Transitions

### Built-in Animations

| Class | Effect |
|-------|--------|
| `animate-spin` | Continuous rotation |
| `animate-ping` | Attention pulse |
| `animate-pulse` | Subtle opacity pulse |
| `animate-bounce` | Bouncing effect |

### Transition Patterns

| Pattern | Classes |
|---------|---------|
| All properties | `transition-all duration-200` |
| Specific | `transition-colors duration-150` |
| With easing | `ease-out` or `ease-in-out` |
| Hover effect | `hover:scale-105 transition-transform` |

---

## 10. Component Extraction

### When to Extract

| Signal | Action |
|--------|--------|
| Same class combo 3+ times | Extract component |
| Complex state variants | Extract component |
| Design system element | Extract + document |

### Extraction Methods

| Method | Use When |
|--------|----------|
| **React/Vue component** | Dynamic, JS needed |
| **@apply in CSS** | Static, no JS needed |
| **Design tokens** | Reusable values |

---

## 11. Anti-Patterns

| Don't | Do |
|-------|-----|
| Arbitrary values everywhere | Use design system scale |
| `!important` | Fix specificity properly |
| Inline `style=` | Use utilities |
| Duplicate long class lists | Extract component |
| `@tailwind` directives / `darkMode` config in v4 | `@import "tailwindcss"` + `@custom-variant dark` |
| Mix v3 config with v4 | Migrate to CSS-first (`@config`/`@plugin` only as a bridge) |
| Use `@apply` heavily | Prefer components |

---

## 12. Performance Principles

| Principle | Implementation |
|-----------|----------------|
| **Purge unused** | Automatic source detection in v4 (`@source` for extras) |
| **Avoid dynamism** | No template string classes |
| **Use the native integration** | `@tailwindcss/vite` for Vite; `@tailwindcss/postcss` elsewhere |
| **Cache builds** | CI/CD caching |

---

> **Remember:** Tailwind v4 is CSS-first. Embrace CSS variables, container queries, and native features. The config file is now optional.
