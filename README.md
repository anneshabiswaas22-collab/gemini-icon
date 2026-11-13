# Gemini Corner-Mark Video Editor

A small, reproducible **local video-editing project** for cleaning a user-selected region (initially the lower-right corner) of a video while keeping the original frame dimensions and copying the source audio when possible.

> **Status (2026-11-13):** Developer-ready MVP plus documentation. The historical source video and any previously exported result are **not in this repository**. The MVP uses FFmpeg's \`delogo\` spatial interpolation, **not** the original project's undocumented transparency-reversal technique. No claim is made that the two methods produce identical results.

## The goal

The first request (6 November 2026) was to remove the small Gemini icon at the **bottom-right** of a user-supplied video (\`gemini_generated_video_33dccd44.mp4\`). Keep the complete frame, existing audio, duration, motion, and visual quality as closely as practical. Avoid cropping the picture. The project now aims to make that editing task reproducible, testable, and easy for contributors to improve.

**Scope:** edit user-owned or otherwise authorized material. Keep original input files outside the repository. Be transparent about edits and do not imply that edited content originated from a different source.

## Quick start

Requirements: Python 3.10+, **FFmpeg** and **ffprobe** on PATH. No third-party Python packages are required.

\`\`\`bash
git clone https://github.com/anneshabiswaas22-collab/gemini-icon.git
cd gemini-icon
python -m pip install -e .
python -m gemini_icon inspect path/to/input.mp4
python -m gemini_icon preview path/to/input.mp4 --rect 1150,640,110,65 --time 2 --output preview.png
python -m gemini_icon process path/to/input.mp4 path/to/cleaned.mp4 --rect 1150,640,110,65
\`\`\`

The rectangle is **an illustration, not an exact mask for the original video**. Use \`preview\` to draw and inspect the actual region on your clip. \`--rect\` means \`X,Y,WIDTH,HEIGHT\` in source pixels, measured from the top-left. The current FFmpeg filter requires the selected box to leave at least one source pixel at each outer edge.

\`\`\`bash
python -m gemini_icon --help
python -m gemini_icon process --help
python -m unittest discover -s tests -v
\`\`\`

## How the MVP works

1. Inspect the video with \`ffprobe\`, checking video dimensions and audio streams.
2. Preview the rectangular region using an outlined box (does not edit video).
3. Apply FFmpeg's \`delogo\` filter to **interpolate the selected region**. The rest of the image stays in frame. Video is encoded to H.264 with configurable CRF/preset.
4. **Stream-copy audio** without audio re-encoding. The result is validated for dimensions, audio stream count, and approximate duration.
5. Write to a temporary file and move it to the destination only after successful validation.

Results in areas with moving objects or complex backgrounds can show interpolation artifacts. No algorithm can guarantee recovery of original pixels hidden beneath a logo. Always review multiple frames and listen to the audio before publishing.

## Files

| Path | Why it exists |
| --- | --- |
| \`src/gemini_icon/__main__.py\` | Working inspect/preview/process CLI |
| \`tests/test_cli.py\` | Synthetic-video integration and validation tests |
| \`docs/PROJECT_CONTEXT.md\` | Recovered conversation brief and provenance limits |
| \`docs/DEVELOPER_HANDOFF.md\` | Architecture, setup, QA, and contributor instructions |
| \`docs/ROADMAP.md\` | Prioritized issues and definition of done |
| \`CONTRIBUTING.md\` | Contribution workflow |
| \`.github/workflows/ci.yml\` | CI tests on Python 3.10–3.12 |

## What is not included

- The original 20-second uploaded MP4, its exact logo mask, and the earlier edited export (not retrievable from the accessible project records here).
- An automated Gemini-icon detector, transparency reconstruction, or optical-flow/video-inpainting model.
- A graphical UI or hosted editing service.
- A blanket assertion that a logo or provenance disclosure can safely or legally be removed from every source.

See [PROJECT_CONTEXT](docs/PROJECT_CONTEXT.md) before changing scope, and [ROADMAP](docs/ROADMAP.md) for the next tasks.
