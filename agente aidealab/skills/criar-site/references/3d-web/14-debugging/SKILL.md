---
name: 3d-debugging
description: Diagnose and fix failures in Three.js, React Three Fiber, WebGL, asset loading, animation, interaction, and performance.
---

# Debugging

## Triage order
1. Reproduce
2. Capture exact error
3. Identify affected layer
4. Reduce to smallest failing case
5. Form a hypothesis
6. Change one variable
7. Verify
8. Add regression protection

## Common categories
- GLB path/loading failure
- unsupported texture format
- material/rendering issue
- camera clipping
- incorrect scale/origin
- animation mixer problems
- event conflicts
- React render loops
- WebGL context loss
- memory leaks
- mobile GPU limitations

## Rule
Do not hide errors with broad try/catch blocks. Fix root causes or provide explicit fallback behavior.
