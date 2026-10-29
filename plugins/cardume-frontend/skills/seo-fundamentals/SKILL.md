---
name: seo-fundamentals
description: "Applies SEO fundamentals: E-E-A-T, Core Web Vitals, technical SEO, meta tags, schema markup, and content structure. Use when auditing or improving search rankings, page metadata, sitemaps, or structured data."
allowed-tools: Read Glob Grep
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# SEO Fundamentals

> Principles for search engine visibility.

---

## 1. E-E-A-T Framework

| Principle | Signals |
|-----------|---------|
| **Experience** | First-hand knowledge, real examples |
| **Expertise** | Credentials, depth of knowledge |
| **Authoritativeness** | Backlinks, mentions, industry recognition |
| **Trustworthiness** | HTTPS, transparency, accurate info |

---

## 2. Core Web Vitals

| Metric | Target | Measures |
|--------|--------|----------|
| **LCP** | < 2.5s | Loading performance |
| **INP** | < 200ms | Interactivity |
| **CLS** | < 0.1 | Visual stability |

---

## 3. Technical SEO Principles

### Site Structure

| Element | Purpose |
|---------|---------|
| XML sitemap | Help crawling |
| robots.txt | Control access |
| Canonical tags | Prevent duplicates |
| HTTPS | Security signal |

### Performance

| Factor | Impact |
|--------|--------|
| Page speed | Core Web Vital |
| Mobile-friendly | Ranking factor |
| Clean URLs | Crawlability |

---

## 4. Content SEO Principles

### Page Elements

| Element | Best Practice |
|---------|---------------|
| Title tag | 50-60 chars, keyword front |
| Meta description | 150-160 chars, compelling |
| H1 | One per page, main keyword |
| H2-H6 | Logical hierarchy |
| Alt text | Descriptive, not stuffed |

### Content Quality

| Factor | Importance |
|--------|------------|
| Depth | Comprehensive coverage |
| Freshness | Regular updates |
| Uniqueness | Original value |
| Readability | Clear writing |

---

## 5. Schema Markup Types

| Type | Use |
|------|-----|
| Article | Blog posts, news |
| Organization | Company info |
| Person | Author profiles |
| Product | E-commerce |
| Review / AggregateRating | Ratings |
| BreadcrumbList | Navigation |

### Retired Rich Results (don't add markup expecting a SERP feature)

| Type | Status in Google Search |
|------|------------------------|
| HowTo | No longer shown (documentation removed Sept 2023) |
| FAQPage | Limited to government/health sites from Aug 2023; no longer shown from May 2026 |

> Keep FAQ content on the page when it helps users; the markup is harmless but earns no rich result. Google retires rich results periodically, so check the [Search documentation updates](https://developers.google.com/search/updates) before promising a feature. Validate markup with the Rich Results Test.

---

## 6. AI Content Guidelines

### What Google Looks For

| ✅ Do | ❌ Don't |
|-------|----------|
| AI draft + human edit | Publish raw AI content |
| Add original insights | Copy without value |
| Expert review | Skip fact-checking |
| Follow E-E-A-T | Keyword stuffing |

---

## 7. Ranking Factors (Prioritized)

| Priority | Factor |
|----------|--------|
| 1 | Quality, relevant content |
| 2 | Backlinks from authority sites |
| 3 | Page experience (Core Web Vitals) |
| 4 | Mobile optimization |
| 5 | Technical SEO fundamentals |

---

## 8. Measurement

| Metric | Tool |
|--------|------|
| Rankings | Search Console, Ahrefs |
| Traffic | Analytics |
| Core Web Vitals | PageSpeed Insights |
| Indexing | Search Console |
| Backlinks | Ahrefs, Semrush |

---

## Audit Script

| Command | Purpose | Usage |
|---------|---------|-------|
| `cardume-seo-checker` | SEO audit of pages in a project | `cardume-seo-checker <project_path>` |

---

> **Remember:** SEO is a long-term game. Quality content + technical excellence + patience = results.
