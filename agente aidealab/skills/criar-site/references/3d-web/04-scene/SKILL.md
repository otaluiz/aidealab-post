---
name: 3d-scene
description: Build reusable Three.js and React Three Fiber scene systems.
---

# Scene System

## Purpose
Create the 3D world independently from page-specific business logic.

## Responsibilities
- Canvas configuration
- Scene composition
- object hierarchy
- model placement
- materials
- environment
- effects
- render settings
- suspense/loading boundaries

## Principles
- Keep scene components small.
- Prefer declarative R3F components.
- Use refs for high-frequency render-loop mutations.
- Avoid expensive allocations inside `useFrame`.
- Dispose resources when dynamically created.

## Reusable primitives
Create reusable systems for:
- Model
- Group
- Ground
- Background
- Environment
- ContactShadow
- ParticleField
- PostProcessing

## Handoff
Expose clear props rather than hard-coding a single project.
