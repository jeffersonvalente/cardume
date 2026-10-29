---
name: create
description: "Scaffolds a brand-new application from scratch: asks clarifying questions, has project-planner write a plan, builds it with the app-builder skill and specialist agents, then starts a preview. Not for features in an existing project."
disable-model-invocation: true
argument-hint: "[what to build]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-core:create - Create Application

$ARGUMENTS

---

## Task

This command scaffolds a brand-new application from scratch. For a feature or change in an existing
project, follow the work level instead (level 2 `spec` flow, level 3 `prd` flow).

### Steps:

1. **Request Analysis**
   - Understand what the user wants
   - If information is missing, ask (see the `brainstorming` skill for question patterns)

2. **Project Planning**
   - Use `project-planner` agent for task breakdown
   - Determine tech stack
   - Plan file structure
   - Create the plan file; project-planner returns its questions under **Open questions** — ask the user and resume it
   - Show the plan and wait for the user's approval

3. **Application Building (After Approval)**
   - Orchestrate with `app-builder` skill
   - Coordinate expert agents:
     - `database-architect` → Schema
     - `backend-specialist` → API
     - **design flow (`/cardume-frontend:design-flow`) → UI** (the design entry point, so visual decisions are made before code; `frontend-specialist` executes inside it)

4. **Preview**
   - Start with `cardume-auto-preview start` when complete
   - Present URL to user

---

## Usage Examples

```
/cardume-core:create blog site
/cardume-core:create e-commerce app with product listing and cart
/cardume-core:create todo app
/cardume-core:create Instagram clone
/cardume-core:create crm system with customer management
```

---

## Before Starting

If request is unclear, ask these questions:
- What type of application?
- What are the basic features?
- Who will use it?

Use defaults, add details later.
