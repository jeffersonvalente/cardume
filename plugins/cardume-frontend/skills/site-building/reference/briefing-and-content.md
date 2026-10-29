# Briefing, sitemap and content

## Turning the brief into decisions

| Brief answer | Decision it drives |
|--------------|--------------------|
| Goal (calls, bookings, sales) | Primary CTA on every page, what analytics counts as a conversion |
| Audience and devices | Mobile-first priorities, reading level, language |
| Content owner and edit frequency | CMS or not, editor training, handoff docs |
| Languages | URL structure, `hreflang`, translation workflow |
| Brand assets | What design-flow receives; whether a brand discovery step is needed first |
| Integrations | Form handler, embeds to gate behind consent, hosting needs |
| Budget and hosting | Static host vs managed platform, paid CMS tier or not |

Missing brand assets are a finding, not a blocker: tell design-flow, which runs its own discovery.

## Sitemap

Write it as a tree, one line per page with its goal and CTA:

```
/                  Home: who we are, main services, trust signals → CTA: book a visit
/services/         Overview → links to each service
/services/<slug>   One service: problem, approach, price range or "from", FAQ → CTA: book
/about             Team, credentials, story, photos of the real place → CTA: book
/blog/             Optional: only if someone will write at least monthly
/contact           Form, phone, WhatsApp, map, hours, address → CTA: send / call
/privacy           Privacy policy (required when collecting any personal data)
```

Prefer fewer, stronger pages. A blog nobody updates hurts trust more than no blog.

## Content model

For each repeated thing, define fields once:

```
service:   title, slug, summary (≤160 chars), body, icon/image, price_from?, faq[], order
team:      name, role, credentials, photo, bio, order
post:      title, slug, date, author, summary, cover, body, tags[]
location:  name, address, geo, phone, hours[], map_url
```

Store as Astro content collections / Markdown with frontmatter when there is no CMS, or as CMS schemas otherwise. Validate fields with a schema (e.g. Zod in Astro collections) so a missing image fails the build instead of the page.

## Page and section patterns

| Page | Sections that usually earn their place |
|------|----------------------------------------|
| Landing | Hero with specific promise + one CTA, problem/outcome, how it works, proof (testimonials, logos, numbers with source), objections/FAQ, final CTA |
| Institutional home | Who/where in one sentence, services overview, differentiators backed by evidence, team/place photos, reviews, location/contact strip |
| Service | What it is, who it is for, process, duration/price expectations, FAQ, CTA |
| About | Story, people with credentials, real photos, values shown through specifics |
| Portfolio | Curated work (fewer, better), each case with context → role → result, contact |
| Blog | Index with filters/tags, post template with author, date, reading time, related posts |
| Docs | Sidebar nav, search, versioning if the product has versions, edit-this-page link |
| Storefront | Catalog grid, product page (photos, price, variants, shipping/returns), cart/checkout handled by the provider |
| Contact | Form, direct channels (phone, WhatsApp, email), map with consent gate, hours, address |

These are content patterns, not visual templates; design-flow decides how they look.

## Copy

- Real copy over lorem ipsum: placeholder text hides layout problems (long names, long German/Portuguese words) and gets shipped by accident.
- Specific beats generic: "Clareamento a laser em 1 sessão de 60 min" beats "Soluções completas para seu sorriso".
- Write for scanning: front-load headings, short paragraphs, one idea each.
- Missing copy: draft it from the brief, mark each draft in `docs/content-todo.md` with the page, the assumption and who must approve. Regulated fields (health, law, finance) need owner approval before launch, because claims can carry legal risk.

## Images

- Real photos of the place, people and work beat stock; stock is acceptable as a clearly temporary placeholder tracked in the content to-do.
- Export at no more than 2x the largest rendered size; serve AVIF/WebP with fallbacks through the framework pipeline.
- Always set dimensions (prevents CLS) and lazy-load below the fold; the hero/LCP image loads eagerly with high fetch priority.
- `alt` describes what the image communicates in context; decorative images get `alt=""`. Do not stuff keywords into `alt`.
- Strip EXIF location data from photos of private places.
