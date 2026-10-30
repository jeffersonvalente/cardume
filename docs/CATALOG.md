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
| [`design-flow`](../plugins/cardume-frontend/agents/design-flow.md) | Designs and iterates on frontend UI through shape, craft, critique, audit and polish, writing production code. |
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
| [`adr`](../plugins/cardume-core/skills/adr/SKILL.md) | Records a decision in docs/adr/ with options and consequences, and updates the index. |
| [`app-builder`](../plugins/cardume-core/skills/app-builder/SKILL.md) | Scaffolds a new app from a plain request: picks the stack and coordinates specialists. |
| [`architecture`](../plugins/cardume-core/skills/architecture/SKILL.md) | Weighs trade-offs and picks patterns (monolith or microservices, layering, events). |
| [`bash-linux`](../plugins/cardume-core/skills/bash-linux/SKILL.md) | Bash patterns and script templates for Linux and macOS. |
| [`behavioral-modes`](../plugins/cardume-core/skills/behavioral-modes/SKILL.md) | Working modes (brainstorm, implement, debug, review, teach, ship) and the output style of each. |
| [`brainstorming`](../plugins/cardume-core/skills/brainstorming/SKILL.md) | Asks the clarifying questions that shape a vague idea: purpose, users, scope, trade-offs. |
| [`clean-code`](../plugins/cardume-core/skills/clean-code/SKILL.md) | Coding standards (SRP, DRY, KISS, YAGNI, naming) with a pre-edit dependency check and a completion self-check. |
| [`code-review-checklist`](../plugins/cardume-core/skills/code-review-checklist/SKILL.md) | Checklist for correctness, security, performance and tests, with severity-tagged comments. |
| [`database-design`](../plugins/cardume-core/skills/database-design/SKILL.md) | Picks a database and ORM, designs schemas and indexes, plans safe migrations. |
| [`documentation-templates`](../plugins/cardume-core/skills/documentation-templates/SKILL.md) | Structure templates for READMEs, API docs, code comments, changelogs and llms.txt. |
| [`gate`](../plugins/cardume-core/skills/gate/SKILL.md) | Checks every acceptance criterion against executed evidence and writes a report in docs/gates/ with an APPROVE/REJECT recommendation. |
| [`generator-pr-description`](../plugins/cardume-core/skills/generator-pr-description/SKILL.md) | Drafts a PR title and body from the branch's full diff, then creates or updates the PR after confirmation. |
| [`implement`](../plugins/cardume-core/skills/implement/SKILL.md) | Builds an approved tasks.md one task at a time, with a fresh subagent, a verification command and a separate reviewer. |
| [`intelligent-routing`](../plugins/cardume-core/skills/intelligent-routing/SKILL.md) *(internal)* | Domain-to-agent routing table. |
| [`lint-and-validate`](../plugins/cardume-core/skills/lint-and-validate/SKILL.md) | Lint, type-check and security-scan commands per ecosystem, with a fix-and-rerun loop. |
| [`parallel-agents`](../plugins/cardume-core/skills/parallel-agents/SKILL.md) | Runs Cardume agents singly, in sequence or in parallel and merges the results. |
| [`plan-writing`](../plugins/cardume-core/skills/plan-writing/SKILL.md) | Writes a short plan file of 5-10 verifiable tasks with dependencies. |
| [`powershell-windows`](../plugins/cardume-core/skills/powershell-windows/SKILL.md) | Windows PowerShell pitfalls: logical operators, ASCII output, ConvertTo-Json depth, paths, errors. |
| [`prd`](../plugins/cardume-core/skills/prd/SKILL.md) | Writes a PRD in docs/prd/ with metrics, acceptance criteria, no-gos, risks and blockers. |
| [`python-patterns`](../plugins/cardume-core/skills/python-patterns/SKILL.md) | Picks a Python framework, async model and project structure, with typing and testing guidance. |
| [`review`](../plugins/cardume-core/skills/review/SKILL.md) | Reviews a change with parallel specialist reviewers, verifies each finding against the code and flags outdated specs. |
| [`spec`](../plugins/cardume-core/skills/spec/SKILL.md) | Asks the questions that change the design, then writes a spec in docs/specs/ with testable requirements and non-goals. |
| [`standards`](../plugins/cardume-core/skills/standards/SKILL.md) | Scans the repository and writes docs/standards.md with its real conventions, each backed by evidence. |
| [`systematic-debugging`](../plugins/cardume-core/skills/systematic-debugging/SKILL.md) | Four-phase debugging: reproduce, isolate, find the root cause, fix and verify. |
| [`tasks`](../plugins/cardume-core/skills/tasks/SKILL.md) | Breaks an approved spec into ordered tasks in tasks.md, each with an owner and a verification command, optionally opening GitHub issues. |
| [`verify`](../plugins/cardume-core/skills/verify/SKILL.md) | Runs every acceptance criterion of a spec and records evidence in verify.md, listing gaps. |

