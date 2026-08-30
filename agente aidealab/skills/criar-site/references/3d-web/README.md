# Claude 3D Web Skills Framework

A generalized modular skill framework for Claude Code/Claude-style agents that build interactive 3D web experiences.

## Structure

- `SKILL.md` — master orchestrator
- `01-discovery/SKILL.md` — requirements and acceptance criteria
- `02-architecture/SKILL.md` — architecture
- `03-assets/SKILL.md` — GLB/GLTF/assets
- `04-scene/SKILL.md` — R3F/Three.js scene
- `05-camera-lighting/SKILL.md` — camera, lighting, shadows
- `06-interaction/SKILL.md` — mouse, touch, drag, scroll
- `07-animation/SKILL.md` — animation systems
- `08-ui-ux/SKILL.md` — 2D UI around 3D
- `09-performance/SKILL.md` — optimization
- `10-accessibility/SKILL.md` — accessibility/fallbacks
- `11-engineering/SKILL.md` — production implementation
- `12-testing/SKILL.md` — testing/validation
- `13-deployment/SKILL.md` — deployment
- `14-debugging/SKILL.md` — diagnosis and repair
- `15-quality-gate/SKILL.md` — final production gate

## Orchestration

The master skill determines which modules are needed and runs them in dependency order. It can re-route failed work to debugging and then back through testing and the quality gate.

## Intended use

Drop the framework into a skills directory and adapt the orchestration mechanism to the agent environment being used.
