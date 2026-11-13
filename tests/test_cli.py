"""Integration tests using generated clips: no user media is checked in."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


FFMPEG_READY = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def command(*parts):
    return subprocess.run(
        [sys.executable, "-m", "gemini_icon", *map(str, parts)],
        text=True, capture_output=True,
    )


@unittest.skipUnless(FFMPEG_READY, "Requires ffmpeg and ffprobe")
class VideoCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "color=c=blue:s=320x180:r=12",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
            "-t", "1", "-c:v", "mpeg4", "-c:a", "aac",
            "-shortest", str(self.source),
        ], check=True, capture_output=True)

    def test_inspect(self):
        proc = command("inspect", self.source)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual((data["width"], data["height"]), (320, 180))
        self.assertEqual(data["audio_stream_count"], 1)

    def test_preview(self):
        destination = self.root / "preview.png"
        proc = command(
            "preview", self.source, "--rect", "250,135,55,30",
            "--time", "0.1", "--output", destination,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertGreater(destination.stat().st_size, 0)

    def test_process_preserves_dimensions_audio_and_duration(self):
        destination = self.root / "clean.mp4"
        proc = command(
            "process", self.source, destination, "--rect", "250,135,55,30",
            "--preset", "ultrafast",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        inspected = command("inspect", destination)
        data = json.loads(inspected.stdout)
        self.assertEqual((data["width"], data["height"]), (320, 180))
        self.assertEqual(data["audio_stream_count"], 1)
        self.assertAlmostEqual(data["duration_seconds"], 1.0, delta=0.25)

    def test_reject_invalid_box_and_avoid_overwriting_source(self):
        out = self.root / "clean.mp4"
        invalid = command("process", self.source, out, "--rect", "300,160,100,30")
        self.assertNotEqual(invalid.returncode, 0)
        self.assertFalse(out.exists())
        same = command("process", self.source, self.source, "--rect", "250,135,55,30")
        self.assertNotEqual(same.returncode, 0)

    def test_reject_existing_output_unless_explicitly_overwriting(self):
        destination = self.root / "clean.mp4"
        destination.write_text("do not clobber")
        proc = command("process", self.source, destination, "--rect", "250,135,55,30")
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(destination.read_text(), "do not clobber")


if __name__ == "__main__":
    unittest.main()
