# Write-up format

Write the assessment in Markdown. For a long review, save it to `docs/` (a deliverable the
team keeps) and return a short summary with the path. Keep the order below: decision-makers
read the first page; engineers read the register.

## 1. Executive summary (half a page)

- One sentence on scope: what was reviewed, when, with what access.
- Overall picture in two or three sentences, in business terms ("Customer exports are
  downloadable by anyone with the link, and nobody would hear about a cost spike until the
  invoice arrives").
- The three to five risks to act on now.
- What the 90-day plan asks for: people, rough effort, any spend.
- Notable strengths worth keeping.

## 2. Top risks

At most ten, ordered by priority. One block per risk:

```markdown
### R1. Customer export bucket is readable by anyone on the internet
**Risk:** Because the bucket that holds nightly customer CSV exports grants `allUsers` the
Storage Object Viewer role, anyone who guesses or finds an object URL can download customer
names and email addresses, which would be a reportable personal-data breach.
**Pillar:** Security (data protection)
**Likelihood:** Likely, object names follow a date pattern and the bucket name appears in a
public support article.
**Impact:** Severe, personal data of every customer in the export, plus notification duties.
**Priority:** Act now
**How it was checked:** `gcloud storage buckets get-iam-policy gs://<export-bucket>` in project
`analytics-prd` showed `allUsers` with `roles/storage.objectViewer`; `publicAccessPrevention`
is `inherited` and no organization policy enforces it. Access logs were not available, so
whether anyone downloaded the files is not verified.
**Affected:** analytics-prd
**Recommendation:** Remove the public binding, enforce public access prevention on the bucket,
give the partner a signed-URL or service-account path instead, and set the
`storage.publicAccessPrevention` organization policy so the next bucket cannot repeat it.
**References:** CIS Google Cloud Platform Foundation Benchmark (Cloud Storage section); Google
Cloud Architecture Framework, security pillar.
```

Keep "How it was checked" concrete enough that someone else can repeat it. When the evidence
is an interview or a document, say so.

## 3. 30/60/90-day plan

Group by time window, not by pillar, because people execute in time:

```markdown
#### Days 1–30: contain
- [ ] Remove `allUsers` from the export bucket and enforce public access prevention
      (owner: data platform lead; done when an anonymous `curl` of a known object returns 403
      and the org policy is set on the folder; retires R1).
- [ ] Create a billing budget for the billing account with alerts at 50/90/100% routed to
      a monitored channel (owner: FinOps lead; done when a test notification reaches the
      on-call channel; retires R2).

#### Days 31–60: fix causes
- [ ] ...

#### Days 61–90: raise the baseline
- [ ] ...
```

Each item names an owner role, a done-condition someone could verify, and the risks it
retires. Add rough effort in person-days only where it helps sequencing. If an item needs
spend (Multi-AZ, a second region, a CSPM licence), give the order of magnitude.

## 4. Risk register (appendix)

All remaining risks in the same block format, or as a compact line each:
`R11 · Reliability · Plausible/Material → Next quarter · one NAT gateway in a single zone
serves all private subnets · checked with aws ec2 describe-nat-gateways`.

## 5. Scope and limits

- Accounts, projects, subscriptions and clusters reviewed, and which were sampled.
- Access used (role names) and anything denied.
- Areas not reviewed and why.
- Open questions, each with the role best placed to answer.

## Writing notes

- Lead with consequence, not configuration. "Checkout stops if zone a fails" beats "RDS
  MultiAZ=false".
- Say when something is fine. A short "Strengths" list keeps trust and protects good choices.
- Do not inflate. A long register of remote, minor items costs credibility for the top ones.
- Quote numbers from billing or metrics when you have them; otherwise give a range and say it
  is an estimate.
