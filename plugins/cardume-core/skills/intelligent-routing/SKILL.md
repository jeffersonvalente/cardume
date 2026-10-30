---
name: intelligent-routing
description: "Domain-to-agent routing table. Use when a request spans several domains and it's unclear which Cardume agent should handle it."
metadata:
  internal: "true"
---

# Routing reference

Claude Code already picks agents by their descriptions. Open this table only when that choice is not
obvious: the request is vague, touches several areas, or an orchestrator is staffing a plan.

## Order of decisions

1. **The user named an agent** (`@backend-specialist`, "use the debugger") → use it.
2. **Work level first** (see the project's CLAUDE.md): building something new goes through the level
   flow — level 1 straight to the specialist, level 2 `spec`, level 3 `prd`. Routing then picks who
   executes each task.
3. **One area matches** → that area's specialist below.
4. **Several areas** → the `orchestrator` coordinates the specialists once there is an approved plan
   (spec/tasks or PRD); before that, write the plan.
5. **Still unsure** → ask the user one short question instead of guessing.

## By area

### Product, planning and delivery chain (`cardume-core`)

| Signals in the request | Agent / skill |
| --- | --- |
| new product, new project, next phase, PRD, requirements, roadmap, OKR, stakeholders | `product-manager` (with the `prd` skill) |
| backlog, prioritize, user stories, split an epic, MVP slicing | `product-owner` |
| system design, contracts between modules, "which database / framework", break down a PRD, ADR | `software-architect` |
| "does it meet the spec", verify the feature | `verify` skill |
| "is it ready to approve", phase gate, QA sign-off, acceptance criteria met | `qa-gatekeeper` (with the `gate` skill) |
| release, version tag, changelog, release notes, launch post | `release-manager` |
| plan or timeline for multi-area work that has no spec or PRD | `project-planner` |
| coordinate several specialists on an approved plan; multi-angle analysis | `orchestrator` |
| error, crash, "not working", flaky behavior, regression | `debugger` |
| explore or map an unfamiliar codebase | `explorer-agent` |
| legacy code, "what does this do", safe refactor | `code-archaeologist` |
| README, API docs, guides, comments | `documentation-writer` |

### Web, design and mobile (`cardume-frontend`)

| Signals | Agent / skill |
| --- | --- |
| visual direction, palette, typography, critique, polish, redesign, "make it look better" | `design-flow` (agent or `/cardume-frontend:design-flow`) |
| a whole website: landing page, company site, portfolio, blog, docs site | `site-builder` (calls `design-flow` for the visual work) |
| components, state, React/Next.js engineering inside an agreed design | `frontend-specialist` |
| iOS, Android, React Native, Flutter, Expo, gestures, mobile navigation | `mobile-developer` |
| slow pages, bundle size, Core Web Vitals, rendering performance | `performance-optimizer` |
| search ranking, meta tags, sitemap, AI-search visibility | `seo-specialist` |

### APIs and databases (`cardume-backend`)

| Signals | Agent |
| --- | --- |
| endpoints, services, Node.js, Python, Java/Spring, Rust, MCP servers | `backend-specialist` |
| schema design, migrations, indexes, slow queries, ORM choice | `database-architect` |

### Data (`cardume-data`)

| Signals | Agent |
| --- | --- |
| BigQuery SQL, data pipelines, DAGs, medallion layers, data loads | `data-engineer-gcp-bigquery` |
| review a data/analytics pull request (`/cardume-data:review-pr`) | `lakehouse-reviewer` |
| read-only audit of one GCP data or AI/ML project: inventory, IAM, data flow (a whole-estate review goes to `devops-engineer`) | `gcp-project-auditor-data-and-ia` |

### Platform and operations (`cardume-platform`)

| Signals | Agent |
| --- | --- |
| CI/CD, Dockerfiles, Terraform authoring, Kubernetes manifests/Helm, deploy procedures, servers | `devops-engineer` |
| health check or maturity review of a whole cloud estate (AWS, GCP, Azure, Kubernetes) | `devops-engineer` (with the `cloud-platform-assessment` skill) |
| review an infrastructure change (Terraform, IAM, network, SSH access, Kubernetes manifests, CI pipelines) | `iac-reviewer` |
| anything against a **running** cluster: inspect, inventory, incident, scale, restart, drain | `kubernetes-copilot` |
| instrumentation, OpenTelemetry, SLOs, alerts, dashboards, latency/error investigation | `observability-engineer` |
| cloud spend, budgets, forecasts, rightsizing, commitments, showback | `finops-architect` |
| foundations for a new platform: landing zone, environments, baseline architecture | `project-bootstrap-architect` |

Kubernetes split: **runtime** work on a live context goes to `kubernetes-copilot`; **authoring**
manifests, Helm charts or pipelines goes to `devops-engineer`.
New product or project: the PRD goes to `product-manager` (cardume-core); its cloud/platform foundations go to `project-bootstrap-architect`, which `product-manager` hands off to once the PRD exists.

### Quality and security (`cardume-qa`)

| Signals | Agent |
| --- | --- |
| test strategy, unit/integration tests, TDD, coverage gaps | `test-engineer` |
| end-to-end automation, Playwright, flaky UI tests, test pipelines | `qa-automation-engineer` |
| security review, OWASP, secrets, auth flows, dependency risk | `security-auditor` |
| authorized penetration testing, exploitation, red team exercises | `penetration-tester` |

### Games (`cardume-games`)

| Signals | Agent |
| --- | --- |
| game mechanics, engines (Godot, Unity, Unreal, Phaser), game feel, multiplayer | `game-developer` |

## Worked examples

| Request | Route |
| --- | --- |
| "Give the pricing page a bolder look" | `design-flow` |
| "Our checkout returns 500 for some users since yesterday" | `debugger` (level 1; a payments area → mini-spec) |
| "Add invoice export to CSV and PDF with filters" | level 2 → `spec` → tasks → `backend-specialist` + `frontend-specialist`, coordinated by `orchestrator` |
| "We're starting a booking platform for clinics" | level 3 → `product-manager` (PRD) → `software-architect` |
| "Why did yesterday's gold table lose rows?" | `data-engineer-gcp-bigquery` |
| "Pods in production keep restarting" | `kubernetes-copilot` |
| "Can we cut 20% of our cloud bill?" | `finops-architect` |
| "Is phase 2 ready to approve?" | `qa-gatekeeper` (gate) |
