---
name: 3d-architecture
description: Design the generalized architecture for interactive 3D web applications.
---

# Architecture

## Purpose
Create a maintainable architecture separating UI, 3D rendering, interaction, animation, assets, and application state.

## Recommended structure
Use a structure similar to:

src/
  app/
  components/
    ui/
    3d/
      Scene/
      Camera/
      Lighting/
      Environment/
      Models/
      Effects/
  hooks/
  lib/
    3d/
    assets/
    performance/
  state/
  types/

public/
  models/
  textures/
  animations/
  hdri/

## Boundaries
- UI owns semantic interface.
- R3F owns 3D rendering.
- Hooks own reusable interaction behavior.
- State owns persistent application state.
- Render-loop state should remain local to the 3D system when possible.
- Asset utilities own loading and preprocessing logic.

## Architecture decisions
For each major decision document:
- chosen approach
- alternatives considered
- reason
- tradeoff

## Handoff
Provide component boundaries and dependency graph to implementation modules.
