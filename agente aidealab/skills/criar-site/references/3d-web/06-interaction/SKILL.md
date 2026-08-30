---
name: 3d-interaction
description: Implement reusable mouse, touch, hover, drag, scroll, and gesture interactions for 3D web experiences.
---

# Interaction

## Supported patterns
- pointer parallax
- hover response
- click/tap
- drag rotation
- orbit
- scroll-driven camera
- scroll-driven object transformation
- touch gestures

## Principles
- Interactions must be smooth and bounded.
- Never depend exclusively on hover.
- Touch must have an equivalent interaction path.
- Use interpolation rather than abrupt transforms.
- Avoid event handlers that trigger excessive React renders.

## Accessibility
Every important 3D interaction must have a 2D or semantic alternative when it affects functionality.

## Handoff
Return reusable hooks/components such as:
- usePointerParallax
- useScrollProgress
- useDragRotation
- useSmoothTransform