### cardume-frontend

| Skill | Purpose |
| --- | --- |
| [`design-flow`](../plugins/cardume-frontend/skills/design-flow/SKILL.md) | Designs and iterates on frontend interfaces through a shape, craft, critique, audit, and polish flow, writing production-grade code for websites, landing pages, dashboards, product UI, app shells, components, forms, settings, onboarding, and empty states. |
| [`frontend-design`](../plugins/cardume-frontend/skills/frontend-design/SKILL.md) | Design principles for web UI: constraints, layout, color, typography, motion, anti-cliché checks. |
| [`geo-fundamentals`](../plugins/cardume-frontend/skills/geo-fundamentals/SKILL.md) | Optimizes content for citation in AI answer engines. |
| [`i18n-localization`](../plugins/cardume-frontend/skills/i18n-localization/SKILL.md) | Finds hardcoded strings and structures locales, plurals, formats and RTL. |
| [`mobile-design`](../plugins/cardume-frontend/skills/mobile-design/SKILL.md) | Mobile UX for iOS and Android: touch targets, lists, offline, navigation, platform conventions. |
| [`performance-profiling`](../plugins/cardume-frontend/skills/performance-profiling/SKILL.md) | Measures before optimizing: Core Web Vitals, Lighthouse, bundle, runtime and memory profiling. |
| [`react-best-practices`](../plugins/cardume-frontend/skills/react-best-practices/SKILL.md) | React and Next.js performance rules: waterfalls, bundle size, server rendering, re-renders. |
| [`react-native-skills`](../plugins/cardume-frontend/skills/react-native-skills/SKILL.md) | React Native and Expo rules for lists, animations, navigation, images and native modules. |
| [`seo-fundamentals`](../plugins/cardume-frontend/skills/seo-fundamentals/SKILL.md) | SEO essentials: E-E-A-T, technical SEO, metadata, schema markup. |
| [`site-building`](../plugins/cardume-frontend/skills/site-building/SKILL.md) | Runs website delivery from brief to launch: sitemap, static-first stack, SEO, LGPD/GDPR consent, quality gates. |
| [`tailwind-patterns`](../plugins/cardume-frontend/skills/tailwind-patterns/SKILL.md) | Tailwind CSS v4 with @theme tokens, container queries and dark mode. |
| [`web-design-guidelines`](../plugins/cardume-frontend/skills/web-design-guidelines/SKILL.md) | Reviews UI code against the Web Interface Guidelines. |

### cardume-backend

| Skill | Purpose |
| --- | --- |
| [`api-patterns`](../plugins/cardume-backend/skills/api-patterns/SKILL.md) | Chooses REST, GraphQL or tRPC and sets versioning, pagination, auth and rate limits. |
| [`java-spring-patterns`](../plugins/cardume-backend/skills/java-spring-patterns/SKILL.md) | Java 17+ and Spring Boot 3/4 architecture, idioms, transactions and testing. |
| [`mcp-builder`](../plugins/cardume-backend/skills/mcp-builder/SKILL.md) | MCP server tool design, schemas, errors and security. |
| [`nodejs-best-practices`](../plugins/cardume-backend/skills/nodejs-best-practices/SKILL.md) | Picks Node.js frameworks and async, error and security patterns. |
| [`rust-pro`](../plugins/cardume-backend/skills/rust-pro/SKILL.md) | Rust 2024 with Tokio and axum: async, types, errors, performance. |

