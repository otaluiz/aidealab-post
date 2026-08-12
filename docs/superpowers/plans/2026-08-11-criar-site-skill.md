# criar-site Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the `criar-site` Agent Skill to `agente aidealab/skills/`, implementing the site-generation flow approved in the design spec, and update the skills catalog README.

**Architecture:** Single-file instruction skill (`SKILL.md`), same pattern as the already-implemented `criar-cliente` — no code, no automated tests, just a precise procedure document consumed by Claude Code at runtime. It orchestrates existing tools/skills (Google Drive MCP, `taste-skill`, `ui-ux-pro-max`, `ui-styling`, git) rather than containing logic itself.

**Tech Stack:** N/A — markdown skill definition only. Runtime dependencies (Drive MCP, `taste-skill`, `ui-ux-pro-max`, `ui-styling`, git, stack scaffolding tools) are invoked by whichever Claude Code session runs the finished skill, not by this plan.

## Global Constraints

- Client `parentId` in Drive: `1xHuFxkYD0INTpdZbzBZLRBy-X3tVM-rv` (same constant `criar-cliente` uses).
- Reference folders read: `00-Identidade-e-Tom`, `01-Referencias/Site` (fallback to `01-Referencias/Instagram` only if `Site` is empty).
- Site repos created at `D:\claude\sites\<cliente-normalizado>\`; client name lowercased, spaces replaced with hyphens (e.g. "Hora da Chipa" → `hora-da-chipa`).
- Two mandatory approval checkpoints — after Etapa 2 (direção de design) and after Etapa 3 (plano de conteúdo) — no code/repo is created before both are approved.
- Explicitly out of scope: deploy/hosting, domain purchase, GitHub push, auto-running `criar-cliente`, using the `frontend-design` skill, fixing one stack for all sites.
- Source of truth for every content decision below: `docs/superpowers/specs/2026-08-11-criar-site-skill-design.md` (already written, self-reviewed, and committed).

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
description: Gera um site novo para um cliente da aidealab a partir das referências e identidade de marca já organizadas no Drive pela criar-cliente. Usa taste-skill para direção de design anti-slop e ui-ux-pro-max para paleta/tipografia/stack concretos e consistência entre páginas via design system persistido. Dispara com "criar site <cliente>" / "crie o site do cliente <cliente>" / "novo site <cliente>". Para em dois checkpoints de aprovação (direção de design, plano de conteúdo) antes de escrever qualquer código.
---
```

- [ ] **Step 2: Write "Quando usar" + pré-requisito**

Mirror the trigger-phrasing tone of `agente aidealab/skills/criar-cliente/SKILL.md:14-18`. State the pre-requisite explicitly: search `Clientes` (parentId above) case-insensitive for the client folder; if missing, **stop** and tell the user to run `criar-cliente` first — never invoke it automatically (one responsibility per skill, matching the convention already stated in `agente aidealab/skills/README.md:19-26`).

- [ ] **Step 3: Write the 6-stage flow**, one subsection per stage, transcribing the decisions from the spec's "Comportamento" section verbatim (not paraphrased loosely — the spec already has the exact wording validated with the user):
  - **Etapa 1 — Coleta de referências**: read `00-Identidade-e-Tom` and `01-Referencias/Site` (fallback `01-Referencias/Instagram` if `Site` empty); if material is insufficient, ask the user directly for brand/business context instead of blocking or inventing.
  - **Etapa 2 — Direção de design**: invoke `taste-skill` with the Etapa 1 material as brief to get the "leitura de design" + three dials (`DESIGN_VARIANCE`, `MOTION_INTENSITY`, `VISUAL_DENSITY`); invoke `ui-ux-pro-max` (`--design-system` with `--variance`/`--motion`/`--density` set from those dials) to get concrete palette/typography/stack; present both to the user. **Checkpoint 1** — wait for explicit approval before continuing; if changes requested, refine and re-present.
  - **Etapa 3 — Plano de conteúdo e páginas**: propose page/section structure and key-copy outline from the approved direction; present to the user. **Checkpoint 2** — wait for explicit approval before building.
  - **Etapa 4 — Construção**: normalize client name (lowercase, spaces→hyphens); `git init` a new repo at `D:\claude\sites\<cliente-normalizado>\`; re-run `ui-ux-pro-max --design-system --persist --output-dir <repo-root>` to write `design-system/<projeto>/MASTER.md` with the approved direction; implement following `MASTER.md` + the approved content plan, using `ui-styling` when the stack is Tailwind/shadcn-based or `ui-ux-pro-max --stack <nome>` guidance otherwise; note explicitly in the doc that this stage (and Etapa 2) are the extension points for future site-development skills the user may add later.
  - **Etapa 5 — Preview**: start the chosen stack's local dev server and show the running site to the user before finalizing.
  - **Etapa 6 — Relatório final**: report local repo path, chosen stack, chosen palette/typography, and a summary of what was built.

- [ ] **Step 4: Write "Ferramentas necessárias"**

List: Drive MCP (`search_files`) for Etapa 1 and the pre-requisite check; the `taste-skill` and `ui-ux-pro-max` skills (invoked via the Skill tool, not by shelling into their internal scripts directly) for Etapa 2 and 4; the `ui-styling` skill for Tailwind/shadcn builds; local `git`; and the dev-server tooling of whichever stack gets chosen.

- [ ] **Step 5: Write "O que reportar sempre"**

Mirror the structure of `agente aidealab/skills/criar-cliente/SKILL.md:67-72`: local repo path, design system summary (palette/typography/stack), and what was created in this run.

- [ ] **Step 6: Write "Fora de escopo"**

Transcribe the 6 bullets from the spec's "Fora de escopo" section verbatim: deploy/hosting/domain purchase; GitHub push; final copy without user approval; auto-running `criar-cliente`; using the standard `frontend-design` skill; fixing one stack for every site.

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
| `criar-site` | sim | gera o site do cliente a partir das referências do Drive, usando taste-skill + ui-ux-pro-max para a direção de design |
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
