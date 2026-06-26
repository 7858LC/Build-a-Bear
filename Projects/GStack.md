---
title: "GStack"
type: resource
tags:
  - tools
  - claude-code
  - ai
  - development
source: https://github.com/garrytan/gstack
author: Garry Tan (Y Combinator)
installed: 2026-06-23
---

# GStack

> *"Ship like a team of twenty."*

An open-source AI coding toolkit by **Garry Tan** (President & CEO, Y Combinator) that augments Claude Code with 23 specialized slash commands — simulating an entire engineering team from a single developer.

## What It Does

Instead of a blank AI prompt, GStack gives you opinionated agent roles: CEO, designer, engineering manager, QA lead, security officer, release engineer. Each slash command embodies a different specialist perspective.

## Key Slash Commands

| Command | Role |
|---------|------|
| `/office-hours` | Product validation — forcing questions on your idea |
| `/plan-ceo-review` | Strategic plan review |
| `/plan-eng-review` | Engineering plan review |
| `/plan-design-review` | Design plan review |
| `/review` | Code review |
| `/qa` | QA testing pass |
| `/ship` | Deployment pipeline |
| `/cso` | Security audit (OWASP + STRIDE) |
| `/browse` | Real Chromium browser control with AI |
| `/design-shotgun` | Visual design generation |
| `/design-html` | Design to production code |
| `/spec` | Write technical specs |
| `/investigate` | Deep code investigation |
| `/diagram` | Architecture diagrams |

## Tech Stack

- **Language:** TypeScript (79%), Go Template (11%), Shell (6%)
- **Runtime:** Bun / Node.js
- **Browser:** Playwright + Chrome DevTools Protocol
- **Memory (optional):** Supabase or PGLite (via GBrain)

## Installation

```bash
git clone https://github.com/garrytan/gstack ~/.claude/skills/gstack
```

**Status on this server:** ✅ Installed at `~/.claude/skills/gstack`

## Notes

- MIT licensed — free and open source
- Garry Tan reported ~810× increase in productivity vs. 2013 baseline
- GBrain adds persistent memory across sessions (optional Supabase setup)
- Works best alongside the existing Claude Code hooks already configured

## Links

- [GitHub Repository](https://github.com/garrytan/gstack)
- [[The-Unseen-Layer|The Unseen Layer]] — apply `/plan-eng-review` and `/cso` here
