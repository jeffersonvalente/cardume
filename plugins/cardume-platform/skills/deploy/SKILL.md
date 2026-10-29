---
name: deploy
description: "Runs pre-flight checks and deploys to a target environment (preview, staging, or production), with rollback support. Takes an optional environment or subcommand such as check or rollback."
disable-model-invocation: true
argument-hint: "[environment]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-platform:deploy - Production Deployment

$ARGUMENTS

---

## Purpose

This command handles production deployment with pre-flight checks, deployment execution, and verification.

---

## Sub-commands

```
/cardume-platform:deploy            - Interactive deployment wizard
/cardume-platform:deploy check      - Run pre-deployment checks only
/cardume-platform:deploy preview    - Deploy to preview/staging
/cardume-platform:deploy production - Deploy to production
/cardume-platform:deploy rollback   - Rollback to previous version
```

---

## Pre-Deployment Checklist

Before any deployment:

```markdown
## 🚀 Pre-Deploy Checklist

### Code Quality
- [ ] No TypeScript errors (`npx tsc --noEmit`)
- [ ] ESLint passing (`npx eslint .`)
- [ ] All tests passing (`npm test`)

### Security
- [ ] No hardcoded secrets
- [ ] Environment variables documented
- [ ] Dependencies audited (`npm audit`)

### Performance
- [ ] Bundle size acceptable
- [ ] No console.log statements
- [ ] Images optimized

### Documentation
- [ ] README updated
- [ ] CHANGELOG updated
- [ ] API docs current

### Ready to deploy? (y/n)
```

---

## Deployment Flow

```
┌───────────────────────────┐
│  /cardume-platform:deploy │
└────────┬──────────────────┘
         │
         ▼
┌─────────────────┐
│  Pre-flight     │
│  checks         │
└────────┬────────┘
         │
    Pass? ──No──► Fix issues
         │
        Yes
         │
         ▼
┌─────────────────┐
│  Build          │
│  application    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Deploy to      │
│  platform       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Health check   │
│  & verify       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ✅ Complete    │
└─────────────────┘
```

---

## Output Format

### Successful Deploy

```markdown
## 🚀 Deployment Complete

### Summary
- **Version:** v1.2.3
- **Environment:** production
- **Duration:** 47 seconds
- **Platform:** Vercel

### URLs
- 🌐 Production: https://app.example.com
- 📊 Dashboard: https://vercel.com/project

### What Changed
- Added user profile feature
- Fixed login bug
- Updated dependencies

### Health Check
✅ API responding (200 OK)
✅ Database connected
✅ All services healthy
```

### Failed Deploy

```markdown
## ❌ Deployment Failed

### Error
Build failed at step: TypeScript compilation

### Details
```
error TS2345: Argument of type 'string' is not assignable...
```

### Resolution
1. Fix TypeScript error in `src/services/user.ts:45`
2. Run `npm run build` locally to verify
3. Try `/cardume-platform:deploy` again

### Rollback Available
Previous version (v1.2.2) is still active.
Run `/cardume-platform:deploy rollback` if needed.
```

---

## Platform Support

| Platform | Command | Notes |
|----------|---------|-------|
| Vercel | `vercel --prod` | Auto-detected for Next.js |
| Railway | `railway up` | Needs Railway CLI |
| Fly.io | `fly deploy` | Needs flyctl |
| Docker | `docker compose up -d` | For self-hosted |

---

## Examples

```
/cardume-platform:deploy
/cardume-platform:deploy check
/cardume-platform:deploy preview
/cardume-platform:deploy production --skip-tests
/cardume-platform:deploy rollback
```
