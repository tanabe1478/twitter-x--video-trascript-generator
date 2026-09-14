# Twitter/X Video Transcript Generator

X（Twitter）の動画をダウンロードし、英語文字起こしの補正と日本語訳を生成します。

## パイプライン

1. `yt-dlp` で動画の音声を取得
2. ローカルの MLX Whisper (`whisper-large-v3-turbo`) で英語を文字起こし
3. OpenCode Go の `grok-4.6` で文脈上明らかな誤認識を補正
   - APIエラー時は `qwen3.8-max` にフォールバック
4. OpenCode Go の `gpt-5.6-luna` で日本語訳

Whisper以外のモデルには音声を渡しません。OpenCode GoモデルはWhisperの下書きをテキストとして補正・翻訳します。

## 必要なもの

- macOS / Apple Silicon
- Python 3.11以上
- `pi` 0.85.1以上
- OpenCode Goサブスクリプション
- PiでOpenCode Goへログイン済みであること

利用可能か確認します。

```bash
pi --list-models opencode-go
```

少なくとも次のモデルが表示される必要があります。

```text
opencode-go/grok-4.6
opencode-go/qwen3.8-max
opencode-go/gpt-5.6-luna
```

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

初回のWhisper実行時には、Hugging Faceからモデルがダウンロードされます。

## 実行

```bash
x-video-transcript \
  'https://x.com/pidotdev/status/2099045420496486415' \
  --context 'Interview with Mario Zechner and Armin Ronacher about Pi, Astra, coding agents, and slop.'
```

出力先はデフォルトで `outputs/<status-id>/` です。

```text
metadata.json             動画のメタデータ
source.*                  ダウンロードした音声
audio-16k.wav             Whisper用に正規化した音声
whisper.json              Whisperの全結果
transcript-whisper.md     Whisperの下書き
refine-prompt.md          誤認識補正に使用したプロンプト
transcript-en.md          補正後の英語文字起こし
translate-prompt.md       翻訳に使用したプロンプト
transcript-ja.md          日本語訳
```

## モデルの変更

補正にQwenを直接使う場合:

```bash
x-video-transcript URL --refine-model qwen3.8-max
```

別のGoモデルを使う場合:

```bash
x-video-transcript URL \
  --refine-model grok-4.6 \
  --fallback-refine-model qwen3.8-max \
  --translation-model gpt-5.6-luna
```

## 再実行

既存の中間結果は自動的に再利用します。全工程を再生成する場合:

```bash
x-video-transcript URL --force
```

Whisperだけを実行し、OpenCode Goの利用枠を消費しない場合:

```bash
x-video-transcript URL --skip-refine --skip-translate
```

## 注意点

- OpenCode Goモデルは音声を聞けないため、音響的に曖昧な箇所を完全には検証できません。
- 人名、製品名、モデル名は `--context` で与えるとWhisperと補正モデルの精度が上がります。
- `grok-4.6`、`qwen3.8-max`、`gpt-5.6-luna` の利用はOpenCode Goの利用枠を消費します。
- 動画と音声のダウンロードおよび利用は、権利者の許諾と各サービスの規約に従ってください。

## Example

最初に作成したPi開発者インタビューの文字起こしは [`examples/pi-developer-interview/`](./examples/pi-developer-interview/) にあります。
