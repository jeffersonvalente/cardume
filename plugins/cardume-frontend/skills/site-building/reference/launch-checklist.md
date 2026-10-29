# Launch checklist

Run on the production build and, after DNS switch, on the production domain. Copy into `docs/launch-checklist.md` and tick items with evidence (command output, screenshot, URL).

## Metadata and SEO

- [ ] Unique `<title>` (~50–60 chars) and meta description (~150–160 chars) per page
- [ ] Open Graph (`og:title`, `og:description`, `og:image` 1200×630, `og:url`, `og:type`) and Twitter card (`summary_large_image`)
- [ ] Canonical URL on every page; one host (www or apex) and one trailing-slash style
- [ ] `sitemap.xml` generated, lists only canonical, indexable URLs; referenced in `robots.txt`
- [ ] `robots.txt` allows production; staging/preview deploys are `noindex`
- [ ] AI-crawler policy decided with the owner and written in `robots.txt` (e.g. training crawlers `GPTBot`, `ClaudeBot`, `Google-Extended` allowed or disallowed; search/answer agents such as `OAI-SearchBot`, `Claude-SearchBot` kept if AI-search visibility matters). `Google-Extended` does not affect Google Search; `llms.txt` is optional and ignored by Google Search
- [ ] Structured data valid (Organization / LocalBusiness subtype / Article / Product / BreadcrumbList as relevant) in Google's Rich Results Test
- [ ] One `h1` per page, logical heading order
- [ ] `hreflang` and `<html lang>` correct on multilingual sites
- [ ] `cardume-seo-checker <project_path>` passes; strategy reviewed by `seo-specialist` if ranking is a goal

## Assets and pages

- [ ] Favicon set (SVG + PNG fallbacks, apple-touch-icon) and web app manifest
- [ ] Custom 404 page with navigation and search/contact; 500 page or host error page branded
- [ ] Redirect map from every old indexed URL (301), tested; no redirect chains
- [ ] No lorem ipsum, no placeholder images left untracked (`docs/content-todo.md` empty or accepted)
- [ ] All images have `alt` (decorative `alt=""`), dimensions set, modern formats

## Performance and quality

- [ ] HTTPS everywhere, HSTS, no mixed content; HTTP redirects to HTTPS
- [ ] Core Web Vitals "good" thresholds (p75, mobile): LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1
- [ ] `cardume-lighthouse-audit <url>`: ≥ 90 in Performance, Accessibility, Best Practices and SEO on mobile
- [ ] `cardume-accessibility-checker <project_path>` clean; keyboard-only walkthrough done; WCAG 2.2 AA basics (contrast, focus visible, labels, target size)
- [ ] Broken-link scan (internal and external) clean
- [ ] Tested on a real phone plus current Chrome, Safari and Firefox

## Forms, consent and analytics

- [ ] Each form submitted on production; submission arrives where the handoff says; server-side validation rejects bad input; spam protection active
- [ ] No non-essential cookies or third-party requests before consent (check DevTools Application and Network tabs in a fresh profile)
- [ ] Reject works as easily as accept; preferences can be reopened from the footer
- [ ] Analytics fires after consent (or is cookieless by configuration); conversions recorded in the analytics real-time view
- [ ] Privacy policy published, linked in footer and near forms, matching the actual tools in use

## Launch and handoff

- [ ] Search Console (and Bing Webmaster Tools) verified, sitemap submitted
- [ ] Google Business Profile updated with the new URL (local businesses)
- [ ] Uptime monitor and form-failure alert configured
- [ ] Backups: repo is the source of truth; CMS content export scheduled; DNS records documented
- [ ] Domain, DNS, host, CMS, analytics and email accounts owned by the client; renewal dates recorded
- [ ] `docs/handoff.md` covers editing, deploying, where data goes, accounts, backups/restore, and open items
