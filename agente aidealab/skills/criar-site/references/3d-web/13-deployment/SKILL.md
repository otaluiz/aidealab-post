---
name: 3d-deployment
description: Prepare, deploy, and verify production 3D web applications.
---

# Deployment

## Pre-deploy
Verify:
- production build
- environment variables
- asset paths
- caching
- compression
- CDN behavior
- HTTPS
- route handling
- error monitoring

## Static assets
Ensure GLB, textures, HDRIs, and other assets are served with appropriate cache headers.

## Deployment targets
Adapt to platforms such as:
- Vercel
- Netlify
- Cloudflare
- traditional Node hosting
- static hosting

## Post-deploy
Verify:
- desktop
- mobile
- slow network
- model loading
- interaction
- console errors
- WebGL fallback
