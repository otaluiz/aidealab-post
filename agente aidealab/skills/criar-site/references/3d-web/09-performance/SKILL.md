---
name: 3d-performance
description: Optimize interactive 3D web applications for loading time, FPS, memory, GPU cost, and mobile devices.
---

# Performance

## Measure first
Inspect:
- initial bundle
- model download size
- texture size
- draw calls
- triangles
- GPU memory pressure
- frame time
- React render frequency
- network waterfall

## Optimization toolbox
- lazy loading
- code splitting
- asset preloading at the right moment
- GLB compression
- texture compression
- instancing
- LOD
- frustum culling
- lower DPR
- simplified shadows
- reduced post-processing
- device capability tiers

## Rules
Never optimize by guesswork when profiling data is available.

## Performance budget
Define project-specific budgets. At minimum track:
- initial 3D payload
- peak draw calls
- target frame rate
- mobile fallback threshold

## Handoff
Return measurable before/after results where tooling allows.
