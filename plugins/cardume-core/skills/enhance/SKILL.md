---
name: enhance
description: "Adds or changes a feature in an existing application: loads project state, plans affected files, asks approval for major changes, applies them via the relevant agents, and refreshes the preview."
disable-model-invocation: true
argument-hint: "[feature to add or change]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-core:enhance - Update Application

$ARGUMENTS

---

## Task

This command adds features or makes updates to existing application.

### Steps:

1. **Understand Current State**
   - Load project state with `cardume-session-manager info`
   - Understand existing features, tech stack

2. **Plan Changes**
   - Determine what will be added/changed
   - Detect affected files
   - Check dependencies

3. **Present Plan to User** (for major changes)
   ```
   "To add admin panel:
   - I'll create 15 new files
   - Update 8 files
   - Takes ~10 minutes
   
   Should I start?"
   ```

4. **Apply**
   - Call relevant agents
   - Route UI/UX work (new screens, components, styling, "dark mode", "responsive", "redesign") through the design flow (`/cardume-frontend:design-flow`) so design decisions are made before code; `frontend-specialist` executes inside it.
   - Make changes
   - Test

5. **Update Preview**
   - Hot reload or restart

---

## Usage Examples

```
/cardume-core:enhance add dark mode
/cardume-core:enhance build admin panel
/cardume-core:enhance integrate payment system
/cardume-core:enhance add search feature
/cardume-core:enhance edit profile page
/cardume-core:enhance make responsive
```

---

## Caution

- Get approval for major changes
- Warn on conflicting requests (e.g., "use Firebase" when project uses PostgreSQL)
- Commit each change with git