### cardume-data

| Skill | Purpose |
| --- | --- |
| [`airflow-testing`](../plugins/cardume-data/skills/airflow-testing/SKILL.md) | Tests and CI for Airflow DAGs (Airflow 3, Cloud Composer): parse and property tests, top-level hazards, Ruff AIR rules. |
| [`bigquery-patterns`](../plugins/cardume-data/skills/bigquery-patterns/SKILL.md) | BigQuery SQL discipline: dry runs, byte caps, pruning, safe joins, integrity checks. |
| [`gcp-observability-patterns`](../plugins/cardume-data/skills/gcp-observability-patterns/SKILL.md) | Read-only GCP investigation: Composer failures, BigQuery job errors, slot and cost spikes, missing files, audit logs. |
| [`lakehouse-architecture`](../plugins/cardume-data/skills/lakehouse-architecture/SKILL.md) | Medallion lakehouse on BigQuery: layers, naming, dimensional modeling, lineage. |

### cardume-platform

| Skill | Purpose |
| --- | --- |
| [`cloud-architecture-best-practices`](../plugins/cardume-platform/skills/cloud-architecture-best-practices/SKILL.md) | Reviews or proposes cloud workload designs as short decision records weighing cost and reliability on AWS, GCP and Azure. |
| [`cloud-platform-assessment`](../plugins/cardume-platform/skills/cloud-platform-assessment/SKILL.md) | Read-only, risk-based Well-Architected review of a whole cloud estate with a 30/60/90-day plan. |
| [`deployment-procedures`](../plugins/cardume-platform/skills/deployment-procedures/SKILL.md) | Safe rollout, pre-deploy checks, rollback and post-deploy verification. |
| [`finops-budgeting`](../plugins/cardume-platform/skills/finops-budgeting/SKILL.md) | Cloud budgets, forecasts, guardrails and unit economics with the FinOps model. |
| [`kubernetes-operations`](../plugins/cardume-platform/skills/kubernetes-operations/SKILL.md) | Works on live clusters with kubectl: triage, review and careful changes, read-only by default. |
| [`observability-patterns`](../plugins/cardume-platform/skills/observability-patterns/SKILL.md) | Vendor-neutral OpenTelemetry, SLOs, burn-rate alerts, dashboards and cardinality cost. |
| [`project-bootstrap-assistant`](../plugins/cardume-platform/skills/project-bootstrap-assistant/SKILL.md) | Plans the platform foundation of a new or inherited system, ending in a charter and 90-day backlog. |
| [`server-management`](../plugins/cardume-platform/skills/server-management/SKILL.md) | Linux server process management, monitoring, logs and scaling. |
| [`terraform-stacks`](../plugins/cardume-platform/skills/terraform-stacks/SKILL.md) | Generates Terraform root modules from bundled GCP templates, without running apply. |

### cardume-qa

| Skill | Purpose |
| --- | --- |
| [`red-team-tactics`](../plugins/cardume-qa/skills/red-team-tactics/SKILL.md) | MITRE ATT&CK-based adversary tactics and reporting. |
| [`tdd-workflow`](../plugins/cardume-qa/skills/tdd-workflow/SKILL.md) | TDD red-green-refactor workflow. |
| [`testing-patterns`](../plugins/cardume-qa/skills/testing-patterns/SKILL.md) | Test pyramid, mocking, fixtures and test organization. |
| [`vulnerability-scanner`](../plugins/cardume-qa/skills/vulnerability-scanner/SKILL.md) | OWASP Top 10, supply chain and attack surface analysis with an automated scan. |
| [`webapp-testing`](../plugins/cardume-qa/skills/webapp-testing/SKILL.md) | E2E strategy, Playwright scripts, and visual and accessibility checks. |

### cardume-games

| Skill | Purpose |
| --- | --- |
| [`game-development`](../plugins/cardume-games/skills/game-development/SKILL.md) | Game engine choice, game loop, input, physics, game feel, saves and shipping. |

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
