"""Reproducible FFmpeg corner-mark cleanup; no Python dependencies."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


class VideoError(Exception):
    """A readable failure that must not leave a claimed output behind."""


def run(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise VideoError(f"Executable not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise VideoError(f"Command failed: {detail[-2500:]}") from exc


def probe(path: Path) -> dict:
    if not path.is_file():
        raise VideoError(f"Input file does not exist: {path}")
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration:stream=index,codec_type,codec_name,width,height,avg_frame_rate",
                "-of", "json", str(path),
            ],
            check=True, capture_output=True, text=True,
        )
        info = json.loads(result.stdout)
    except FileNotFoundError as exc:
        raise VideoError("ffprobe is required on PATH") from exc
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise VideoError(f"Could not inspect video: {path}") from exc
    if not any(s.get("codec_type") == "video" for s in info.get("streams", [])):
        raise VideoError(f"No video stream found: {path}")
    return info


def video_stream(info: dict) -> dict:
    return next(s for s in info["streams"] if s.get("codec_type") == "video")


def audio_count(info: dict) -> int:
    return sum(s.get("codec_type") == "audio" for s in info.get("streams", []))


def duration(info: dict) -> float | None:
    try:
        return float(info.get("format", {}).get("duration"))
    except (TypeError, ValueError):
        return None


def parse_rect(value: str, info: dict) -> tuple[int, int, int, int]:
    try:
        pieces = value.split(",")
        if len(pieces) != 4:
            raise ValueError("exactly four numbers expected")
        x, y, width, height = (int(n.strip()) for n in pieces)
    except ValueError as exc:
        raise VideoError("Rectangle must be X,Y,WIDTH,HEIGHT (whole pixels)") from exc
    stream = video_stream(info)
    frame_width, frame_height = int(stream["width"]), int(stream["height"])
    if width < 2 or height < 2:
        raise VideoError("Rectangle width and height must be at least two pixels")
    if x < 1 or y < 1 or x + width >= frame_width or y + height >= frame_height:
        raise VideoError(
            f"Rectangle {value} must fit within {frame_width}x{frame_height} "
            "and leave at least one pixel along every frame edge"
        )
    return x, y, width, height


def preview(args: argparse.Namespace) -> None:
    source, target = Path(args.input), Path(args.output)
    info = probe(source)
    x, y, w, h = parse_rect(args.rect, info)
    if source.resolve() == target.resolve():
        raise VideoError("Input and output paths cannot be identical")
    if target.exists() and not args.overwrite:
        raise VideoError(f"Output already exists (add --overwrite): {target}")
    if not target.parent.is_dir():
        raise VideoError(f"Output directory is missing: {target.parent}")
    if not (0 <= args.time):
        raise VideoError("--time must be nonnegative")
    filt = f"drawbox=x={x}:y={y}:w={w}:h={h}:color=yellow@0.9:t=3"
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-ss", str(args.time), "-i", str(source),
        "-vf", filt, "-frames:v", "1", str(target),
    ])
    if not target.is_file() or target.stat().st_size == 0:
        raise VideoError("Preview image was not created")
    print(f"Preview: {target}")


def process(args: argparse.Namespace) -> None:
    source, target = Path(args.input), Path(args.output)
    original = probe(source)
    x, y, w, h = parse_rect(args.rect, original)
    if source.resolve() == target.resolve():
        raise VideoError("Never overwrite the input video")
    if target.exists() and not args.overwrite:
        raise VideoError(f"Output already exists (add --overwrite): {target}")
    if not target.parent.is_dir():
        raise VideoError(f"Output directory is missing: {target.parent}")
    if target.suffix.lower() != ".mp4":
        raise VideoError("Process output must be .mp4")
    if not 0 <= args.crf <= 51:
        raise VideoError("--crf must be from 0 to 51")
    tmp = target.with_name(f".{target.stem}.{uuid.uuid4().hex}.partial.mp4")
    filt = f"delogo=x={x}:y={y}:w={w}:h={h}:show=0"
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-i", str(source), "-map", "0:v:0", "-map", "0:a?",
        "-map_metadata", "0", "-vf", filt,
        "-c:v", "libx264", "-crf", str(args.crf), "-preset", args.preset,
        "-pix_fmt", "yuv420p", "-c:a", "copy",
        "-movflags", "+faststart", str(tmp),
    ]
    try:
        run(command)
        edited = probe(tmp)
        src_stream = video_stream(original)
        out_stream = video_stream(edited)
        if (src_stream.get("width"), src_stream.get("height")) != (
            out_stream.get("width"), out_stream.get("height")
        ):
            raise VideoError("Output video dimensions changed")
        if audio_count(original) != audio_count(edited):
            raise VideoError("Output audio stream count changed")
        a, b = duration(original), duration(edited)
        if a is not None and b is not None and abs(a - b) > 0.25:
            raise VideoError(f"Duration differs significantly: {a:.3f}s vs {b:.3f}s")
        if not tmp.is_file() or tmp.stat().st_size == 0:
            raise VideoError("Output file was empty")
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()
    print(f"Edited video: {target}")
    print(f"Frame: {out_stream['width']}x{out_stream['height']}; audio streams: {audio_count(edited)}")
    print("Review the finished frames and audio; delogo interpolation may show artifacts.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gemini_icon",
        description="Edit a selected video corner without cropping the frame.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_cmd = sub.add_parser("inspect", help="Show source video metadata")
    inspect_cmd.add_argument("input")
    preview_cmd = sub.add_parser("preview", help="Draw a box on one source frame")
    preview_cmd.add_argument("input")
    preview_cmd.add_argument("--rect", required=True, help="X,Y,WIDTH,HEIGHT in pixels")
    preview_cmd.add_argument("--time", type=float, default=1.0, help="Time in seconds")
    preview_cmd.add_argument("--output", required=True, help="Image filename, e.g. preview.png")
    preview_cmd.add_argument("--overwrite", action="store_true")
    process_cmd = sub.add_parser("process", help="Interpolate selected area with FFmpeg delogo")
    process_cmd.add_argument("input")
    process_cmd.add_argument("output")
    process_cmd.add_argument("--rect", required=True, help="X,Y,WIDTH,HEIGHT in pixels")
    process_cmd.add_argument("--crf", type=int, default=18, help="H.264 quality; lower is better")
    process_cmd.add_argument("--preset", default="medium", choices=[
        "ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"
    ])
    process_cmd.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        for exe in ("ffmpeg", "ffprobe"):
            if shutil.which(exe) is None:
                raise VideoError(f"{exe} is not installed or not on PATH")
        if args.command == "inspect":
            info = probe(Path(args.input))
            v = video_stream(info)
            print(json.dumps({
                "width": v["width"], "height": v["height"],
                "fps": v.get("avg_frame_rate"), "duration_seconds": duration(info),
                "audio_stream_count": audio_count(info),
            }, indent=2))
        elif args.command == "preview":
            preview(args)
        else:
            process(args)
        return 0
    except VideoError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
