---
name: 3d-assets
description: Inspect, validate, optimize, and integrate GLTF/GLB models, textures, HDRIs, and animation assets.
---

# 3D Assets

## Purpose
Make 3D assets production-ready before scene integration.

## Inspect
For every model determine:
- file format
- triangle/vertex counts
- meshes
- materials
- textures
- animation clips
- skeletons
- node hierarchy
- dimensions
- origin/pivot
- scale
- compression status

## Optimization
Prefer:
- GLB over unnecessarily fragmented asset sets
- Draco or Meshopt when appropriate
- KTX2/Basis textures when supported
- texture resizing based on device needs
- removal of unused materials, nodes, and animations
- instancing for repeated geometry

## Integration
Expose models through reusable components:
- ModelLoader
- Model
- AnimatedModel
- AssetErrorBoundary
- preload helpers

## Guardrails
Do not destroy source assets. Keep an optimized derivative when preprocessing is required.
