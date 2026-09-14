from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"


def timestamp(seconds: float) -> str:
    value = max(0, int(seconds))
    return f"{value // 60:02d}:{value % 60:02d}"


def output_name(url: str) -> str:
    match = re.search(r"/status/(\d+)", url)
    return match.group(1) if match else "transcript"


def find_source(output_dir: Path) -> Path | None:
    candidates = [
        path
        for path in output_dir.glob("source.*")
        if path.suffix not in {".part", ".ytdl", ".json"}
    ]
    return sorted(candidates)[0] if candidates else None


def extract_with_reply_fallback(
    ydl: Any, url: str, max_parents: int = 5
) -> tuple[dict[str, Any], str]:
    import yt_dlp
    from yt_dlp.extractor.twitter import TwitterIE

    current_url = url
    visited: set[str] = set()
    for _ in range(max_parents + 1):
        try:
            return ydl.extract_info(current_url, download=True), current_url
        except yt_dlp.utils.DownloadError as error:
            if "No video could be found in this tweet" not in str(error):
                raise

            tweet_id = output_name(current_url)
            if tweet_id == "transcript" or tweet_id in visited:
                raise
            visited.add(tweet_id)

            status = TwitterIE(ydl)._extract_status(tweet_id)
            parent_id = status.get("in_reply_to_status_id_str")
            if not parent_id:
                raise
            parent_user = status.get("in_reply_to_screen_name") or "i"
            current_url = f"https://x.com/{parent_user}/status/{parent_id}"
            print(
                f"No attached video; trying parent post: {current_url}",
                flush=True,
            )

    raise RuntimeError(f"No video found after following {max_parents} parent posts")


def download(url: str, output_dir: Path, verbose: bool) -> tuple[Path, dict[str, Any]]:
    import yt_dlp

    options = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "source.%(ext)s"),
        "noplaylist": True,
        "quiet": not verbose,
        "no_warnings": not verbose,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info, resolved_url = extract_with_reply_fallback(ydl, url)

    source = find_source(output_dir)
    if source is None:
        raise RuntimeError("yt-dlp completed but the downloaded audio was not found")

    metadata = {
        "id": info.get("id"),
        "title": info.get("title"),
        "description": info.get("description"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "upload_date": info.get("upload_date"),
        "requested_url": url,
        "resolved_url": resolved_url,
        "webpage_url": info.get("webpage_url") or resolved_url,
    }
    return source, metadata


def configure_ffmpeg() -> str:
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    executable_dir = Path(sys.executable).parent
    link = executable_dir / "ffmpeg"
    if not link.exists():
        try:
            if link.is_symlink():
                link.unlink()
            link.symlink_to(ffmpeg)
        except OSError as error:
            raise RuntimeError(
                f"Could not expose the bundled ffmpeg at {link}: {error}"
            ) from error
    os.environ["PATH"] = f"{executable_dir}{os.pathsep}{os.environ.get('PATH', '')}"
    return ffmpeg


def normalize_audio(source: Path, destination: Path) -> None:
    ffmpeg = configure_ffmpeg()
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(destination),
    ]
    subprocess.run(command, check=True)


def whisper_prompt(metadata: dict[str, Any], context: str | None) -> str:
    parts = [
        "Accurate verbatim transcript. Preserve technical terms, product names, "
        "profanity, and false starts. Do not summarize."
    ]
    for key in ("title", "description", "uploader"):
        value = metadata.get(key)
        if value:
            parts.append(f"{key}: {value}")
    if context:
        parts.append(f"Additional context: {context}")
    return "\n".join(parts)[:4000]


def run_whisper(
    audio: Path,
    model: str,
    metadata: dict[str, Any],
    context: str | None,
    verbose: bool,
) -> dict[str, Any]:
    configure_ffmpeg()
    import mlx_whisper

    return mlx_whisper.transcribe(
        str(audio),
        path_or_hf_repo=model,
        language="en",
        verbose=verbose,
        word_timestamps=True,
        initial_prompt=whisper_prompt(metadata, context),
    )


def render_whisper(result: dict[str, Any]) -> str:
    lines = []
    for segment in result.get("segments", []):
        start = timestamp(float(segment["start"]))
        end = timestamp(float(segment["end"]))
        text = str(segment["text"]).strip()
        if text:
            lines.append(f"[{start}-{end}] {text}")
    return "\n".join(lines) + "\n"


def save_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download an X/Twitter video and transcribe it with local MLX Whisper"
    )
    parser.add_argument("url", help="X/Twitter status URL containing a video")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: outputs/<status-id>)",
    )
    parser.add_argument(
        "--context",
        help="Names, terminology, speaker hints, or other source context",
    )
    parser.add_argument("--whisper-model", default=DEFAULT_WHISPER_MODEL)
    parser.add_argument(
        "--force", action="store_true", help="Regenerate existing intermediate files"
    )
    parser.add_argument("--verbose", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = args.output_dir or Path("outputs") / output_name(args.url)
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = output_dir / "metadata.json"
    source = None if args.force else find_source(output_dir)
    if source is None:
        print("[1/3] Downloading audio with yt-dlp...", flush=True)
        source, metadata = download(args.url, output_dir, args.verbose)
        save_json(metadata_path, metadata)
    else:
        print(f"[1/3] Reusing {source}", flush=True)
        metadata = (
            json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata_path.exists()
            else {"webpage_url": args.url}
        )

    normalized = output_dir / "audio-16k.wav"
    if args.force or not normalized.exists():
        print("[2/3] Normalizing audio...", flush=True)
        normalize_audio(source, normalized)
    else:
        print(f"[2/3] Reusing {normalized}", flush=True)

    whisper_json = output_dir / "whisper.json"
    whisper_md = output_dir / "transcript-whisper.md"
    if args.force or not whisper_md.exists():
        print(f"[3/3] Transcribing with {args.whisper_model}...", flush=True)
        result = run_whisper(
            normalized,
            args.whisper_model,
            metadata,
            args.context,
            args.verbose,
        )
        save_json(whisper_json, result)
        whisper_md.write_text(render_whisper(result), encoding="utf-8")
    else:
        print(f"[3/3] Reusing {whisper_md}", flush=True)

    print(str(output_dir.resolve()))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
