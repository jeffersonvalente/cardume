---
name: site-building
description: "Runs website delivery from brief to launch: sitemap, static-first stack, SEO, LGPD/GDPR consent, quality gates. Use when building a landing page, company site, portfolio, blog, docs site or small store."
allowed-tools: Read Write Edit Glob Grep Bash
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# Site Building

Runs a website project from the first question to the handoff. A website is mostly content, findability and trust; an application is mostly state and logic. This skill covers the first kind and delegates specialties to their owners so the guidance stays in one place.

## Site or application?

| Signal | Site (this skill) | Application (`app-builder`, `frontend-specialist`) |
|--------|-------------------|------------------------------------------------------|
| Users log in | No, or only an editor in a CMS | Yes, accounts and roles |
| Main job | Inform, persuade, get a contact or sale | Let users do work, manage data |
| Pages | Mostly the same for every visitor | Personalized, data-driven views |
| Back end | Form handler, CMS, hosted checkout | Custom API and database |

Mixed cases: build the site here and hand the app part (customer portal, booking engine with availability logic) to the application owners, linking the two.

## Reference map

Read only the file for the phase you are in.

| File | Read when |
|------|-----------|
| `reference/briefing-and-content.md` | Briefing, sitemap, content model, page/section patterns, copy and images |
| `reference/stack-and-deploy.md` | Choosing framework, CMS and hosting |
| `reference/compliance-forms-analytics.md` | Forms, LGPD/GDPR consent, privacy policy, analytics, i18n |
| `reference/launch-checklist.md` | Quality gates, launch day, handoff |

## Workflow

### 1. Brief

Ask what the request does not already answer, in one batched message, so the user is interrupted once:

1. **Goal:** what should a visit produce (call, booking request, sale, signup, credibility)?
2. **Audience:** who, where, on which devices; what they need to decide.
3. **Pages:** which pages exist or are expected; is there an old site to migrate?
4. **Content owner:** who writes and approves copy and photos, and who updates them later?
5. **CMS needs:** how often does content change, and who edits it (developer, non-technical staff)?
6. **Languages:** which, and is one primary?
7. **Brand assets:** logo, colors, fonts, photography, tone of voice; anything to avoid?
8. **Forms and integrations:** contact, booking, newsletter, WhatsApp, maps, payments, CRM; where should submissions go?
9. **Budget, hosting and domain:** recurring cost tolerance, existing host or domain registrar, deadline.

When the user wants speed, state assumptions instead of blocking ("Assuming Portuguese only, the owner edits copy twice a year, submissions go by email"). Record the brief in `docs/site-brief.md` so later phases can cite it.

### 2. Sitemap and content model

- Draft the sitemap as a tree with one primary goal per page and the call to action that serves it.
- Define content types for anything repeated (service, team member, post, case study, product) with their fields. This drives the CMS choice and the templates.
- If an old site exists, inventory its URLs now; every indexed URL needs a destination in the redirect map before launch.

Detail and page/section patterns: `reference/briefing-and-content.md`.

### 3. Stack decision

Pick the simplest stack that meets the brief, and write down why.

