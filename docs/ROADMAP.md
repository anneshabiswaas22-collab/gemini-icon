# Roadmap and prioritized work

**P0 — Reproducible foundation (this handoff)**

- [x] Record the real user goal and provenance limitations.
- [x] Provide command-line inspect, preview, process commands.
- [x] Avoid overwriting user input and copy audio when supported.
- [x] Validate output dimensions, audio count, and duration.
- [x] Synthetic integration tests + GitHub Actions workflow.
- [ ] Run the actual historical 20-second video through the pipeline (source binary unavailable here).
- [ ] Manually review the original and edited files side by side.
- [ ] Confirm licensing with the repository owner before treating this repository as open source.

**P1 — Quality and correctness**

- [ ] Add video test fixtures with scrolling textures, moving objects, and dark/bright transitions.
- [ ] Compare FFmpeg \`delogo\`, OpenCV spatial inpainting, and temporal background reconstruction.
- [ ] Add optional corner-border handling for masks touching image edges.
- [ ] Verify VFR inputs, color management, HDR/10-bit input, rotated-video metadata, and multiple audio tracks.
- [ ] Provide objective checks (frame count/fps, audio packet/codec comparison, VMAF/SSIM outside the edit region).
- [ ] Save run metadata (command/options, FFmpeg build, probe results) as JSON.
- [ ] Establish a visually reviewed before/after image gallery using authorized fixtures.

**P2 — Usability and automation**

- [ ] Interactive drag-to-select ROI and playback preview.
- [ ] Automatic candidate-logo localization, with confidence scores and manual override.
- [ ] Track drifting/animated marks across scenes with a time-dependent mask.
- [ ] Batch input directory processing and per-file error reports.
- [ ] Windows PowerShell, macOS, and Linux package/install documentation.
- [ ] Progress/cancel control and friendly error reporting.

**P3 — Advanced restoration**

- [ ] Investigate an optional known-alpha compositing reversal for translucent logos when the alpha and actual graphic are **known**. Do not imply exact recovery without evidence.
- [ ] Add temporally consistent video inpainting with optical flow/video-aware models.
- [ ] Benchmark quality, speed, CPU/GPU memory, and edge-artifact rates.
- [ ] Optional GUI/web interface with proper media privacy controls.
- [ ] Establish a release pipeline and versioned sample outputs.

## Current definition of done

A task is done only when code is merged, automated tests pass, limitations are documented, and source-specific quality claims have been verified on real output. A prior chat's “done” message is not a substitute for a binary artifact or independent inspection.
