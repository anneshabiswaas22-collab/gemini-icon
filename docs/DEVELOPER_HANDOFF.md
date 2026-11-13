# Developer handoff

Start here if you have not read the ChatGPT conversation.

## Setup

1. Install Python 3.10 or later, FFmpeg (including `ffprobe`), and Git.
2. Clone this repository and run `python -m pip install -e .`.
3. Run `python -m unittest discover -s tests -v`.
4. Try `python -m gemini_icon inspect sample.mp4` on a clip you own.
5. Use `preview` to draw a region; inspect frames from the beginning, middle, end.
6. Run `process` and compare dimensions, length, audio, and visible artifacts.

The tests synthesize their own 320×180 MP4 and sine-wave audio; no AI-generated or proprietary video is needed for CI.

## Architecture

```text
source MP4 (local, not committed)
    |
    +--> ffprobe --> width, height, streams, duration
    |
    +--> preview --> FFmpeg drawbox --> PNG showing ROI
    |
    +--> process --> FFmpeg delogo --> H.264 picture
                                     + stream-copied audio
                                          |
                                       temp MP4
                                          |
                             ffprobe validation + atomic replace
                                          |
                                     cleaned MP4
```

The ROI (`--rect X,Y,W,H`) uses pixels, top-left origin. It is explicit, not detected automatically. We intentionally reject rectangles touching the frame boundary because the current FFmpeg `delogo` path assumes nearby edge pixels. Do not falsely label a processing result “perfect cleanup”; inspect the output.

## Engineering choices

- The MVP has **no Python runtime dependencies**, only FFmpeg/ffprobe.
- Use `subprocess.run` with argument arrays (no shell interpolation).
- Never overwrite the input; overwriting an existing result requires `--overwrite`.
- Preserve full frame dimensions. The H.264 video necessarily involves re-encoding and may have some generational loss; audio is copied as encoded packets when possible.
- Check for exact stream count/dimensions and approximate duration before accepting a result.
- MP4 is the only processing output currently supported. Non-MP4 containers/unsupported source audio may require remuxing/transcoding in a later change.
- `delogo` is an initial baseline, not a smart video-inpainting model. For complex backgrounds, document its limitations and benchmark alternatives.

## Acceptance tests before closing an issue

- Audio is present when source had audio and plays correctly.
- Output has same width/height and roughly same duration as source; report any intentional frame-rate changes.
- No unintentional crop, letterbox, black bars, frame flashes, or freezes.
- Icon is gone in representative still, moving, light, and dark scenes.
- No obvious rectangular patch or background smearing.
- Reproducible command and version information are recorded in the PR.
- Tests pass on CI and a contributor manually reviews a real, authorized sample.

## Contributor workflow

Create a short issue with expected behavior and sample metadata. Branch from `main`, make focused changes, add a regression test, and submit a PR. Do not post copyrighted video or private chat content in public issues. For visual regression use synthetic samples or carefully authorized short fixtures.

See `docs/ROADMAP.md` for priorities and `CONTRIBUTING.md` for pull-request conventions.
