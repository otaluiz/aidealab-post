# criar-site Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the `criar-site` Agent Skill to `agente aidealab/skills/`, implementing the site-generation flow approved in the design spec, and update the skills catalog README.

**Architecture:** Single-file instruction skill (`SKILL.md`), same pattern as the already-implemented `criar-cliente` — no code, no automated tests, just a precise procedure document consumed by Claude Code at runtime. It orchestrates existing tools/skills (Google Drive MCP, `impeccable`, `ui-ux-pro-max`, `ui-styling`, `Shadcn_UI` MCP, `21st.dev` MCP, `gsap-framer-scroll-animation`, `gsap-skills`, git) rather than containing logic itself.

**Tech Stack:** N/A for the plan itself — markdown skill definition only. The sites `criar-site` generates are fixed to React + Next.js (Vercel-ready). Runtime dependencies (Drive MCP, `impeccable`, `ui-ux-pro-max`, `ui-styling`, `Shadcn_UI` MCP, `21st.dev` MCP, `gsap-framer-scroll-animation`, `gsap-skills`, git, Next.js dev server) are invoked by whichever Claude Code session runs the finished skill, not by this plan.

## Global Constraints

- Client `parentId` in Drive: `1xHuFxkYD0INTpdZbzBZLRBy-X3tVM-rv` (same constant `criar-cliente` uses).
- Reference folders read: `00-Identidade-e-Tom`, `01-Referencias/Site` (fallback to `01-Referencias/Instagram` only if `Site` is empty).
- Site repos created at `D:\claude\sites\<cliente-normalizado>\`; client name lowercased, spaces replaced with hyphens (e.g. "Hora da Chipa" → `hora-da-chipa`).
- Stack is fixed: React + Next.js (Vercel-ready) for every site — not decided case-by-case.
- Two mandatory approval checkpoints — after Etapa 2 (direção de design) and after Etapa 3 (plano de conteúdo) — no code/repo is created before both are approved.
- `impeccable` is the backbone of Etapa 2 (direção) and Etapa 4 (construção + QA final via `audit`/`polish`). `ui-ux-pro-max` is consulted pointwise for concrete data (palettes, typography, stack guidance, including `--stack threejs` when applicable), not the owner of persistence — `impeccable`'s own `PRODUCT.md`/`DESIGN.md` own that. `taste-skill` is dropped (redundant with `impeccable`).
- Components (3-tier hierarchy): `Originkit` MCP (ready-made marketing sections — hero, navbar, pricing, cards, forms — with native Framer Motion) first; `Shadcn_UI` MCP (official registry) for primitives Originkit doesn't cover; `21st.dev` MCP (broader catalog + AI generation) only as the final fallback.
- Animation: `gsap-framer-scroll-animation` (Framer Motion) is the default for component transitions/micro-interactions; `gsap-skills:gsap-scrolltrigger` + `gsap-skills:gsap-react` (GSAP) are reserved for complex scroll-driven animation (pinning, horizontal scroll, choreography).
- 3D and video are conditional — only when the approved design direction calls for them: React Three Fiber + `@react-three/drei` + `@react-three/postprocessing` + `Lenis` for procedural 3D/smooth scroll (no custom 3D models, no Blender MCP — evaluated and dropped); GSAP-scrubbed `<video>` for scroll-driven video, `useVideoTexture` (drei) for video-as-3D-texture, plain `<video>` for backgrounds — no video CDN/streaming service by default.
- `marketing:content-creation` drafts conversion copy (headlines, CTAs) in Etapa 3 — not placeholder text.
- Explicitly out of scope: deploy/hosting, domain purchase, GitHub push, auto-running `criar-cliente`, using `taste-skill` standalone or the `frontend-design` skill, deciding stack case-by-case, creating/managing Drive folders (exclusive to `criar-cliente`), custom 3D models/Blender MCP, video CDN/streaming.
- Source of truth for every content decision below: `docs/superpowers/specs/2026-08-11-criar-site-skill-design.md` (revised twice after this plan's Task 1 first pass — read the current version, not a cached copy; every decision in its "Comportamento", "Implementação", and "Fora de escopo" sections is binding).

---

## Task 1: Write `agente aidealab/skills/criar-site/SKILL.md`

**Files:**
- Create: `agente aidealab/skills/criar-site/SKILL.md`

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-08-11-criar-site-skill-design.md` (all content decisions).
- Produces: the `criar-site` skill itself — triggered by "criar site \<cliente\>" / "crie o site do cliente \<cliente\>" / "novo site \<cliente\>". Nothing else in the repo calls into it programmatically.

