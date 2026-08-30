---
name: 3d-engineering
description: Implement clean, typed, reusable production code for 3D web applications.
---

# Engineering

## Code quality
- TypeScript strictness where practical
- explicit interfaces
- reusable components
- small modules
- clear naming
- no duplicated scene logic
- no unnecessary dependencies

## React rules
- avoid state updates inside high-frequency frame loops
- memoize only when profiling or architecture justifies it
- use refs for mutable render-loop values
- keep side effects controlled
- clean up event listeners and animation resources

## Error handling
Implement:
- loading boundaries
- model-load errors
- WebGL fallback
- runtime-safe defaults

## Deliverables
Return complete files when implementation is requested, not pseudo-code.
