---
name: 3d-web-master
description: Master orchestrator for building production-ready interactive 3D web experiences with Claude Code, React/Next.js, Three.js, React Three Fiber, Drei, GLTF/GLB assets, animations, interactions, performance optimization, accessibility, testing, and deployment.
---

# 3D Web Master Orchestrator

## Mission
Orchestrate specialized skills to design, implement, validate, optimize, and deploy generalized 3D web experiences.

## Core principle
Do not solve every problem in one prompt. Decompose the request into specialized modules, execute them in dependency order, and integrate their outputs into a coherent implementation.

## Default stack
- TypeScript
- React / Next.js
- Three.js
- React Three Fiber
- @react-three/drei
- GLTF/GLB
- Tailwind CSS when a utility UI layer is useful

Adapt the stack when the project explicitly requires another framework.

## Workflow
1. Inspect the user's goal, constraints, existing repository, assets, and runtime.
2. Invoke `01-discovery` to define requirements and acceptance criteria.
3. Invoke `02-architecture` to define project structure and technical boundaries.
4. Invoke `03-assets` to inspect, validate, optimize, and integrate 3D assets.
5. Invoke `04-scene` to design the Three.js/R3F scene.
6. Invoke `05-camera-lighting` for camera, environment, lights, shadows, and rendering quality.
7. Invoke `06-interaction` for pointer, touch, hover, drag, and scroll behavior.
8. Invoke `07-animation` for animation state, timelines, transitions, and motion systems.
9. Invoke `08-ui-ux` for 2D interface, overlays, navigation, CTAs, loading, and responsive composition.
10. Invoke `09-performance` to optimize rendering, assets, memory, network, and device adaptation.
11. Invoke `10-accessibility` for keyboard support, reduced motion, semantic UI, and fallbacks.
12. Invoke `11-engineering` to implement clean, typed, reusable production code.
13. Invoke `12-testing` to validate functionality, visuals, responsiveness, and regressions.
14. Invoke `13-deployment` for build, environment variables, hosting, caching, and production verification.
15. If anything fails, route the issue to `14-debugging`, then re-run the affected module.
16. Finish with `15-quality-gate` and do not declare completion until all critical acceptance criteria pass.

## Dependency rules
- Discovery precedes architecture.
- Architecture precedes implementation.
- Assets must be understood before scene integration.
- Scene, camera/lighting, interaction, animation, and UI may be developed in parallel after architecture.
- Performance and accessibility are continuous concerns, not final-only tasks.
- Testing follows implementation and repeats after debugging.
- Deployment follows a passing quality gate.

## Output contract
Every module must return:
- Objective
- Assumptions
- Inputs
- Decisions
- Files/components affected
- Implementation details
- Risks
- Validation checklist
- Handoff notes

## Guardrails
- Never invent missing asset properties; inspect them or state assumptions.
- Never sacrifice mobile usability for desktop visual quality without explicit approval.
- Never add libraries unnecessarily.
- Prefer reusable components and isolated systems.
- Keep rendering state separate from application/business state.
- Avoid unnecessary React re-renders inside the render loop.
- Respect reduced-motion preferences.
- Treat performance budgets as acceptance criteria.
