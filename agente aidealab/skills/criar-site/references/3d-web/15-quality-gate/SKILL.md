---
name: 3d-quality-gate
description: Perform the final production-readiness review for an interactive 3D web application.
---

# Quality Gate

## Required checks

### Functional
- [ ] Main user goal works
- [ ] 3D assets load
- [ ] Interactions work
- [ ] Animations transition correctly
- [ ] Navigation works
- [ ] Loading/error states work

### Visual
- [ ] Camera framing is intentional
- [ ] Lighting is coherent
- [ ] Materials render correctly
- [ ] No obvious clipping/z-fighting
- [ ] Responsive composition is acceptable

### Performance
- [ ] Initial payload is acceptable
- [ ] Models/textures are optimized
- [ ] Mobile quality tier exists
- [ ] No obvious memory leak
- [ ] Frame rate is acceptable on target devices

### Accessibility
- [ ] Keyboard navigation
- [ ] Focus states
- [ ] Reduced motion
- [ ] Semantic controls
- [ ] WebGL fallback

### Engineering
- [ ] Type checking passes
- [ ] Build passes
- [ ] No critical console errors
- [ ] No unnecessary dependencies
- [ ] Components are reusable

## Final decision
Return one of:
- PASS
- PASS WITH WARNINGS
- FAIL

A FAIL must include the blocking issues and route them back to the appropriate skill.