- [ ] **Step 1: Write the YAML frontmatter**

```yaml
---
name: criar-site
description: Gera um site novo (React + Next.js) para um cliente da aidealab a partir das referências e identidade de marca já organizadas no Drive pela criar-cliente. Usa impeccable como espinha dorsal de direção de design anti-slop, construção e QA final, consultando ui-ux-pro-max para dados concretos, os MCPs Originkit/Shadcn_UI/21st.dev para componentes, e opcionalmente React Three Fiber/GSAP/Lenis para 3D e vídeo scroll-driven quando a direção pedir. Dispara com "criar site <cliente>" / "crie o site do cliente <cliente>" / "novo site <cliente>". Para em dois checkpoints de aprovação (direção de design, plano de conteúdo) antes de escrever qualquer código.
---
```

- [ ] **Step 2: Write "Quando usar" + pré-requisito**

Mirror the trigger-phrasing tone of `agente aidealab/skills/criar-cliente/SKILL.md:14-18`. State the pre-requisite explicitly: search `Clientes` (parentId above) case-insensitive for the client folder; if missing, **stop** and tell the user to run `criar-cliente` first — never invoke it automatically (one responsibility per skill, matching the convention already stated in `agente aidealab/skills/README.md:19-26`).

- [ ] **Step 3: Write the 6-stage flow**, one subsection per stage, transcribing the decisions from the spec's current "Comportamento" section verbatim (re-read the spec now — it was revised twice since Task 1's first pass; do not reuse wording from an earlier session):
  - **Etapa 1 — Coleta de referências**: read `00-Identidade-e-Tom` and `01-Referencias/Site` (fallback `01-Referencias/Instagram` if `Site` empty); if material is insufficient, ask the user directly for brand/business context instead of blocking or inventing.
  - **Etapa 2 — Direção de design**: invoke `impeccable` (command `shape`, or the new-work flow for a client's first site) with the Etapa 1 material as context to get the mode (Persuade) and an anti-slop design direction; when `impeccable` needs a concrete data point (palette/typography options for the identified vibe), it consults `ui-ux-pro-max` pointwise; present the direction (mode, palette, typography) to the user. **Checkpoint 1** — wait for explicit approval before continuing; if changes requested, refine and re-present.
  - **Etapa 3 — Plano de conteúdo e páginas**: propose page/section structure and, using `marketing:content-creation`, a conversion-copy outline (headlines, CTAs, key text) from the approved direction — not placeholder text; present to the user. **Checkpoint 2** — wait for explicit approval before building.
  - **Etapa 4 — Construção**: normalize client name (lowercase, spaces→hyphens); `git init` a new React + Next.js repo at `D:\claude\sites\<cliente-normalizado>\`; `impeccable` builds the site following the approved direction and content plan, persisting project context in `PRODUCT.md`/`DESIGN.md`; for components (3-tier), check `Originkit` MCP first (ready-made marketing sections), then `Shadcn_UI` MCP (official primitives) for what Originkit doesn't cover, then `21st.dev` MCP (broader catalog + AI generation) as the final fallback; for animation, use `gsap-framer-scroll-animation` (Framer Motion) by default for component transitions/micro-interactions, and `gsap-skills:gsap-scrolltrigger` + `gsap-skills:gsap-react` (GSAP) specifically for complex scroll-driven animation; **conditionally, only when the approved direction calls for it**, add React Three Fiber + `@react-three/drei` + `@react-three/postprocessing` + `Lenis` for procedural 3D/smooth scroll (no custom models, no Blender), plus GSAP-scrubbed `<video>`, `useVideoTexture` (drei) for 3D video textures, and plain `<video>` for background video (no CDN); before moving on, run `impeccable audit` + `impeccable polish` (or the `impeccable-finish-reviewer` subagent) as a final QA pass; note explicitly in the doc that this stage (and Etapa 2) are the extension points for future site-development skills the user may add later.
  - **Etapa 5 — Preview**: start the Next.js local dev server and show the running site to the user before finalizing.
  - **Etapa 6 — Relatório final**: report local repo path, chosen design direction (palette/typography/mode), a summary of what was built, and the QA result from `impeccable audit`/`polish`.

- [ ] **Step 4: Write "Ferramentas necessárias"**

List: Drive MCP (`search_files`, read-only — `criar-site` never creates/manages Drive folders, that stays exclusive to `criar-cliente`) for Etapa 1 and the pre-requisite check; the `impeccable` skill (+ its `impeccable-finish-reviewer` and `impeccable-asset-producer` subagents where applicable, invoked via the Skill/Agent tools, not by shelling into internal scripts directly) for Etapa 2 and 4; the `ui-ux-pro-max` skill (also via the Skill tool) as a pointwise data reference in Etapa 2 and 4; the `marketing:content-creation` skill for conversion copy in Etapa 3; the `ui-styling` skill for Tailwind/shadcn implementation reference; the `Originkit` MCP for ready-made marketing sections; the `Shadcn_UI` MCP for the official component/block/theme registry; the `21st.dev` MCP for extended component search/generation; the `gsap-framer-scroll-animation` skill for Framer Motion; the `gsap-skills:gsap-scrolltrigger` and `gsap-skills:gsap-react` skills for complex scroll animation; React Three Fiber/`drei`/`postprocessing`/`Lenis` (code libraries, conditional on the approved direction) for 3D/video; local `git`; and the Next.js local dev server for Etapa 5.

- [ ] **Step 5: Write "O que reportar sempre"**

Mirror the structure of `agente aidealab/skills/criar-cliente/SKILL.md:67-72`: local repo path, design system summary (palette/typography/stack), and what was created in this run.

- [ ] **Step 6: Write "Fora de escopo"**

Transcribe the current bullets from the spec's "Fora de escopo" section verbatim (re-read the spec — this section was revised twice): deploy/hosting/domain purchase; GitHub push; final copy without user approval; auto-running `criar-cliente`; using `taste-skill` standalone or the standard `frontend-design` skill; deciding stack case-by-case (it's fixed to React + Next.js now); creating/managing Drive client folders (exclusive to `criar-cliente`); custom 3D models/Blender MCP; video CDN/streaming hosting.

- [ ] **Step 7: Cross-check against the spec**

Read the finished `SKILL.md` side-by-side with `docs/superpowers/specs/2026-08-11-criar-site-skill-design.md` section by section (Comportamento, Implementação, Fora de escopo) and confirm nothing was dropped or contradicted. Fix any gap found.

- [ ] **Step 8: Commit**

```bash
git add "agente aidealab/skills/criar-site/SKILL.md"
git commit -m "Add criar-site skill"
```

## Task 2: Update the skills catalog README

**Files:**
- Modify: `agente aidealab/skills/README.md`

**Interfaces:**
- Consumes: the existing table format at `agente aidealab/skills/README.md:8-13` and the "Planejadas" sentence at `agente aidealab/skills/README.md:14-17`.

- [ ] **Step 1: Add the catalog row**

```markdown
| `criar-site` | sim | gera o site do cliente (React + Next.js, com 3D/vídeo condicional) a partir das referências do Drive, usando impeccable como espinha dorsal de direção/construção/QA |
```

- [ ] **Step 2: Update the "Planejadas" sentence**

Remove `criar site` from the not-yet-created list, leaving only `criar carrossel` e `postar no Instagram`.

- [ ] **Step 3: Commit**

```bash
git add "agente aidealab/skills/README.md"
git commit -m "Add criar-site to skills catalog"
```

## Verification

This is a prose-only Agent Skill (no runtime code to unit test — same as `criar-cliente`), so verification is manual:

1. Read the finished `SKILL.md` end-to-end and confirm it reads as one coherent, executable procedure — no placeholders, no contradiction with the spec.
2. Confirm the YAML frontmatter parses cleanly (e.g. `python -c "import yaml; yaml.safe_load(open('agente aidealab/skills/criar-site/SKILL.md', encoding='utf-8').read().split('---')[1])"`) so the skill is discoverable by name/description matching.
3. Confirm `agente aidealab/skills/README.md` renders correctly — table row aligned with the existing columns, "Planejadas" sentence still reads naturally.
4. Optional dry run: in a fresh Claude Code session against this repo, say "criar site \<cliente de teste existente no Drive\>" and confirm it stops correctly at Checkpoint 1 without creating any repo or files — this exercises the trigger phrase and the pre-requisite check without needing a full site build.
