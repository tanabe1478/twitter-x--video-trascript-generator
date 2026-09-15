import unittest

from x_video_transcript.cli import (
    ParakeetTranscriber,
    Segment,
    Transcript,
    WhisperTranscriber,
    build_transcriber,
    output_name,
    render_transcript,
)


class CliHelpersTest(unittest.TestCase):
    def test_output_name_uses_status_id(self):
        self.assertEqual(output_name("https://x.com/example/status/12345"), "12345")

    def test_output_name_has_fallback(self):
        self.assertEqual(output_name("https://example.com/video"), "transcript")

    def test_render_transcript(self):
        transcript = Transcript(
            engine="parakeet",
            model="mlx-community/parakeet-tdt-0.6b-v2",
            segments=[
                Segment(1.2, 65.9, " hello "),
                Segment(66.0, 67.0, "  "),
            ],
            raw={},
        )
        self.assertEqual(render_transcript(transcript), "[00:01-01:05] hello\n")

    def test_build_transcriber_defaults_to_parakeet(self):
        transcriber = build_transcriber("parakeet")
        self.assertIsInstance(transcriber, ParakeetTranscriber)
        self.assertEqual(transcriber.model, "mlx-community/parakeet-tdt-0.6b-v2")

    def test_build_transcriber_whisper(self):
        transcriber = build_transcriber("whisper", whisper_model="custom/model")
        self.assertIsInstance(transcriber, WhisperTranscriber)
        self.assertEqual(transcriber.model, "custom/model")

    def test_build_transcriber_rejects_unknown(self):
        with self.assertRaises(ValueError):
            build_transcriber("other")


if __name__ == "__main__":
    unittest.main()
