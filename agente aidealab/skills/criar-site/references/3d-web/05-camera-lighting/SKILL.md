---
name: 3d-camera-lighting
description: Design cinematic cameras, lighting, environments, shadows, and rendering quality for web 3D.
---

# Camera and Lighting

## Camera
Support:
- perspective camera
- responsive framing
- smooth target tracking
- cinematic transitions
- safe mobile composition

## Lighting
Use a deliberate hierarchy:
- key light
- fill light
- rim/accent light
- environment lighting

Choose physically plausible intensity and color relationships.

## Shadows
Use the least expensive shadow technique that achieves the visual goal.

## Quality tiers
Define at least:
- high
- medium
- low/mobile

Adapt:
- shadow map size
- DPR
- post-processing
- environment complexity
- effect density

## Validation
Check model readability, silhouette, highlights, shadows, clipping, and mobile framing.
