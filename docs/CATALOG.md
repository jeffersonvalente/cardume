# Catalog

Every agent, skill and manual command in the Cardume plugins: 33 specialist agents, 62 skills and 13 manual commands. Each purpose line is the first sentence of the item's own `description`; open the file for the full text and the "Use when" trigger.

You rarely call any of these by name. Claude picks agents and skills from their descriptions (see [How it works](HOW_IT_WORKS.md#routing)). Manual commands run only when you type them.

- [Agents](#agents)
- [Skills](#skills)
- [Manual commands](#manual-commands)

## Agents

### cardume-core

| Agent | Purpose |
| --- | --- |
| [`code-archaeologist`](../plugins/cardume-core/agents/code-archaeologist.md) | Analyzes legacy and undocumented code, explains what it does, and plans safe incremental refactors using characterization tests and the strangler-fig pattern. |
| [`debugger`](../plugins/cardume-core/agents/debugger.md) | Investigates bugs to their root cause with a reproduce → isolate → understand → fix-and-verify process, then adds a regression test. |
| [`documentation-writer`](../plugins/cardume-core/agents/documentation-writer.md) | Writes technical documentation such as READMEs, API docs, code comments (JSDoc/TSDoc/docstrings), ADRs, changelogs, tutorials, and llms.txt. |
| [`explorer-agent`](../plugins/cardume-core/agents/explorer-agent.md) | Read-only codebase explorer that maps structure, entry points, dependencies, architectural patterns, and risks, and researches feasibility of integrations. |
| [`orchestrator`](../plugins/cardume-core/agents/orchestrator.md) | Coordinates several Cardume specialist agents on one task and merges their findings into a single report. |
| [`product-manager`](../plugins/cardume-core/agents/product-manager.md) | Turns vague requests into product requirements: problem and evidence, success metrics, appetite, user stories and verifiable acceptance criteria, using the prd skill. |
| [`product-owner`](../plugins/cardume-core/agents/product-owner.md) | Owns the backlog: prioritizes it (MoSCoW, RICE), splits epics into user stories and refines them into testable criteria using the prd and spec formats. |
| [`project-planner`](../plugins/cardume-core/agents/project-planner.md) | Writes a lightweight plan (docs/PLAN-{task-slug}.md) with task breakdown, agent assignments, dependencies and verification steps, without writing code. |
| [`qa-gatekeeper`](../plugins/cardume-core/agents/qa-gatekeeper.md) | Independent verifier: checks a PR, feature or phase against its written criteria (PRD, spec, standards) by running the checks itself, and reports pass/fail with evidence. |
| [`release-manager`](../plugins/cardume-core/agents/release-manager.md) | Prepares and publishes releases (Release + DevRel) - checks the gate or explicit approval, picks the semver bump, updates CHANGELOG.md, writes docs/release/vX.Y.Z.md with release notes, rollback plan and an honest announcement, then prepares tag and GitHub release commands for confirmation. |
| [`software-architect`](../plugins/cardume-core/agents/software-architect.md) | Software architect: after a PRD is approved, writes contracts, ADRs and the feature list in docs/prd/<slug>-architecture.md; after each feature's spec is approved, writes its tasks.md (tasks skill). |

### cardume-frontend

| Agent | Purpose |
| --- | --- |
| [`design-flow`](../plugins/cardume-frontend/agents/design-flow.md) | Design director that runs the design flow (shape, craft, critique, audit, polish) and writes production-grade UI code. |
| [`frontend-specialist`](../plugins/cardume-frontend/agents/frontend-specialist.md) | Senior frontend architect that implements maintainable React/Next.js code with a performance-first mindset. |
| [`mobile-developer`](../plugins/cardume-frontend/agents/mobile-developer.md) | Builds cross-platform mobile apps with React Native, Expo, and Flutter, applying touch, performance, offline, security, and platform conventions and verifying with real builds. |
| [`performance-optimizer`](../plugins/cardume-frontend/agents/performance-optimizer.md) | Profiles and optimizes web performance: Core Web Vitals (LCP, INP, CLS), bundle size, rendering, network, and memory. |
| [`seo-specialist`](../plugins/cardume-frontend/agents/seo-specialist.md) | Audits and improves SEO and GEO (Generative Engine Optimization): technical SEO, Core Web Vitals, E-E-A-T, schema markup, and visibility in AI search answers. |
| [`site-builder`](../plugins/cardume-frontend/agents/site-builder.md) | Delivers websites (landing pages, company sites, portfolios, blogs, docs, small stores) from brief to launch, delegating design to design-flow and SEO to seo-specialist. |

### cardume-backend

| Agent | Purpose |
| --- | --- |
| [`backend-specialist`](../plugins/cardume-backend/agents/backend-specialist.md) | Backend architect for Node.js, Python, Java/Spring Boot, and serverless/edge systems. |
| [`database-architect`](../plugins/cardume-backend/agents/database-architect.md) | Database architect for schema design, query optimization, migrations, and serverless databases. |

### cardume-data

| Agent | Purpose |
| --- | --- |
| [`data-engineer-gcp-bigquery`](../plugins/cardume-data/agents/data-engineer-gcp-bigquery.md) | Data engineer for BigQuery lakehouses on GCP: medallion layers, dbt/Dataform or SQL models, Kimball marts, Airflow/Composer DAGs, cost and data-quality fixes. |
| [`gcp-project-auditor-data-and-ia`](../plugins/cardume-data/agents/gcp-project-auditor-data-and-ia.md) | Read-only auditor for one GCP data or AI/ML project: inventory, IAM and public exposure, data flow and governance, ranked recommendations with evidence. |
| [`lakehouse-reviewer`](../plugins/cardume-data/agents/lakehouse-reviewer.md) | Read-only reviewer for data-pipeline PRs: risk-ranked checks of SQL, models and DAGs plus data-diff evidence in the configured validation environment, ending in a proposed verdict. |

### cardume-platform

| Agent | Purpose |
| --- | --- |
| [`devops-engineer`](../plugins/cardume-platform/agents/devops-engineer.md) | DevOps engineer for infrastructure as code (Terraform/OpenTofu), CI/CD pipelines, deploy procedures, Linux servers and logs, Kubernetes manifests and Helm charts, and whole-estate cloud platform assessments. |
| [`finops-architect`](../plugins/cardume-platform/agents/finops-architect.md) | FinOps architect for AWS/GCP/Azure: analyzes bills and usage, explains cost changes, builds budgets and forecasts, and proposes ranked savings (rightsizing, commitments, storage, egress, showback). |
| [`iac-reviewer`](../plugins/cardume-platform/agents/iac-reviewer.md) | Read-only reviewer for infrastructure-as-code changes (Terraform/OpenTofu on GCP, Kubernetes manifests, CI pipelines): IAM and security, secrets, blast radius, state, cost, workload hardening and pipeline permissions; approves or requests changes. |
| [`kubernetes-copilot`](../plugins/cardume-platform/agents/kubernetes-copilot.md) | Live-cluster SRE co-pilot for GKE, EKS, AKS and on-prem Kubernetes: crashloops, OOMKills, NotReady nodes, stuck rollouts, scaling, cordon/drain, and cluster reviews. |
| [`observability-engineer`](../plugins/cardume-platform/agents/observability-engineer.md) | Observability engineer for services and infrastructure: OpenTelemetry instrumentation, SLOs and error budgets, burn-rate alerting, dashboards, and telemetry-driven incident investigation, vendor-neutral. |
| [`project-bootstrap-architect`](../plugins/cardume-platform/agents/project-bootstrap-architect.md) | Platform kickoff architect for new or inherited systems: runs the landing-zone decision log (identity, environments, network, CI/CD, security, operations) and writes a platform charter and 90-day backlog. |

### cardume-qa

| Agent | Purpose |
| --- | --- |
| [`penetration-tester`](../plugins/cardume-qa/agents/penetration-tester.md) | Offensive security specialist for authorized penetration tests and red team exercises: reconnaissance, attack simulation, vulnerability exploitation, and reporting. |
| [`qa-automation-engineer`](../plugins/cardume-qa/agents/qa-automation-engineer.md) | Test automation engineer for end-to-end and regression suites with Playwright or Cypress and their CI pipelines. |
| [`security-auditor`](../plugins/cardume-qa/agents/security-auditor.md) | Security auditor for code and architecture: OWASP Top 10 (2025), supply chain, authentication, injection, XSS, secrets, and zero-trust design. |
| [`test-engineer`](../plugins/cardume-qa/agents/test-engineer.md) | Test engineer for unit, integration, and E2E tests using TDD. |

### cardume-games

| Agent | Purpose |
| --- | --- |
| [`game-developer`](../plugins/cardume-games/agents/game-developer.md) | Game developer that builds and debugs 2D/3D games for web, mobile, desktop and console-minded targets in Godot, Unity, Unreal, Phaser, Three.js, Bevy and similar engines. |

## Skills

Skills load when a request matches their description. You can also call any of them by hand, for example `/cardume-core:spec` or `/cardume-core:gate`. Skills marked *internal* are hidden from installers for other tools.

### cardume-core

| Skill | Purpose |
| --- | --- |
| [`adr`](../plugins/cardume-core/skills/adr/SKILL.md) | Records an Architecture Decision Record in docs/adr/ (MADR-style: drivers, options, decision, consequences, confirmation) and keeps the index current. |
| [`app-builder`](../plugins/cardume-core/skills/app-builder/SKILL.md) | Builds a new full-stack, mobile, desktop, CLI, or extension app from a natural-language request by detecting project type, choosing the tech stack, scaffolding from templates, and coordinating specialist agents. |
| [`architecture`](../plugins/cardume-core/skills/architecture/SKILL.md) | Architecture decision framework covering context discovery questions, trade-off analysis and pattern selection (monolith vs microservices, layering, event-driven); ADRs are recorded via the adr skill. |
| [`bash-linux`](../plugins/cardume-core/skills/bash-linux/SKILL.md) | Bash patterns for Linux and macOS covering command chaining, file and text operations, process and network commands, error handling, and script templates. |
| [`behavioral-modes`](../plugins/cardume-core/skills/behavioral-modes/SKILL.md) | Defines working modes (brainstorm, implement, debug, review, teach, ship, plus multi-agent explore and plan-execute-critic) with the behavior and output style for each. |
| [`brainstorming`](../plugins/cardume-core/skills/brainstorming/SKILL.md) | Clarifying-question protocol (purpose, users, scope, trade-offs) plus progress, error, and completion messaging patterns. |
| [`clean-code`](../plugins/cardume-core/skills/clean-code/SKILL.md) | Pragmatic coding standards (SRP, DRY, KISS, YAGNI, naming, small functions, no needless comments or over-engineering) plus a pre-edit dependency check, a completion self-check, and which cardume-* verification script each agent runs. |
| [`code-review-checklist`](../plugins/cardume-core/skills/code-review-checklist/SKILL.md) | Code review checklist covering correctness, security (injection, XSS, secrets, prompt injection), performance, code quality, testing, and docs, with severity-tagged comment conventions. |
| [`database-design`](../plugins/cardume-core/skills/database-design/SKILL.md) | Database decision guide for choosing a database (PostgreSQL, Neon, Turso, SQLite) and ORM (Drizzle, Prisma, Kysely), schema design and normalization, indexing, and safe migrations. |
| [`documentation-templates`](../plugins/cardume-core/skills/documentation-templates/SKILL.md) | Structure templates for READMEs, API endpoint docs, code comments (JSDoc/docstrings), changelogs, ADRs, and AI-friendly docs such as llms.txt. |
| [`gate`](../plugins/cardume-core/skills/gate/SKILL.md) | Runs a phase or milestone gate: checks every acceptance criterion of the PRD/spec against executed evidence, writes docs/gates/GATE-<id>.md with a pass/fail table and an APPROVE/REJECT recommendation, and leaves the decision to the user. |
| [`generator-pr-description`](../plugins/cardume-core/skills/generator-pr-description/SKILL.md) | Drafts a consolidated PR title and body from the branch's full diff and commits vs its base (repo PR template or built-in), in the user's or project's language (e.g. |
| [`implement`](../plugins/cardume-core/skills/implement/SKILL.md) | Builds an approved tasks.md one task at a time: a fresh subagent per task, the task's verification command run after each, the diff checked by a separate reviewer, the checkbox ticked only with evidence. |
| [`intelligent-routing`](../plugins/cardume-core/skills/intelligent-routing/SKILL.md) *(internal)* | Domain → agent routing table for the Cardume suite. |
| [`lint-and-validate`](../plugins/cardume-core/skills/lint-and-validate/SKILL.md) | Lint, type-check, and security-scan commands per ecosystem (ESLint, tsc, npm audit, Ruff, Bandit, MyPy) and a fix-and-rerun quality loop. |
| [`parallel-agents`](../plugins/cardume-core/skills/parallel-agents/SKILL.md) | Patterns for running Cardume specialist agents through Claude Code's Agent tool, covering single, sequential, and parallel invocation, context passing, and synthesizing results into one report. |
| [`plan-writing`](../plugins/cardume-core/skills/plan-writing/SKILL.md) | Principles for writing short, specific plans of 5-10 verifiable tasks with dependencies, project-specific verification scripts, and a final verification phase. |
| [`powershell-windows`](../plugins/cardume-core/skills/powershell-windows/SKILL.md) | Windows PowerShell patterns and pitfalls such as parenthesizing cmdlets in logical operators, ASCII-only script output, ConvertTo-Json -Depth, paths, and error handling. |
| [`prd`](../plugins/cardume-core/skills/prd/SKILL.md) | Writes a product requirements document in docs/prd/ (problem and evidence, success metrics, appetite, verifiable acceptance criteria, no-gos, typed risks, test script, blockers) for a new product, project or phase. |
| [`python-patterns`](../plugins/cardume-core/skills/python-patterns/SKILL.md) | Python decision guide for choosing a framework (Django, FastAPI, Flask), async vs sync, type hints and Pydantic, project structure, background tasks, error handling, and testing. |
| [`review`](../plugins/cardume-core/skills/review/SKILL.md) | Reviews a change with parallel specialist reviewers chosen from the touched files, drops low-confidence findings, verifies each remaining one against the code, and flags specs left outdated by the change. |
| [`spec`](../plugins/cardume-core/skills/spec/SKILL.md) | Specifies a feature before building it: asks the questions that change the design, then writes docs/specs/<slug>/spec.md with testable EARS requirements, acceptance criteria, design notes and non-goals. |
| [`standards`](../plugins/cardume-core/skills/standards/SKILL.md) | Scans the repository and writes docs/standards.md with the project's actual conventions (stack, layout, naming, errors, tests, lint, commits, CI), each backed by evidence. |
| [`systematic-debugging`](../plugins/cardume-core/skills/systematic-debugging/SKILL.md) | Systematic 4-phase debugging (reproduce, isolate, understand root cause, fix and verify) with evidence templates and a 5 Whys analysis. |
| [`tasks`](../plugins/cardume-core/skills/tasks/SKILL.md) | Breaks an approved spec into small ordered tasks in docs/specs/<slug>/tasks.md, each with requirement IDs, an owner agent/lane, contracts it depends on and a verification command; --issues also opens GitHub issues after confirmation. |
| [`verify`](../plugins/cardume-core/skills/verify/SKILL.md) | Checks an implementation against every requirement of its spec by executing each acceptance criterion, records evidence in docs/specs/<slug>/verify.md, lists gaps and proposes spec amendments for drift. |

### cardume-frontend

| Skill | Purpose |
| --- | --- |
| [`design-flow`](../plugins/cardume-frontend/skills/design-flow/SKILL.md) | Designs and iterates on frontend interfaces through a shape, craft, critique, audit, and polish flow, writing production-grade code for websites, landing pages, dashboards, product UI, app shells, components, forms, settings, onboarding, and empty states. |
| [`frontend-design`](../plugins/cardume-frontend/skills/frontend-design/SKILL.md) | Applies design thinking to web UI decisions: constraints, UX psychology, layout, color, typography, effects, and motion, with anti-cliché checks. |
| [`geo-fundamentals`](../plugins/cardume-frontend/skills/geo-fundamentals/SKILL.md) | Optimizes content for citation in AI answer engines (ChatGPT, Claude, Perplexity, Gemini): entity clarity, citable statistics, FAQs, author credentials, AI crawler access. |
| [`i18n-localization`](../plugins/cardume-frontend/skills/i18n-localization/SKILL.md) | Applies internationalization and localization patterns: detecting hardcoded strings, structuring locale files, pluralization, date/number formatting, and RTL support. |
| [`mobile-design`](../plugins/cardume-frontend/skills/mobile-design/SKILL.md) | Guides mobile-first design and implementation decisions for iOS and Android: touch targets, thumb zone, list and animation performance, offline, security, navigation, and platform conventions. |
| [`performance-profiling`](../plugins/cardume-frontend/skills/performance-profiling/SKILL.md) | Measures and analyzes performance before optimizing: Core Web Vitals, Lighthouse, bundle analysis, runtime and memory profiling. |
| [`react-best-practices`](../plugins/cardume-frontend/skills/react-best-practices/SKILL.md) | Applies Vercel Engineering's React and Next.js performance rules: eliminating waterfalls, bundle size, server-side performance, client data fetching, re-renders, and rendering. |
| [`react-native-skills`](../plugins/cardume-frontend/skills/react-native-skills/SKILL.md) | Applies React Native and Expo performance and correctness rules: list virtualization, animations, navigation, images, and native modules. |
| [`seo-fundamentals`](../plugins/cardume-frontend/skills/seo-fundamentals/SKILL.md) | Applies SEO fundamentals: E-E-A-T, Core Web Vitals, technical SEO, meta tags, schema markup, and content structure. |
| [`site-building`](../plugins/cardume-frontend/skills/site-building/SKILL.md) | Runs website delivery: brief, sitemap, static-first stack, design-flow design handoff, build, SEO, LGPD/GDPR consent, quality gates, launch. |
| [`tailwind-patterns`](../plugins/cardume-frontend/skills/tailwind-patterns/SKILL.md) | Applies Tailwind CSS v4 patterns: CSS-first @theme configuration, design token architecture, container queries, dark mode, and responsive utilities. |
| [`web-design-guidelines`](../plugins/cardume-frontend/skills/web-design-guidelines/SKILL.md) | Reviews UI code against the Web Interface Guidelines for accessibility, focus states, forms, animation, typography, and performance. |

### cardume-backend

| Skill | Purpose |
| --- | --- |
| [`api-patterns`](../plugins/cardume-backend/skills/api-patterns/SKILL.md) | API design decision guide: choosing REST, GraphQL, or tRPC, response formats, versioning, pagination, auth, rate limiting, and API security testing. |
| [`java-spring-patterns`](../plugins/cardume-backend/skills/java-spring-patterns/SKILL.md) | Guides Java 17+ and Spring Boot 3.x/4.x work: architecture choice (layered, hexagonal, DDD, modular monolith, CQRS, events), idioms the JDK baseline allows (records, sealed types, pattern matching, virtual threads), Spring transactions, DI and errors, Testcontainers, ArchUnit, Micrometer. |
| [`mcp-builder`](../plugins/cardume-backend/skills/mcp-builder/SKILL.md) | Principles for building MCP (Model Context Protocol) servers: tool design, resource and prompt patterns, input schemas, error handling, and security. |
| [`nodejs-best-practices`](../plugins/cardume-backend/skills/nodejs-best-practices/SKILL.md) | Node.js decision guide: framework selection, async patterns, error handling, security, and project architecture, focused on reasoning over copy-paste templates. |
| [`rust-pro`](../plugins/cardume-backend/skills/rust-pro/SKILL.md) | Modern Rust (edition 2024) guidance: async with Tokio and axum, advanced type-system features, error handling, performance, and production systems programming. |

### cardume-data

| Skill | Purpose |
| --- | --- |
| [`airflow-testing`](../plugins/cardume-data/skills/airflow-testing/SKILL.md) | Testing and CI for Airflow DAGs (Airflow 3 with 2.x notes, Cloud Composer): DagBag parse tests, DAG property tests, top-level code hazards, Ruff AIR rules, credential-free CI. |
| [`bigquery-patterns`](../plugins/cardume-data/skills/bigquery-patterns/SKILL.md) | BigQuery SQL discipline: dry runs, byte caps, partition and column pruning, safe joins and casts, job timeouts, before/after integrity checks. |
| [`gcp-observability-patterns`](../plugins/cardume-data/skills/gcp-observability-patterns/SKILL.md) | Read-only GCP investigation for data platforms via Logging, Monitoring, Storage, gcloud and catalog tools: Composer DAG failures, BigQuery job errors, slot/cost spikes, missing landing files, audit logs, project discovery. |
| [`lakehouse-architecture`](../plugins/cardume-data/skills/lakehouse-architecture/SKILL.md) | Medallion lakehouse design on BigQuery: layer contracts, naming, dimensional modeling (dim_/fct_ defaults), lineage and change propagation. |

### cardume-platform

| Skill | Purpose |
| --- | --- |
| [`cloud-architecture-best-practices`](../plugins/cardume-platform/skills/cloud-architecture-best-practices/SKILL.md) | Reviews or proposes cloud workload designs as short decision records weighing cost, complexity, reliability and operability, with provider-grounded cost levers for AWS, GCP and Azure. |
| [`cloud-platform-assessment`](../plugins/cardume-platform/skills/cloud-platform-assessment/SKILL.md) | Runs a read-only, risk-based review of a whole cloud estate (AWS, GCP, Azure, Kubernetes) along the provider's Well-Architected pillars and returns evidence-backed risks plus a 30/60/90-day plan. |
| [`deployment-procedures`](../plugins/cardume-platform/skills/deployment-procedures/SKILL.md) | Production deployment principles: safe rollout workflows, pre-deploy verification, rollback strategy, and post-deploy checks, focused on reasoning over fixed scripts. |
| [`finops-budgeting`](../plugins/cardume-platform/skills/finops-budgeting/SKILL.md) | Builds and reviews cloud budgets, forecasts and guardrails with the FinOps Inform/Optimize/Operate model: FOCUS cost data, variance bridges, unit economics, forecast worksheet, commitments. |
| [`kubernetes-operations`](../plugins/cardume-platform/skills/kubernetes-operations/SKILL.md) | Guides work on live Kubernetes clusters with kubectl (GKE, EKS, AKS, on-prem): incident triage, cluster review and inventory, and careful changes. |
| [`observability-patterns`](../plugins/cardume-platform/skills/observability-patterns/SKILL.md) | Guides vendor-neutral observability: OpenTelemetry instrumentation and Collector pipelines, trace-correlated logs, RED/USE, SLOs with multi-burn-rate alerts, dashboards, sampling and cardinality cost control, and telemetry-driven incident investigation. |
| [`project-bootstrap-assistant`](../plugins/cardume-platform/skills/project-bootstrap-assistant/SKILL.md) | Plans the technical/platform foundation of a new or inherited system as a decision log over landing-zone design areas, ending in a platform charter and 90-day backlog for devops-engineer. |
| [`server-management`](../plugins/cardume-platform/skills/server-management/SKILL.md) | Server management principles: process management, monitoring strategy, log handling, and scaling decisions, focused on reasoning over commands. |
| [`terraform-stacks`](../plugins/cardume-platform/skills/terraform-stacks/SKILL.md) | Generates Terraform root modules (stacks) for a project from bundled GCP module and stack templates, plus HCP Terraform Stacks guidance, without running terraform apply. |

### cardume-qa

| Skill | Purpose |
| --- | --- |
| [`red-team-tactics`](../plugins/cardume-qa/skills/red-team-tactics/SKILL.md) | Red team tactics based on MITRE ATT&CK: attack phases, initial access, persistence, lateral movement, detection evasion, and reporting. |
| [`tdd-workflow`](../plugins/cardume-qa/skills/tdd-workflow/SKILL.md) | Test-driven development workflow using the red-green-refactor cycle. |
| [`testing-patterns`](../plugins/cardume-qa/skills/testing-patterns/SKILL.md) | Testing patterns and principles: test pyramid, unit and integration tests, mocking strategies, fixtures, and test organization. |
| [`vulnerability-scanner`](../plugins/cardume-qa/skills/vulnerability-scanner/SKILL.md) | Vulnerability analysis principles: OWASP Top 10 (2025), supply chain security, attack surface mapping, and risk prioritization, with an automated security scan. |
| [`webapp-testing`](../plugins/cardume-qa/skills/webapp-testing/SKILL.md) | Web application testing: E2E strategy, Playwright scripts, visual and accessibility checks, and deep audits of a running site. |

### cardume-games

| Skill | Purpose |
| --- | --- |
| [`game-development`](../plugins/cardume-games/skills/game-development/SKILL.md) | Game development principles across engines: engine selection, game loop and architecture, input, physics, game feel, UI, audio, saves, performance, mobile, multiplayer, testing, accessibility and shipping. |

## Manual commands

These skills set `disable-model-invocation: true`: Claude never starts them on its own. Type them with the plugin prefix.

| Command | Purpose |
| --- | --- |
| [`/cardume-core:brainstorm`](../plugins/cardume-core/skills/brainstorm/SKILL.md) | Explores a project or feature idea before implementation: clarifies the goal and constraints, lays out at least three approaches with pros, cons, and effort, and recommends one. |
| [`/cardume-core:create`](../plugins/cardume-core/skills/create/SKILL.md) | Scaffolds a brand-new application from scratch: asks clarifying questions, has project-planner write a plan, builds it with the app-builder skill and specialist agents, then starts a preview. |
| [`/cardume-core:debug`](../plugins/cardume-core/skills/debug/SKILL.md) | Investigates the given symptom or error systematically: gathers evidence, ranks hypotheses, tests them one by one, fixes the root cause, and reports it in a structured Debug format with prevention steps. |
| [`/cardume-core:enhance`](../plugins/cardume-core/skills/enhance/SKILL.md) | Adds or changes a feature in an existing application: loads project state, plans affected files, asks approval for major changes, applies them via the relevant agents, and refreshes the preview. |
| [`/cardume-core:orchestrate`](../plugins/cardume-core/skills/orchestrate/SKILL.md) | Runs a two-phase multi-agent workflow on the given task: project-planner writes a plan for approval, then 3+ specialist agents implement or analyze in parallel, verification scripts run, and results are merged into one Orchestration Report. |
| [`/cardume-core:plan`](../plugins/cardume-core/skills/plan/SKILL.md) | Creates a project plan file (docs/PLAN-{task-slug}.md) for the given request using the project-planner agent: clarifying questions, task breakdown, agent assignments, and a verification checklist. |
| [`/cardume-core:preview`](../plugins/cardume-core/skills/preview/SKILL.md) | Manages the local development preview server via cardume-auto-preview: start, stop, restart, status, or health check, with port-conflict handling. |
| [`/cardume-core:release`](../plugins/cardume-core/skills/release/SKILL.md) | Prepares a release: checks the approved gate or explicit OK, detects existing release tooling, picks the semver bump with reasons, writes the Keep a Changelog entry and docs/release/vX.Y.Z.md (notes, rollback, honest announcement), and hands over tag/publish commands for confirmation. |
| [`/cardume-core:setup`](../plugins/cardume-core/skills/setup/SKILL.md) | Adds or updates the Cardume conventions block in this project's CLAUDE.md through a deterministic script (backup, diff, only the marked block changes; AGENTS.md is imported, never edited) and suggests stack and code-intelligence plugins. |
| [`/cardume-core:status`](../plugins/cardume-core/skills/status/SKILL.md) | Shows the current project status board: project info and tech stack, features done and pending, agent progress, file counts, and preview server health. |
| [`/cardume-data:review-pr`](../plugins/cardume-data/skills/review-pr/SKILL.md) | Reviews a data/analytics PR: SQL, grain, cost and DAG risks plus data evidence from a configured non-production environment, then drafts a review the user approves before anything is posted. |
| [`/cardume-platform:deploy`](../plugins/cardume-platform/skills/deploy/SKILL.md) | Runs pre-flight checks and deploys to a target environment (preview, staging, or production), with rollback support. |
| [`/cardume-qa:test`](../plugins/cardume-qa/skills/test/SKILL.md) | Generates tests for a file or feature, or runs the test suite, a coverage report, or watch mode. |

The `cardume-*` command-line tools that the plugins put on the PATH are listed in [Safety → Verification commands](SAFETY.md#verification-commands).
