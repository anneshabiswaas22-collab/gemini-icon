# Project context and recovered history

## Origin and user intent

The project name is **Remove Gemini Icon**. The first user request, dated **6 November 2026**, was to edit the uploaded video `gemini_generated_video_33dccd44.mp4` and remove the Gemini symbol in the **lower-right corner**. The next user message asked what had been done and requested an explanation.

The user's desired outcome was a **usable edited MP4**, not just written directions. Quality constraints from the prior exchange:
- Remove the visible lower-right icon without obvious editing artifacts.
- Preserve full picture dimensions/framing (prefer no cropping).
- Preserve original audio and video timing where possible.
- Produce a video that can be reviewed and shared.

## Historical report — not an independent verification

A prior assistant reported it had produced a cleaned result. That report described:
- **1280 × 720**, **20 seconds**, **480 frames**;
- re-encoded picture, copied audio;
- a Python/FFmpeg technique characterized as reversing partial transparency followed by edge smoothing;
- checking multiple scenes.

However, the retrievable project history **does not include** that script, the actual pixel mask, the produced binary, its attachment link, checksum, or independent test evidence. These claims are recorded as **historical assistant statements**, not as verified deliverables. No assertion is made that the original output is stored on GitHub.

## Current independently verifiable baseline

As of **13 November 2026**, this repository was inspected and initially contained only `README.md` with `# gemini-icon`. This handoff introduces an independently implemented, generic FFmpeg `delogo` CLI, synthetic-video tests, docs, and CI. It does **not** reconstruct or reproduce the undocumented original transparency method.

## Boundaries

- Do not include private chat transcripts or media without explicit authorization.
- Do not commit the source MP4 or the edited output by default. Video assets may be too large and rights-sensitive for an ordinary public Git repository.
- `delogo` estimates missing pixels using nearby colors. It cannot recover arbitrary original pixels obscured by an opaque mark.
- Maintain disclosure/provenance where it matters; work only on videos the user can lawfully modify.
- This is a focused media-processing repository, **not** the user's separate full-featured AI video-editor or animated-movie project.

## Open questions for implementation (not required to start)

The original source clip/edited export need to be supplied again for **source-specific** regression tests. The right-bottom coordinates, logo size, translucency, animation, and scene movement remain unknown in the accessible records. A reviewer should compare the historical export, if supplied, with the new pipeline and choose the best reconstruction method based on visual evidence.