| Situation | Default | Reason |
|-----------|---------|--------|
| One-pager, rarely changes | Plain static HTML/CSS (+ a little JS) | Nothing to maintain or upgrade; any host serves it |
| Content site, blog, docs, portfolio, institutional | **Astro** | Ships zero JS by default, content collections, islands for the few interactive parts |
| Needs app-like features, auth areas, per-request data, ISR at scale | Next.js | Server rendering and incremental regeneration; cost is more JS and more moving parts |
| Docs site specifically | Astro Starlight (or the team's existing docs tool) | Search, navigation and i18n built in |
| Small storefront | Static site + hosted checkout (Stripe Payment Links, Shopify Buy Button) or Shopify itself | Payments, tax and PCI stay with the provider |

CMS: no CMS when the developer edits content or it changes rarely (Markdown in the repo is cheaper and versioned). Add a headless CMS when non-technical people edit often. Options and hosting trade-offs: `reference/stack-and-deploy.md`.

### 4. Design (hand off to design-flow)

Invoke the `cardume-frontend:design-flow` skill when visual work starts. Pass it the brief, sitemap, content model and brand assets. It runs its own setup, register choice (sites are usually the **brand** register) and gates (brief → direction → palette → mock → code); wait at those gates with the user rather than designing in parallel. Do not choose palette, typography or layout outside that flow; it owns the design law and UI code quality.

### 5. Build

- Mobile first, semantic HTML, one `h1` per page, landmarks (`header`, `nav`, `main`, `footer`).
- Templates per content type; components per section pattern. Keep content in collections or the CMS, not hard-coded in components.
- Images through the framework's image pipeline (AVIF/WebP, explicit `width`/`height`, `srcset`, lazy below the fold, eager plus `fetchpriority="high"` for the LCP image).
- Fonts: self-host, subset, `font-display: swap`, preload only the one or two critical files.
- Third-party scripts (chat widgets, maps, pixels) load after consent and after interaction where possible; each one costs performance and privacy.
- Forms, consent and analytics follow `reference/compliance-forms-analytics.md`.

### 6. Content and SEO

- Real copy from the brief, never lorem ipsum. When the owner has not supplied copy, draft specific text and mark it for review in `docs/content-todo.md`.
- Every image has meaningful `alt` text (empty `alt=""` only for decorative images).
- Per-page title and description, Open Graph and Twitter card tags, canonical URL, `sitemap.xml`, `robots.txt`, structured data matching the business type.
- AI crawlers: decide with the owner which to allow in `robots.txt`. Training crawlers (`GPTBot`, `ClaudeBot`, the `Google-Extended` token) are separate from search/answer agents (`OAI-SearchBot`, `Claude-SearchBot`); blocking `Google-Extended` does not affect Google Search. `llms.txt` is optional: Google Search ignores it and needs no special AI files.
- Local businesses: `LocalBusiness` (or a subtype) schema with name, address, phone and hours consistent with the Google Business Profile; a page per service and location when it serves real searches.
- Delegate strategy and audits to `seo-specialist` or the `seo-fundamentals` / `geo-fundamentals` skills; this skill only ensures the pieces are wired.

### 7. Quality gates

Run against a production build, not the dev server:

```bash
cardume-lighthouse-audit <preview-url>          # performance, a11y, best practices, SEO
cardume-accessibility-checker <project_path>    # WCAG issues in markup
cardume-seo-checker <project_path>              # meta, headings, alt, links
cardume-i18n-checker <project_path>             # multilingual sites only
```

Targets: Lighthouse ≥ 90 in every category on mobile; Core Web Vitals at the 75th percentile LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1; WCAG 2.2 AA basics (contrast, keyboard, focus visible, labels, target size). Fix failures or report them with a reason; a gate that was skipped is reported as skipped.

### 8. Launch

Work through `reference/launch-checklist.md` on the production domain: HTTPS, redirects from old URLs, sitemap submitted to Search Console, forms tested end to end, analytics firing only after consent, 404/500 pages, favicon/manifest, broken-link scan.

### 9. Handoff

Leave the owner able to run the site without you, in `docs/handoff.md`: how to edit content, how to deploy, where forms and analytics go, accounts and who owns them (domain, host, CMS, analytics, in the client's name), backup and restore, renewal dates, and the open items list.

## Delegation summary

| Need | Owner |
|------|-------|
| Visual direction, UI code quality | `cardume-frontend:design-flow` skill / `design-flow` agent |
| Framework depth, interactive islands, Next.js | `frontend-specialist` |
| SEO / AI-search strategy and audit | `seo-specialist`, `seo-fundamentals`, `geo-fundamentals` |
| Core Web Vitals regressions | `performance-optimizer`, `performance-profiling` |
| Translations and locale handling | `i18n-localization` |
| Web application parts | `app-builder`, `frontend-specialist` |

## Common failure modes

- Building before the brief: the sitemap and stack then get rebuilt when the real goal surfaces.
- Picking Next.js or a CMS by habit for a site that changes twice a year; the owner inherits upgrades and bills for nothing.
- Analytics or embedded maps/videos setting cookies before consent.
- Launching without the redirect map, losing the old site's rankings.
- Placeholder copy and stock photos that make a small business look like every other one.
- Accounts registered in the developer's name, leaving the owner locked out later.
