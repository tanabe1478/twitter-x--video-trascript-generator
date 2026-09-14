# Twitter/X Video Transcript Generator

X（Twitter）の動画をローカルWhisperで文字起こしし、Piのモデルで英語補正と日本語訳を生成する **Pi Package / Extension** です。

## パイプライン

1. `yt-dlp` で動画の音声を取得
2. ローカルの MLX Whisper (`whisper-large-v3-turbo`) で英語を文字起こし
3. `pi -p --model google-vertex/gemini-2.5-pro` で誤認識を補正
   - 失敗時は `google-vertex/gemini-2.5-flash` にフォールバック
4. `pi -p --model google-vertex/gemini-2.5-flash` で日本語訳

Pythonが担当するのはダウンロード、音声の正規化、Whisperだけです。言語モデルはPython APIから呼ばず、Extensionが独立した `pi -p` プロセスとして起動します。

## なぜPackage + Extensionなのか

- **Package** はGitHubからインストール・更新するための配布単位です。
- **Extension** は `/x-transcribe` コマンドと `x_video_transcript` ツールをPiへ追加します。
- **Skill** だけで構成するより処理が決定的で、親モデルによる手順の読み違いや余分なトークン消費を防げます。
- Pi SDKでモデルを直接呼ぶ方法もありますが、ここでは認証とモデル解決を通常のPiと揃えるため、明示的に `pi -p` を使用します。

## 必要なもの

- macOS / Apple Silicon
- Python 3.11以上
- Pi 0.85.1以上
- 使用するモデルのプロバイダーをPiで認証済みであること

利用可能なモデルは次のコマンドで確認できます。

```bash
pi --list-models
```

デフォルト構成では、Vertex AIの次のモデルを使用します。

```text
google-vertex/gemini-2.5-pro
google-vertex/gemini-2.5-flash
```

モデルは環境変数で任意のPiモデルへ変更できます。

## インストール

GitHubからPi Packageとしてインストールします。

```bash
pi install https://github.com/tanabe1478/twitter-x--video-trascript-generator
```

Piを起動または `/reload` した後、ローカルWhisper環境を一度だけセットアップします。

```text
/x-transcribe-setup
```

デフォルトでは `~/.cache/twitter-x-video-transcript-generator/venv` にPython仮想環境を作成します。初回のWhisper実行時にはHugging Faceからモデルがダウンロードされます。

## 使用方法

### Slash command

```text
/x-transcribe https://x.com/pidotdev/status/2099045420496486415 Interview with Mario Zechner and Armin Ronacher about Pi, Astra, coding agents, and slop.
```

URLだけを指定することもできます。

```text
/x-transcribe https://x.com/pidotdev/status/2099045420496486415
```

指定した投稿に動画がなく、動画投稿への返信だった場合は、親投稿を最大5件まで自動的に追跡します。`metadata.json` の `requested_url` と `resolved_url` で確認できます。

引数なしで `/x-transcribe` を実行すると、URLと補足情報の入力ダイアログが表示されます。

### 通常の会話から利用

Extensionは `x_video_transcript` ツールも登録します。そのためPiへ自然文で依頼できます。

```text
https://x.com/example/status/123 の動画を文字起こしして日本語に翻訳して
```

## モデル設定

モデルは環境変数で変更できます。値はPiの完全なモデルセレクターです。

```bash
export XVT_REFINE_MODEL='google-vertex/gemini-2.5-pro'
export XVT_REFINE_FALLBACK_MODEL='google-vertex/gemini-2.5-flash'
export XVT_TRANSLATION_MODEL='google-vertex/gemini-2.5-flash'
```

その他の設定:

| 環境変数 | デフォルト | 説明 |
|---|---|---|
| `XVT_REFINE_MODEL` | `google-vertex/gemini-2.5-pro` | 英語補正モデル |
| `XVT_REFINE_FALLBACK_MODEL` | `google-vertex/gemini-2.5-flash` | 補正失敗時のモデル |
| `XVT_TRANSLATION_MODEL` | `google-vertex/gemini-2.5-flash` | 日本語翻訳モデル |
| `XVT_WHISPER_MODEL` | `mlx-community/whisper-large-v3-turbo` | ローカルWhisperモデル |
| `XVT_OUTPUT_DIR` | `outputs` | 実行ディレクトリからの出力ルート |
| `XVT_VENV_DIR` | `~/.cache/twitter-x-video-transcript-generator/venv` | Python仮想環境 |
| `XVT_PYTHON` | `python3` | セットアップに使うPython |
| `XVT_LOCAL_TRANSCRIBER` | 仮想環境内のコマンド | ローカル処理コマンドの上書き |

ツール呼び出しでは、環境変数を変えずリクエスト単位でモデルや出力先を上書きすることもできます。

## `pi -p` の実行形

Extension内部では、おおむね次の形で別Piプロセスを起動します。

```bash
pi \
  --model "$XVT_REFINE_MODEL" \
  --thinking high \
  --no-tools \
  --no-session \
  --no-context-files \
  --no-extensions \
  --no-skills \
  --print \
  @outputs/STATUS_ID/refine-prompt.md
```

翻訳では `XVT_TRANSLATION_MODEL` と `--thinking low` を使用します。子プロセスではツールやExtensionを無効にし、再帰的な起動とプロンプトインジェクションの影響を抑えています。

## 出力

デフォルトでは、Piを起動したディレクトリの `outputs/<status-id>/` に保存します。

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

## ローカル開発

```bash
npm install
npm run check

python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -v

pi -e .
```

ローカルWhisperだけを直接実行する場合:

```bash
.venv/bin/x-video-transcript-local \
  'https://x.com/example/status/123' \
  --output-dir outputs/123
```

## 注意点

- 補正・翻訳モデルには音声を渡しません。元音声を扱うのはローカルWhisperだけです。
- 人名、製品名、モデル名はコンテキストとして与えると精度が上がります。
- モデル呼び出しは、指定したプロバイダーの利用枠または料金を消費する場合があります。
- 動画と音声の利用は、権利者の許諾と各サービスの規約に従ってください。

## Examples

- [`examples/pi-developer-interview/`](./examples/pi-developer-interview/): 最初に作成した約13分のインタビュー
- [`examples/pi-self-modifying-harness/`](./examples/pi-self-modifying-harness/): OpenCode GoモデルによるEnd-to-End動作確認
- [`examples/pi-fomo/`](./examples/pi-fomo/): Vertex AIモデルによるEnd-to-End動作確認
- [`examples/pi-memory/`](./examples/pi-memory/): 動画投稿への返信URLを自動解決した例
