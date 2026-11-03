# Kokoro portable GLB runtime v0.1

Use the existing Kokoro controller/configuration studio. Blender is needed only to author or re-export the model, not to display the converted character.

The runtime folder contains the GLB, sampled rig-response data and WebGL renderer. From runtime/web run `npm ci --ignore-scripts`. Node 22.12+ and a locally installed Chrome/Chromium are required. The existing Python studio retains its own dependencies.

The studio folder is the complete updated application; run python app.py from it. The optional studio_overlay targets the already delivered Controller Rig Integration v0.1. Back up the corresponding files before applying the overlay; do not replace an independently modified engine or desktop without merging its changes. In the Portable GLB tab select Node, the runtime folder, and Chrome/Chromium, enable the direct browser window, and connect the portable model. Existing commands and actual simulated motor positions drive the character. Facial controls remain manual. Save/Load/Restart preserve profiles without auto-launching executables.

This is a three-motor adapter (head, right arm, right forearm) plus blink, jaw, gaze and pupil controls. It is not a full port of every Rain rig constraint. Offline sampled control combinations approximate the source. The source .blend is separately preserved, not duplicated here. Neutral procedural material channels are baked; refraction, subsurface lighting and non-armature modifiers are not claimed identical.

The original VTK optical feedback remains separate and unchanged. No physical sensing, generalized cognition, automatic emotion or speech is claimed. Linux was tested; Windows and phones were not.

Credit: Rain Rig (CC) Blender Foundation | studio.blender.org — CC BY 4.0. Modified as Kokoro.
