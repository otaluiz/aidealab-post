---
name: 3d-animation
description: Design and implement reusable animation systems for models, scenes, UI transitions, and scroll timelines.
---

# Animation

## Types
Support:
- GLTF animation clips
- procedural animation
- spring-like motion
- timeline animation
- scroll-linked animation
- state transitions
- entrance/exit animation

## Principles
- Separate animation state from business state.
- Use AnimationMixer/actions for imported clips.
- Use frame-loop updates for continuous 3D motion.
- Avoid unnecessary animation work when objects are not visible.
- Respect `prefers-reduced-motion`.

## Animation states
Model animation should be expressible as states such as:
idle, hover, active, transition, disabled

## Validation
Ensure transitions are deterministic and do not accumulate duplicate mixers/listeners.
