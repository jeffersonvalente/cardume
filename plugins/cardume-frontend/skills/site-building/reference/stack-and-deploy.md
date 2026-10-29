# Stack, CMS and deployment

Prefer stable concepts over pinned versions: check the current major version and its official starter when scaffolding. At the time of writing the current majors are Astro 6 and Next.js 16; confirm on astro.build and nextjs.org.

Disclosure: Astro's company joined Cloudflare in January 2026 (<https://astro.build/blog/joining-cloudflare/>). Astro stays MIT-licensed and supports other hosts; recommend it on technical merit and keep the host choice independent.

## Framework

| Option | Choose when | Avoid when |
|--------|-------------|------------|
| Plain static HTML/CSS | One-pager or a handful of pages, developer-maintained, rarely changes | Repeated content types, many pages, multiple languages |
| **Astro** (default for content sites) | Institutional sites, blogs, portfolios, docs, marketing; mostly static with a few interactive islands | Heavy client state, logged-in areas |
| Astro Starlight | Documentation sites | Marketing sites (too opinionated) |
| Next.js | App-like features (auth areas, personalized pages, per-request data), very large catalogs needing ISR, team already on React/Next | A brochure site: more JS, more upgrades, more hosting coupling |
| Eleventy / Hugo | Team already uses them; very large static content sets (Hugo builds fast) | Need for component islands with a modern UI framework |
| Hosted builders (Webflow, WordPress managed) | The owner insists on visual editing without developers and accepts platform lock-in | Performance and code ownership are priorities |

If the project already has a stack, keep it unless it blocks the brief; migrations are a separate decision for the user.

For a Next.js marketing site, the `app-builder` skill's `nextjs-static` template is a starting point; for Next.js depth use `frontend-specialist`.

## CMS

| Option | Type | Good for | Trade-off |
|--------|------|----------|-----------|
| No CMS (Markdown/MDX in repo) | Git | Developer-edited, rarely changing content | Non-technical edits need a developer |
| Decap CMS | Git-based, open source | Small sites where editors change Markdown through a web UI; content stays in the repo | Simpler UI, editorial workflow depends on Git host auth |
| Sanity | Hosted headless | Structured content, live preview, custom editing UI, free tier for small teams | Content lives in a vendor; costs grow with users/usage |
| Strapi | Self-hosted headless (or their cloud) | Data must stay on own infrastructure, custom roles | You run and patch a Node server and database |
| Contentful | Hosted headless, enterprise | Large teams, many locales, governance | Expensive beyond the free tier; overkill for small sites |
| Shopify | Commerce platform | Storefronts beyond a few products | Monthly fee and transaction fees |

No CMS is better when: one person edits, content changes less than monthly, or the budget cannot carry a recurring fee. Add the CMS later if editing pain shows up; the content model does not change.

When a CMS is used, rebuild on publish (webhook to the host's build hook) so the static site stays current.

## Hosting and deployment

| Host | Strengths | Trade-offs |
|------|-----------|------------|
| Vercel | Best-in-class Next.js support, preview deploys per branch, edge functions | Commercial use needs a paid plan; costs rise with bandwidth/functions; Next features couple to it |
| Netlify | Preview deploys, built-in forms with spam filtering, redirects file, functions | Build-minute and bandwidth limits on lower tiers |
| Cloudflare Workers (static assets) | Large global network, generous free bandwidth, functions for form handlers in the same deploy, Turnstile integration | Some framework server features need adapters; Cloudflare now says "start new projects with Workers" rather than Pages (existing Pages projects keep working) |
| GitHub Pages | Free, simple for static sites and docs | No server functions, limited headers/redirect control, public repo on the free plan |
| GCS or S3 + CDN (Cloud CDN / CloudFront) | Full control, fits existing cloud accounts and compliance needs | You configure TLS, caching, redirects, 404 handling and invalidation yourself |

Defaults: static Astro → Cloudflare Workers or Netlify; Next.js → Vercel (or a Node host if lock-in matters); docs → GitHub Pages or the same host as the product site.

Always:

- Deploy from Git with preview deploys for review; production from the main branch.
- Register domain, host and DNS in the owner's accounts, with the developer as a collaborator.
- Set security headers (HSTS, `Content-Security-Policy` sized to the real third parties, `Referrer-Policy`, `X-Content-Type-Options`, `Permissions-Policy`) and clickjacking protection: `Content-Security-Policy: frame-ancestors 'self'` (or `'none'`) plus `X-Frame-Options: SAMEORIGIN`/`DENY` for older clients. Send these as HTTP headers from the host; `frame-ancestors` is ignored in a `<meta>` CSP.
- Astro 6 has built-in CSP (`security.csp` in `astro.config`): it emits a `<meta http-equiv="content-security-policy">` with hashes for the page's scripts and styles. Test it with `build` + `preview` (not active in dev), and still set `frame-ancestors` and the other headers at the host.
- Cache static assets with long immutable lifetimes (hashed filenames) and HTML with short ones.
- Keep `www` vs apex consistent with a single permanent redirect.
