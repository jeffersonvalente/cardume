---
name: geo-fundamentals
description: "Optimizes content for citation in AI answer engines. Use when improving AI search visibility or running a GEO audit."
allowed-tools: Read Glob Grep
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# GEO Fundamentals

> Optimization for AI-powered search engines.

---

## 1. What is GEO?

**GEO** = Generative Engine Optimization

| Goal | Platform |
|------|----------|
| Be cited in AI responses | ChatGPT, Claude, Perplexity, Gemini |

### SEO vs GEO

| Aspect | SEO | GEO |
|--------|-----|-----|
| Goal | #1 ranking | AI citations |
| Platform | Google | AI engines |
| Metrics | Rankings, CTR | Citation rate |
| Focus | Keywords | Entities, data |

---

## 2. AI Engine Landscape

| Engine | Citation Style | Opportunity |
|--------|----------------|-------------|
| **Perplexity** | Numbered [1][2] | Highest citation rate |
| **ChatGPT** | Inline/footnotes | Custom GPTs |
| **Claude** | Contextual | Long-form content |
| **Gemini** | Sources section | SEO crossover |

---

## 3. Retrieval Factors

How AI engines tend to select content to cite (engines do not publish weights; treat these as qualitative signals):

| Factor | What helps |
|--------|------------|
| Semantic relevance | Directly answers the question in clear, self-contained passages |
| Authority signals | Named authors, credentials, reputable mentions and links |
| Freshness | Visible "last updated" dates, current facts |
| Crawlability | Server-rendered HTML the engine's crawler is allowed to fetch |
| Source diversity | Engines mix sources, so unique data and angles stand out |

---

## 4. Content That Gets Cited

| Element | Why It Works |
|---------|--------------|
| **Original statistics** | Unique, citable data |
| **Expert quotes** | Authority transfer |
| **Clear definitions** | Easy to extract |
| **Step-by-step guides** | Actionable value |
| **Comparison tables** | Structured info |
| **FAQ sections** | Direct answers |

---

## 5. GEO Content Checklist

### Content Elements

- [ ] Question-based titles
- [ ] Summary/TL;DR at top
- [ ] Original data with sources
- [ ] Expert quotes (name, title)
- [ ] FAQ section (3-5 Q&A)
- [ ] Clear definitions
- [ ] "Last updated" timestamp
- [ ] Author with credentials

### Technical Elements

- [ ] Article schema with dates
- [ ] Person schema for author
- [ ] FAQ content in plain HTML (FAQPage markup is optional: Google no longer shows FAQ rich results)
- [ ] Fast loading (< 2.5s)
- [ ] Clean HTML structure

---

## 6. Entity Building

| Action | Purpose |
|--------|---------|
| Google Knowledge Panel | Entity recognition |
| Wikipedia (if notable) | Authority source |
| Consistent info across web | Entity consolidation |
| Industry mentions | Authority signals |

---

## 7. AI Crawler Access

### Key AI User-Agents (robots.txt tokens)

| Vendor | Token | Purpose |
|--------|-------|---------|
| OpenAI | `GPTBot` | Crawls content that may be used for model training |
| OpenAI | `OAI-SearchBot` | Surfaces sites in ChatGPT search answers |
| OpenAI | `ChatGPT-User` | User-initiated fetches; robots.txt may not apply |
| Anthropic | `ClaudeBot` | Collects content that may be used for model training |
| Anthropic | `Claude-SearchBot` | Indexes content to improve Claude's search results |
| Anthropic | `Claude-User` | Fetches pages when a Claude user asks a question |
| Google | `Google-Extended` | Control token only (no separate crawler) for Gemini training/grounding; does not affect Google Search |
| Google | `Googlebot` | Google Search, including AI features in Search |
| Perplexity | `PerplexityBot` | Surfaces and links sites in Perplexity search results |
| Perplexity | `Perplexity-User` | User-initiated fetches; generally ignores robots.txt |

> Vendors add and rename agents; verify against their docs before shipping robots.txt: [OpenAI](https://developers.openai.com/api/docs/bots), [Anthropic](https://support.claude.com/en/articles/8896518), [Google](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers), [Perplexity](https://docs.perplexity.ai/guides/bots).

### Access Decision

| Strategy | When |
|----------|------|
| Allow search + user agents | Want AI citations (`OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`, user agents) |
| Block training agents only | Opt out of training (`GPTBot`, `ClaudeBot`, `Google-Extended`) while staying citable |
| Selective | Allow some, block others per vendor |

---

## 8. Measurement

| Metric | How to Track |
|--------|--------------|
| AI citations | Manual monitoring |
| "According to [Brand]" mentions | Search in AI |
| Competitor citations | Compare share |
| AI-referred traffic | UTM parameters |

---

## 9. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Publish without dates | Add timestamps |
| Vague attributions | Name sources |
| Skip author info | Show credentials |
| Thin content | Comprehensive coverage |

---

> **Remember:** AI cites content that's clear, authoritative, and easy to extract. Be the best answer.

---

## Script

| Command | Purpose | Command |
|--------|---------|---------|
| `cardume-geo-checker` | GEO audit (AI citation readiness) | `cardume-geo-checker <project_path>` |

