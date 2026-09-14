import unittest

from x_video_transcript.cli import output_name, render_whisper, strip_code_fence


class CliHelpersTest(unittest.TestCase):
    def test_output_name_uses_status_id(self):
        self.assertEqual(output_name("https://x.com/example/status/12345"), "12345")

    def test_output_name_has_fallback(self):
        self.assertEqual(output_name("https://example.com/video"), "transcript")

    def test_render_whisper(self):
        result = {
            "segments": [
                {"start": 1.2, "end": 65.9, "text": " hello "},
                {"start": 66.0, "end": 67.0, "text": "  "},
            ]
        }
        self.assertEqual(render_whisper(result), "[00:01-01:05] hello\n")

    def test_strip_markdown_fence(self):
        self.assertEqual(
            strip_code_fence("```markdown\n[00:01] Hello\n```"),
            "[00:01] Hello\n",
        )


if __name__ == "__main__":
    unittest.main()
