---
name: 3d-accessibility
description: Make 3D web experiences accessible through semantic UI, keyboard controls, reduced motion, and graceful fallbacks.
---

# Accessibility

## Requirements
- semantic HTML for controls
- keyboard navigation
- visible focus
- adequate contrast
- descriptive labels
- no functionality available only through hover
- `prefers-reduced-motion` support
- graceful degradation if WebGL fails
- readable content independent of the 3D scene

## Reduced motion
When enabled:
- remove unnecessary camera movement
- reduce floating/parallax
- disable decorative animation
- preserve functional transitions where appropriate

## WebGL failure
Provide a useful 2D fallback instead of a blank canvas.
