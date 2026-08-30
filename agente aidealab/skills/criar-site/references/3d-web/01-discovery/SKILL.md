---
name: 3d-discovery
description: Convert a 3D web request into requirements, constraints, acceptance criteria, and an implementation plan.
---

# Discovery

## Purpose
Turn an ambiguous 3D website request into a concrete technical brief.

## Extract
- Product or experience goal
- Target audience
- Primary user action
- Platforms: desktop, tablet, mobile
- Browser/runtime constraints
- Required 3D assets
- Interactions
- Animation requirements
- Visual direction
- Accessibility requirements
- Performance expectations
- Hosting/deployment constraints
- Existing codebase and dependencies

## Questions
Ask only questions that materially block implementation. Otherwise make explicit, reversible assumptions.

## Acceptance criteria
Define measurable criteria such as:
- model loads successfully
- interaction works with mouse and touch
- mobile fallback exists
- no console errors
- build succeeds
- reduced motion is respected
- scene remains within agreed performance budget

## Handoff
Produce a concise technical brief for `02-architecture`.
