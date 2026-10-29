---
type: llm
focus: last_message
weight: 2
---

PASS if the answer (1) asks briefing questions or states explicit assumptions about things not given (who edits content and how often, where form submissions go, hosting/domain/budget, brand assets beyond the logo); (2) proposes a sitemap (e.g. home, services or per-service pages, team/about, contact with map and hours, privacy policy); (3) picks a static-first stack (Astro or plain static HTML, optionally a light or no CMS) with a stated reason, rather than defaulting to a full web-app stack; (4) covers LGPD: consent before non-essential cookies/analytics or embedded maps, a privacy policy page, and minimal/careful handling of patient data in the form; (5) covers local SEO: LocalBusiness/Dentist structured data, consistent name/address/phone with the Google Business Profile, Portuguese titles/descriptions; (6) includes form handling (server-side validation, spam protection, where submissions go) and a launch checklist or quality gates (Lighthouse/Core Web Vitals, accessibility, sitemap/robots, HTTPS).
FAIL if it jumps straight to generic page code or a Next.js/full-stack app with no stack reasoning, omits LGPD/consent entirely, ignores local SEO, or uses lorem ipsum placeholder copy as the plan.
