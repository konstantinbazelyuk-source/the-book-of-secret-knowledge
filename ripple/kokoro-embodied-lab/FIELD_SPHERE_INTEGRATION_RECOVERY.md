# Kokoro Embodiment — Field Sphere Integration Recovery Log
Date: 2026-10-21
Status: Source recovery required; engineering integration not yet verified.
Branch: research/kokoro-embodied-motion-v1 (preserve master)

## User-confirmed direction
The field sphere in the Ripple Fair category is a candidate spatial perception substrate for Kokoro. The user's proposed advance is to combine its internal digital-space field representation with Kokoro's expressive embodiment components, not replace the field sphere with generic animation.

### Intended chain
Field sphere observations and existing mathematics -> coordinate/time registration -> expressive motion state -> skinned bust deformation and Gaussian spatial appearance -> rendered expression -> optional feedback into the field.

The motion system must be capable of expressing information represented in the sphere through head, eyes, face, jaw, neck and shoulders. Retain separate measurable perception, control, deformation, and appearance operations with a common coordinate and time contract.

## Previously agreed technologies
- Viggle-style reference motion extraction and retargeting (do not presume proprietary Viggle source access).
- XYZ point geometry and point-cloud measurements.
- 3D Gaussian splatting/appearance representation.
- Skinned surface geometry with non-rigid expression deformation.
- Temporal/spacetime motion mathematics.
- Ripple Motor and vehicle-control feedback.
- Ripple Genetic Weights.
- Existing Lumina character assets where source compatibility is established.

### Mathematical expression for retargeting
p_i(t) = sum_j w_ij T_j(t) p_i(0) + delta_p_i(t)

This expression is an agreed working reference, NOT a recovered field-sphere equation. The original field-sphere mathematical formula remains to be retrieved.

## Existing executable baseline
- bust.mjs / bust.html: procedural 3D Gaussian primitive renderer and animated facial controls; not yet trained 3DGS or a complete skinned mesh.
- bust.test.mjs: deformation and projection tests.
- xyz.mjs, control.mjs: older reference implementations. Preserve them; do not substitute them for the revised system.

## Recovery tasks
1. Locate original 'Ripple Fair' field-sphere files and exact mathematical formulas; record archive/file path and version.
2. Inspect the field's actual data representation, coordinate system, units, temporal updates, and perception outputs.
3. Write an adapter that converts verified field outputs to timestamped motion parameters, without inventing unobserved field capabilities.
4. Retarget motion to a genuine deformable bust surface and attached Gaussian primitives; maintain one shared geometry.
5. Verify causality: changing field input changes corresponding measured 3D deformation, and the motion is continuous and bounded.
6. Connect video-derived reference motion and existing Ripple control components only after interfaces are verified.

## Evidence and constraints
Library archive inventory and project catalog were searched on 2026-10-21. They contain numerous Ripple/Kokoro archive references, but the exact field-sphere source and mathematics have NOT yet been located or read. GitHub code search for the phrase 'field sphere' returned no matching indexed results; this does not prove absence from the repository. Do not infer the formula, field data structures, or implemented perception capability from the user's description alone.

No conceptual-only substitute, vestigial module, fabricated benchmark, or unverified functionality should be presented as an implemented field-sphere integration.
