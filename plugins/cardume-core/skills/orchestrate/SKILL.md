---
name: orchestrate
description: "Runs a two-phase multi-agent workflow on the given task: project-planner writes a plan for approval, then 3+ specialist agents implement or analyze in parallel, verification scripts run, and results are merged into one Orchestration Report."
disable-model-invocation: true
argument-hint: "[complex task]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# Multi-Agent Orchestration

Coordinate specialized agents to solve this task.

## Task to Orchestrate
$ARGUMENTS

---

## Minimum Agent Requirement

Orchestration means at least 3 different agents. With fewer, you are delegating rather than orchestrating, and the task loses the cross-domain review that justifies this command. Before finishing, count the agents you invoked; if fewer than 3, invoke more from the matrix below.

### Agent Selection Matrix

| Task Type | Suggested Agents (minimum) |
|-----------|---------------------------|
| **Web App** | frontend-specialist, backend-specialist, test-engineer |
| **API** | backend-specialist, security-auditor, test-engineer |
| **UI/Design** | frontend-specialist, seo-specialist, performance-optimizer |
| **Database** | database-architect, backend-specialist, security-auditor |
| **Full Stack** | project-planner, frontend-specialist, backend-specialist, devops-engineer |
| **Debug** | debugger, explorer-agent, test-engineer |
| **Security** | security-auditor, penetration-tester, devops-engineer |

---

## Pre-Flight: Mode Check

| Current Mode | Task Type | Action |
|--------------|-----------|--------|
| **Plan mode** | Any | Proceed with the planning phase only |
| **Normal** | Simple execution | Proceed directly |
| **Normal** | Complex/multi-file | Start with Phase 1 (planning) |

---

## Two-Phase Orchestration

### Phase 1: Planning (sequential, no parallel agents)

| Step | Agent | Action |
|------|-------|--------|
| 1 | `project-planner` | Create `docs/PLAN-{task-slug}.md` |
| 2 | (optional) `explorer-agent` | Codebase discovery if needed |

Use only project-planner and explorer-agent during planning, so implementation doesn't start before the plan is agreed.

### Checkpoint: User Approval

```
After the plan is complete, ask:

"✅ Plan created: docs/PLAN-{task-slug}.md

Do you approve? (Y/N)
- Y: Start implementation
- N: I'll revise the plan"
```

Wait for explicit approval before Phase 2 — implementing an unapproved plan wastes the work of several agents if the user wants changes.

### Phase 2: Implementation (parallel agents after approval)

| Parallel Group | Agents |
|----------------|--------|
| Foundation | `database-architect`, `security-auditor` |
| Core | `backend-specialist`, `frontend-specialist` |
| Polish | `test-engineer`, `devops-engineer` |

After approval, invoke independent agents in parallel.

## Available Agents

| Agent | Domain | Use When |
|-------|--------|----------|
| `project-planner` | Planning | Task breakdown, plan file |
| `explorer-agent` | Discovery | Codebase mapping |
| `frontend-specialist` | UI/UX | React, Vue, CSS, HTML |
| `backend-specialist` | Server | API, Node.js, Python |
| `database-architect` | Data | SQL, NoSQL, Schema |
| `security-auditor` | Security | Vulnerabilities, Auth |
| `penetration-tester` | Security | Active testing |
| `test-engineer` | Testing | Unit, E2E, Coverage |
| `devops-engineer` | Ops | CI/CD, Docker, Deploy |
| `mobile-developer` | Mobile | React Native, Flutter |
| `performance-optimizer` | Speed | Lighthouse, Profiling |
| `seo-specialist` | SEO | Meta, Schema, Rankings |
| `documentation-writer` | Docs | README, API docs |
| `debugger` | Debug | Error analysis |
| `orchestrator` | Meta | Coordination |

The `intelligent-routing` skill lists the rest of the suite (data, platform, design agents).

---

## Orchestration Steps

### Step 1: Analyze Task Domains
Identify every domain this task touches:
```
□ Security     → security-auditor, penetration-tester
□ Backend/API  → backend-specialist
□ Frontend/UI  → frontend-specialist
□ Database     → database-architect
□ Testing      → test-engineer
□ DevOps       → devops-engineer
□ Mobile       → mobile-developer
□ Performance  → performance-optimizer
□ SEO          → seo-specialist
□ Planning     → project-planner
```

### Step 2: Phase Detection

| If Plan Exists | Action |
|----------------|--------|
| No plan in `docs/` | → Phase 1 (planning only) |
| Plan exists + user approved | → Phase 2 (implementation) |

### Step 3: Execute Based on Phase

**Phase 1 (Planning):**
```
Use the project-planner agent to create the plan
→ stop after the plan is created
→ ask the user for approval
```

**Phase 2 (Implementation, after approval):**
```
Invoke agents in parallel:
Use the frontend-specialist agent to [task]
Use the backend-specialist agent to [task]
Use the test-engineer agent to [task]
```

**Context passing**

Subagents start with no memory of this conversation, so every invocation needs:

1. **Original user request:** full text of what the user asked
2. **Decisions made:** all user answers to clarifying questions
3. **Previous agent work:** summary of what earlier agents did
4. **Current plan state:** plan files in the workspace, if any

**Example with full context:**
```
Use the project-planner agent to create the plan:

**CONTEXT:**
- User Request: "A social platform for students, using mock data"
- Decisions: Tech=Vue 3, Layout=Grid Widgets, Auth=Mock, Design=Youthful & dynamic
- Previous Work: Orchestrator asked 6 questions, user chose all options
- Current Plan: docs/PLAN-student-social.md exists with initial structure

**TASK:** Create a detailed plan based on the decisions above. Don't infer anything from the folder name.
```

Without this context the subagent will make its own (usually wrong) assumptions.

### Step 4: Verification
The last agent runs the verification scripts:
```bash
cardume-security-scan .
cardume-lint-runner .
```

### Step 5: Synthesize Results
Combine all agent outputs into a unified report.

---

## Output Format

```markdown
## 🎼 Orchestration Report

### Task
[Original task summary]

### Agents Invoked (minimum 3)
| # | Agent | Focus Area | Status |
|---|-------|------------|--------|
| 1 | project-planner | Task breakdown | ✅ |
| 2 | frontend-specialist | UI implementation | ✅ |
| 3 | test-engineer | Verification scripts | ✅ |

### Verification Scripts Executed
- [x] cardume-security-scan → Pass/Fail
- [x] cardume-lint-runner → Pass/Fail

### Key Findings
1. **[Agent 1]**: Finding
2. **[Agent 2]**: Finding
3. **[Agent 3]**: Finding

### Deliverables
- [ ] Plan created
- [ ] Code implemented
- [ ] Tests passing
- [ ] Scripts verified

### Summary
[One paragraph synthesis of all agent work]
```

---

## Completion Check

Before reporting orchestration complete, verify:

1. ✅ **Agent count:** 3 or more agents invoked
2. ✅ **Scripts executed:** at least `cardume-security-scan` ran
3. ✅ **Report generated:** Orchestration Report lists all agents

If a check fails, invoke more agents or run the scripts before finishing.
