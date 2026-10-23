# Viggle / PINOC technology adaptation study — ecosystem-wide
Date: 2026-10-23
Scope: Ripple, Kokoro, robotics, media/video, creative tools, game systems, spatial reconstruction, and future applications. NOT Kokoro-only.

## Verified public interfaces and capabilities
1. PINOC/JST-2 video-to-motion and text-to-motion: export GLB/FBX motion; Mixamo, MetaHuman, MetaHuman Body rigs. PINOC documents a 65-bone Mixamo-named skeleton.
2. Image-to-3D character: rigged .vsplat; this is not an ordinary skinned GLB/FBX mesh. Needs compatible Viggle Splat Engine.
3. Scene generation: .spz Gaussian splats, panoramic/posed views and scene reconstruction; camera poses represented as 4x4 matrices.
4. JST-1 Mix/Remix: character + driving motion -> video; reusable character/motion IDs and alpha-mask output.
5. Viggle-Animate: publicly available model resources, with third-party ComfyUI workflows. Large weights and memory costs; check upstream licensing before reuse.
6. H3 video with audio and Viggle Image are media workflows separate from motion extraction.
7. PINOC MCP endpoint documented as https://pinoc.mcp.viggle.ai/mcp with read-only vs credit-spending write permissions.
8. Viggle API offers asynchronous jobs, export links that expire, and an introductory developer credit offer; do not presume account activation.

## Primary official references
- https://viggle.ai/developers
- https://viggle.ai/pinoc/ai-motion-capture/
- https://viggle.ai/pinoc/mcp
- https://viggle.ai/pinoc

## Public model implementation references
- https://huggingface.co/Viggle/Viggle-Animate
- https://github.com/Saganaki22/ComfyUI-Viggle-Animate-H3
- https://github.com/aireet/viggle-animate-workflow

## Transferable engineering patterns
- Versioned character and motion assets with reusable IDs, metadata and provenance.
- Portable timestamped skeletal tracks; explicit joint hierarchy, units, handedness, rest poses.
- Hierarchical bone-length-preserving retargeting with root motion, contact handling and interpolation.
- Character representations as skinned meshes OR specialized Gaussian splat assets; adapters rather than pretending formats are interchangeable.
- Separate spatial scene assets from character motion and appearance.
- Motion quality metrics: endpoint error, bone-length drift, contact slip, temporal jerk, reconstruction error.
- Async job orchestration with retries, idempotency where supported, caching, cost controls, signed URL renewal.
- Multi-target export to video, GLB/FBX, or spatial assets based on consumer requirements.

## Completed local adaptation and verification
Independent Python prototype saved in downloadable bundle 'viggle_motion_research_bundle.zip':
- motion_core.py (prior): pose interpolation, basic retarget, ground correction.
- motion_pipeline.py (new): versioned ripple.motion.v1 JSON schema validation; timestamp interpolation; hierarchical length-preserving positional retargeting; JSON load/save.
- test_motion_core.py and test_motion_pipeline.py: 10 tests passed locally 2026-10-23.
This is NOT a Viggle model, motion extractor, FBX/GLB parser, or trained 3D Gaussian splatting engine. No real video-to-motion inference or asset compatibility test has yet been performed.

## Next implementation stages
1. Build actual GLB animation importer/exporter with verified joint and quaternion transforms, preserve provenance.
2. Test with legally usable PINOC exports and public sample clips; record coordinate conventions.
3. Extend retargeting to joint rotations, IK, constraints, contact preservation and temporal quality metrics.
4. Add .spz/.vsplat handling via compatible renderers, respecting format and licensing constraints.
5. Connect field-sphere/vision, Kokoro bust, Ripple Motor, media workflows, and independent game/robotics consumers via common motion schema.
6. Integrate Viggle API or MCP only with explicit connected credentials and credit-aware user authorization.

Preserve original repo master and all locked predecessors; conduct research in isolated branch.
