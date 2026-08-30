---
name: 3d-testing
description: Validate 3D web applications across functionality, rendering, responsiveness, accessibility, and build integrity.
---

# Testing

## Test layers
1. Type checking
2. Linting
3. Unit tests for pure logic
4. Component tests where practical
5. Browser integration tests
6. Responsive tests
7. Accessibility checks
8. Visual regression where available
9. Performance profiling

## 3D-specific checks
- model loads
- animations play
- interactions work
- camera does not clip
- scene does not break after route changes
- resources are cleaned up
- fallback works when WebGL is unavailable

## Regression rule
Any optimization or visual change must be checked against existing acceptance criteria.
