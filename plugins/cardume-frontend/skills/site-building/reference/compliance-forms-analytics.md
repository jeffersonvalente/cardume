# Forms, compliance, analytics and i18n

This is engineering guidance, not legal advice. For regulated sectors (health, finance, children) or large-scale data processing, recommend the owner confirm with a lawyer or their data protection officer.

## Forms

- **Validate on the server**, always. Client-side validation is for usability; anything reaching the handler must be re-checked (types, lengths, email format, allowed values).
- **Spam protection** without hurting people: honeypot field + time-to-submit check first; add Cloudflare Turnstile or hCaptcha when spam persists. Avoid puzzle CAPTCHAs (accessibility and conversion cost). Rate-limit by IP at the handler.
- **Where submissions go:** decide with the owner and write it in the handoff. Options: host form feature (Netlify Forms), a serverless function that emails via a transactional provider (Resend, Postmark, SES) and/or stores in a sheet/CRM, or a form service. Send a copy somewhere durable, because email alone gets lost.
- **Collect the minimum.** Each field needs a purpose. Health data (e.g. symptoms in a clinic form) is sensitive personal data under LGPD and special-category data under GDPR; prefer "describe briefly" optional fields and do not require it.
- **Accessible:** visible `<label>` per field, errors announced and linked to the field, do not rely on color, keep entered values on error.
- **Feedback:** clear success state, what happens next and when; an error state with an alternative channel (phone/WhatsApp).
- **Consent text** near the submit button linking to the privacy policy; a checkbox only for optional extra uses (e.g. newsletter), never pre-checked.
- Test end to end on production: a real submission arrives, the auto-reply (if any) works, spam is filtered.

## Cookie consent (LGPD / GDPR)

- Strictly necessary cookies (session, security, the consent record itself) need no consent. Analytics, advertising pixels, embedded videos/maps that set cookies, and chat widgets do.
- **Nothing non-essential loads before consent.** Gate scripts, not just cookies: render embeds as click-to-load placeholders, and load tags only after the matching category is accepted.
- Banner: accept and reject equally prominent on the first layer, categories with granular choice, no pre-ticked boxes, a link to the privacy policy, and a persistent way to change the choice later (footer link).
- Store the consent choice and timestamp; re-ask when purposes change.
- If using Google tags, implement Consent Mode v2: set defaults for `ad_storage`, `analytics_storage`, `ad_user_data` and `ad_personalization` (all `denied` before choice) and send an `update` on the visitor's choice. **Basic** mode blocks Google tags until the visitor interacts with the banner (nothing reaches Google on reject); **Advanced** mode loads tags immediately with denied defaults and sends cookieless pings. Basic is the safer default under the "nothing before consent" rule above; Advanced needs the owner's informed, documented decision. See <https://developers.google.com/tag-platform/security/concepts/consent-mode>.
- Brazil: follow the ANPD guide "Cookies e Proteção de Dados Pessoais" (v1.0, October 2022; check anpd.gov.br for a newer edition). EU: the ePrivacy rules as applied by the national authority.
- Options: a lightweight open-source library (e.g. vanilla-cookieconsent) or a CMP (Cookiebot, Usercentrics, CookieYes) when the owner needs a scanner, audit logs or IAB TCF for advertising.

## Privacy policy and legal pages

A privacy policy page is needed whenever the site collects any personal data (forms, analytics, cookies). It should state: who the controller is and how to contact them (and the DPO/encarregado when applicable), what data is collected and why, the legal basis, who receives it (host, form provider, analytics), international transfers, retention, data subject rights and how to exercise them, and cookie categories. Write it in the site's language(s), in plain words, matching what the site actually does.

Also consider: terms of use for storefronts, imprint/company details where local law requires them (e.g. company registration number in BR footers, Impressum in Germany), and consumer-law information for e-commerce (returns, right of withdrawal).

## Accessibility as compliance

WCAG 2.2 AA is the practical target.

- **EU:** the European Accessibility Act applies to many e-commerce and consumer services since 28 June 2025. Presumption of conformity comes from the harmonised standard EN 301 549: V3.2.1 (2021) maps to WCAG 2.1 AA; V4.1.1 (published September 2026) aligns with WCAG 2.2, and it carries presumption of conformity only once cited in the Official Journal (expected late 2026; check the current status). Meeting WCAG 2.2 AA covers both.
- **Brazil:** LBI (Lei 13.146/2015) art. 63 requires accessible websites for companies with headquarters or commercial representation in Brazil and for public bodies. ABNT NBR 17225:2025 (March 2025, based on WCAG 2.2) is the national technical standard for web content accessibility. Basics: contrast, keyboard access, visible focus, labels, alt text, target size ≥ 24×24 px, captions for video, no content relying only on color. Verify with `cardume-accessibility-checker` plus a keyboard-only pass.

## Analytics with consent

- Pick the lightest tool that answers the brief's goal. Privacy-friendly, cookieless options (Plausible, Fathom, Umami, Cloudflare Web Analytics) often need no consent banner for analytics; confirm their configuration does not set identifiers.
- GA4 or ad pixels: load only after consent; define conversions that match the goal (form submitted, WhatsApp click, call click, purchase).
- Track outcomes, not everything. Document event names in the handoff.

## i18n

- Ask which languages and which is primary; do not machine-translate silently, mark machine drafts for review.
- URL per locale (`/en/...`, `/pt-br/...` or per-domain), never cookie- or IP-only switching; search engines need crawlable URLs.
- `<html lang>`, `hreflang` alternates including `x-default`, localized titles/descriptions/slugs where useful, locale-aware dates, numbers and currency.
- Language switcher that keeps the current page, labelled with language names in their own language, not flags.
- Use the `i18n-localization` skill for the workflow and `cardume-i18n-checker <project_path>` to catch missing keys.
