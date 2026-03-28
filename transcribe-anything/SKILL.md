---
name: transcribe-anything
description: |
  Transcribes audio and video files to text using pluggable ASR backends. Default backend is local whisper CLI (openai-whisper). Supports whisperX (with diarization), insanely-fast-whisper, faster-whisper, whisper.cpp, OpenAI Whisper API, Groq Whisper API, Deepgram, AssemblyAI, Gemini, and Hugging Face models. Handles very long files (1-8+ hours) by preprocessing with ffmpeg: extracts audio from video, converts to optimal ASR format, detects and skips silence, and chunks for API size limits. Supports speaker diarization, word-level timestamps, custom vocabulary, and multiple output formats. Use this skill when someone says "transcribe this", "convert to text", "speech to text", "get the transcript", "transcribe this video/audio/podcast/recording", or provides a media file and wants text output.
license: MIT
compatibility: |
  Requires macOS (Apple Silicon recommended) with ffmpeg installed. At minimum one ASR backend must be available — openai-whisper is the default (pip install openai-whisper). For diarization, whisperX is recommended (pip install whisperx). For cloud backends, relevant API keys must be set as environment variables.
metadata:
  author: swyxio
  version: "1.0"
  last-updated: "2026-03-28"
  hardware: Apple Silicon (M-series), also works on CUDA GPUs and CPU
  primary-tools: ffmpeg, whisper, whisperx, yt-dlp
---

# Transcribe Anything

Transcribes audio and video files to text. Pluggable backends, silence skipping for long files, optional speaker diarization, and multiple output formats.

## Setup

### Required (install these first)

```bash
# ffmpeg — audio extraction, preprocessing, silence detection
brew install ffmpeg

# yt-dlp — downloading video/audio from URLs (optional but recommended)
brew install yt-dlp

# Default ASR backend — OpenAI's whisper CLI
pip3 install --break-system-packages openai-whisper
```

### Recommended Extras

```bash
# curl_cffi — prevents OAuth errors when downloading private videos
pip3 install --break-system-packages curl_cffi

# faster-whisper — 4x faster than whisper, built-in VAD silence skipping, lower memory
# Best local backend for long files (1hr+)
pip3 install --break-system-packages faster-whisper

# whisperX — adds speaker diarization + precise word-level timestamps
# Bundles faster-whisper + pyannote alignment
pip3 install --break-system-packages whisperx
```

**whisperX diarization setup** (one-time):
1. Create a Hugging Face account at https://huggingface.co
2. Accept the terms for these gated models:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
3. Create an access token at https://huggingface.co/settings/tokens
4. Set `export HF_TOKEN=hf_...` in your shell profile

Without HF token access, whisperX still works for transcription and word alignment — just no speaker labels.

### Other Local Backends (optional, pick what you need)

```bash
# insanely-fast-whisper — batched GPU inference, 10-20x faster on NVIDIA GPUs
pip3 install --break-system-packages insanely-fast-whisper

# whisper.cpp — C++ native with Metal acceleration on Apple Silicon
# Best option if you want to avoid Python entirely
brew install whisper-cpp
```

### Cloud API Keys (optional)

Set these environment variables if you want to use cloud backends. None are required — local whisper works out of the box.

```bash
# OpenAI — best accuracy with gpt-4o-transcribe ($0.006/min)
export OPENAI_API_KEY=sk-...

# Groq — cheapest and fastest cloud option ($0.00004/min with turbo)
export GROQ_API_KEY=gsk_...

# Deepgram — best cloud diarization ($0.0043/min)
export DEEPGRAM_API_KEY=...

# AssemblyAI — cloud diarization + auto-chapters ($0.0062/min)
export ASSEMBLYAI_API_KEY=...

# Gemini — handles 9.5hr files natively, flexible prompting
export GEMINI_API_KEY=...
```

### Verify Your Setup

Run this to check what's available:

```bash
echo "=== Required ==="
which ffmpeg && echo "ffmpeg: OK" || echo "ffmpeg: MISSING (brew install ffmpeg)"
which whisper && echo "whisper: OK" || echo "whisper: MISSING (pip3 install --break-system-packages openai-whisper)"

echo ""
echo "=== Local Backends ==="
which whisperx && echo "whisperx: OK" || echo "whisperx: not installed"
python3 -c "import faster_whisper" 2>/dev/null && echo "faster-whisper: OK" || echo "faster-whisper: not installed"
which insanely-fast-whisper 2>/dev/null && echo "insanely-fast-whisper: OK" || echo "insanely-fast-whisper: not installed"
which whisper-cpp 2>/dev/null && echo "whisper.cpp: OK" || echo "whisper.cpp: not installed"

echo ""
echo "=== Cloud APIs ==="
[ -n "$OPENAI_API_KEY" ] && echo "OpenAI: configured" || echo "OpenAI: not set"
[ -n "$GROQ_API_KEY" ] && echo "Groq: configured" || echo "Groq: not set"
[ -n "$DEEPGRAM_API_KEY" ] && echo "Deepgram: configured" || echo "Deepgram: not set"
[ -n "$ASSEMBLYAI_API_KEY" ] && echo "AssemblyAI: configured" || echo "AssemblyAI: not set"
[ -n "$GEMINI_API_KEY" ] && echo "Gemini: configured" || echo "Gemini: not set"

echo ""
echo "=== Optional ==="
which yt-dlp && echo "yt-dlp: OK" || echo "yt-dlp: not installed (brew install yt-dlp)"
python3 -c "import curl_cffi" 2>/dev/null && echo "curl_cffi: OK" || echo "curl_cffi: not installed"
[ -n "$HF_TOKEN" ] && echo "HF token: configured (diarization ready)" || echo "HF token: not set (no diarization)"
```

## Backend Selection Guide

Pick the backend based on the user's needs:

| Scenario | Backend | Why |
|----------|---------|-----|
| Default / just works | `whisper` | Already installed, good quality |
| Need speaker labels | `whisperx` | Integrated diarization + word alignment |
| Very long file, local | `faster-whisper` | VAD silence skipping, low memory |
| Maximum speed, local GPU | `insanely-fast-whisper` | Batched inference, 10-20x faster |
| Apple Silicon, no Python | `whisper.cpp` | Metal acceleration, pure C++ |
| Cheapest cloud, fast | `groq` | $0.00004/min with turbo model |
| Best cloud accuracy | `openai` | gpt-4o-transcribe model |
| Cloud with diarization | `deepgram` or `assemblyai` | Native speaker labels |
| Flexible Q&A over audio | `gemini` | Can ask questions, not just transcribe |

If the user doesn't specify, use this priority:
1. `whisper` (already installed locally)
2. `whisperx` (if diarization requested and installed)
3. `openai` API (if OPENAI_API_KEY is set and file is manageable)

## Step-by-Step Workflow

### Step 1: Identify the Input

Accept any of these input types:
- Audio files: mp3, wav, flac, ogg, m4a, opus, wma, aac
- Video files: mp4, mkv, webm, mov, avi, wmv
- URLs: Use the download-video skill first, or yt-dlp directly

If the input is a URL:
```bash
yt-dlp -x --audio-format wav -o "%(title)s.%(ext)s" "{url}"
```

### Step 2: Preprocess Audio with ffmpeg

**Always preprocess.** This step is critical for quality and speed.

```bash
# Extract audio from video (or re-encode audio) to ASR-optimal format
ffmpeg -i "{input}" \
  -vn \
  -ac 1 \
  -ar 16000 \
  -acodec pcm_s16le \
  -af "highpass=f=80,lowpass=f=8000,loudnorm=I=-16:TP=-1.5:LRA=11" \
  "{output_stem}_preprocessed.wav"
```

Flags explained:
- `-vn` — strip video
- `-ac 1` — mono (stereo wastes processing time, no ASR benefit)
- `-ar 16000` — 16kHz (what whisper expects internally)
- `-acodec pcm_s16le` — 16-bit WAV
- `highpass=f=80` — remove rumble below speech range
- `lowpass=f=8000` — remove hiss above speech range
- `loudnorm` — normalize volume (critical for variable-volume recordings)

**Check duration after preprocessing:**
```bash
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "{preprocessed_file}" | cut -d. -f1)
echo "Duration: ${DURATION}s ($((DURATION / 3600))h $(((DURATION % 3600) / 60))m)"
```

### Step 3: Handle Long Files (>30 minutes)

For files over 30 minutes, apply silence detection and chunking. This is especially important for 1-8 hour recordings.

#### 3a: Silence Analysis

```bash
# Detect silent regions (informational — see what we're working with)
ffmpeg -i "{preprocessed_file}" \
  -af silencedetect=noise=-30dB:d=2.0 \
  -f null - 2>&1 | grep -c "silence_end"
# Shows number of silence gaps >= 2 seconds
```

Silence threshold guide:
- `-30dB` — clean recordings (studio, podcast)
- `-35dB` — moderate background noise
- `-40dB` — noisy environments

#### 3b: For Local Backends (whisper, whisperx, faster-whisper)

Local backends handle long files natively — no need to chunk. But use VAD to skip silence:

**With faster-whisper (built-in VAD):**
```python
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    "preprocessed.wav",
    language="en",
    word_timestamps=True,
    vad_filter=True,
    vad_parameters=dict(
        min_silence_duration_ms=1000,
        speech_pad_ms=400,
        threshold=0.5,
    ),
    condition_on_previous_text=False,  # prevents hallucination cascades on long files
)
```

**With whisper CLI (no built-in VAD — preprocess silence out):**
```bash
# Remove silences longer than 2s, keeping 0.3s padding
ffmpeg -i "{preprocessed_file}" \
  -af "silenceremove=start_periods=1:start_threshold=-30dB:stop_periods=-1:stop_duration=2.0:stop_threshold=-30dB" \
  "{output_stem}_trimmed.wav"

# Then transcribe the trimmed file
whisper "{output_stem}_trimmed.wav" --model turbo --language en \
  --condition_on_previous_text False \
  --word_timestamps True \
  --output_format json \
  --output_dir ./
```

**Important for long files:** Always use `--condition_on_previous_text False` with whisper on files over 30 minutes. Without this, a single hallucination can cascade and corrupt hours of transcript (whisper repeats the same phrase endlessly).

#### 3c: For Cloud APIs (25MB file size limit)

Cloud APIs (OpenAI, Groq) have a 25MB limit. Compress first, then chunk if needed.

```bash
# Compress to opus (smallest format for speech) — 1 hour ≈ 14MB
ffmpeg -i "{preprocessed_file}" -ac 1 -ar 16000 -c:a libopus -b:a 32k "{output_stem}.ogg"

# Check file size
SIZE_MB=$(du -m "{output_stem}.ogg" | cut -f1)
echo "File size: ${SIZE_MB}MB"
```

If the compressed file is under 25MB, send it directly. Otherwise, chunk on silence boundaries:

```bash
# Split into ~20-minute chunks on silence boundaries
# (under 25MB each at opus 32kbps)
ffmpeg -i "{output_stem}.ogg" \
  -f segment \
  -segment_time 1200 \
  -c copy \
  "{output_stem}_chunk_%03d.ogg"
```

For each chunk, track the start offset for timestamp correction:
```bash
# Get duration of each chunk for timestamp reassembly
for f in {output_stem}_chunk_*.ogg; do
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  echo "$f: ${dur}s"
done
```

### Step 4: Transcribe

#### Backend: whisper (default)

```bash
whisper "{input_file}" \
  --model turbo \
  --language en \
  --output_format json \
  --output_dir "{output_dir}" \
  --word_timestamps True \
  --condition_on_previous_text False \
  --fp16 False
```

Model selection for Apple Silicon (CPU — no CUDA):
- `turbo` — best balance of speed and quality (recommended default)
- `large-v3` — highest quality, 2-3x slower than turbo
- `medium.en` — faster, English-only, good for clear speech
- `small.en` — fast, acceptable quality for clean recordings
- `base.en` — fastest, use only for quick previews

Note: `--fp16 False` is required on CPU (Apple Silicon without MLX). Whisper defaults to fp16 which only works on CUDA.

#### Backend: whisperx (with diarization)

```bash
whisperx "{input_file}" \
  --model large-v3 \
  --language en \
  --diarize \
  --min_speakers 2 \
  --max_speakers 6 \
  --hf_token "{HF_TOKEN}" \
  --compute_type int8 \
  --output_dir "{output_dir}" \
  --output_format json
```

If no HF token is available, whisperX still works for transcription and word alignment, just without diarization:
```bash
whisperx "{input_file}" \
  --model large-v3 \
  --language en \
  --compute_type int8 \
  --output_dir "{output_dir}" \
  --output_format json
```

#### Backend: faster-whisper (Python, best for long files)

```python
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    "{input_file}",
    language="en",
    beam_size=5,
    word_timestamps=True,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=1000),
    condition_on_previous_text=False,
)

for segment in segments:
    print(f"[{segment.start:.2f} -> {segment.end:.2f}] {segment.text}")
```

#### Backend: insanely-fast-whisper (GPU batched)

```bash
insanely-fast-whisper \
  --file-name "{input_file}" \
  --model-name openai/whisper-large-v3-turbo \
  --task transcribe \
  --language en \
  --batch-size 24 \
  --timestamp word \
  --transcript-path "{output_stem}.json"
```

#### Backend: whisper.cpp (Metal acceleration on Apple Silicon)

```bash
# Download model if needed
whisper-cpp-download-model large-v3

# Transcribe with Metal GPU acceleration
whisper-cpp \
  -m ~/.local/share/whisper-cpp/ggml-large-v3.bin \
  -f "{preprocessed_wav}" \
  -l en \
  -t 8 \
  --output-json \
  --print-progress
```

Note: whisper.cpp requires WAV input (not mp3/ogg). Always preprocess to WAV first.

#### Backend: OpenAI API

```bash
curl -s https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@{input_file}" \
  -F model="gpt-4o-transcribe" \
  -F language="en" \
  -F response_format="verbose_json" \
  -F 'timestamp_granularities[]=word' \
  -F 'timestamp_granularities[]=segment' \
  > "{output_stem}_openai.json"
```

For multiple chunks, loop and offset timestamps:
```bash
OFFSET=0
for chunk in {output_stem}_chunk_*.ogg; do
  curl -s https://api.openai.com/v1/audio/transcriptions \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -F file="@$chunk" \
    -F model="gpt-4o-transcribe" \
    -F language="en" \
    -F response_format="verbose_json" \
    -F 'timestamp_granularities[]=segment' \
    > "${chunk%.ogg}_transcript.json"

  DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$chunk")
  OFFSET=$(echo "$OFFSET + $DUR" | bc)
done
```

#### Backend: Groq API (cheapest cloud)

Same OpenAI-compatible format, different base URL:
```bash
curl -s https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@{input_file}" \
  -F model="whisper-large-v3-turbo" \
  -F language="en" \
  -F response_format="verbose_json" \
  -F 'timestamp_granularities[]=word' \
  -F 'timestamp_granularities[]=segment' \
  > "{output_stem}_groq.json"
```

#### Backend: Deepgram (cloud, native diarization)

```bash
curl -s -X POST "https://api.deepgram.com/v1/listen?model=nova-3&smart_format=true&diarize=true&language=en&utterances=true" \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: audio/wav" \
  --data-binary "@{input_file}" \
  > "{output_stem}_deepgram.json"
```

#### Backend: AssemblyAI (cloud, native diarization + chapters)

```python
import assemblyai as aai
aai.settings.api_key = os.environ["ASSEMBLYAI_API_KEY"]

config = aai.TranscriptionConfig(
    speaker_labels=True,
    language_code="en",
    auto_chapters=True,
    word_boost=["custom", "vocabulary", "terms"],
)

transcript = aai.Transcriber().transcribe("{input_file}", config=config)

for utterance in transcript.utterances:
    print(f"Speaker {utterance.speaker}: {utterance.text}")
```

#### Backend: Gemini (flexible, prompt-based)

```python
import google.generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")
audio = genai.upload_file("{input_file}")

response = model.generate_content([
    audio,
    """Transcribe this audio verbatim. Format as markdown with:
    - Timestamps every ~30 seconds as ### headers (e.g., ### [00:01:30])
    - Speaker labels if you can distinguish voices (Speaker 1, Speaker 2, etc.)
    - Paragraph breaks at natural topic shifts
    Do not summarize or omit anything. Transcribe every word spoken."""
])

print(response.text)
```

Note: Gemini handles up to ~9.5 hours natively (no chunking needed) but timestamps are approximate and output is unstructured text shaped by your prompt.

### Step 5: Format Output

The user's default preference is **markdown-formatted plain text**. Convert the raw backend output to this format.

#### Default: Markdown transcript

```markdown
# Transcript: {filename}

**Date transcribed:** {date}
**Duration:** {duration}
**Backend:** {backend}
**Model:** {model}

---

## [00:00:00]

{text of first segment or group of segments...}

## [00:05:23]

{text continues with periodic timestamp headers...}

---

*Transcribed with {backend} ({model})*
```

**Formatting rules:**
- Insert `## [HH:MM:SS]` timestamp headers every 2-5 minutes (not every segment — that's too noisy)
- Group consecutive segments by the same speaker into paragraphs
- If diarization is available, prefix with bold speaker labels: `**Speaker 1:** text...`
- Use `---` horizontal rules at major topic shifts or long pauses (>10s)
- Keep paragraph breaks at natural sentence boundaries

#### With speaker diarization:

```markdown
# Transcript: {filename}

**Speakers:** 3 detected
**Duration:** 1h 23m

---

## [00:00:00]

**Speaker 1:** Welcome everyone to today's session. We're going to be talking about...

**Speaker 2:** Thanks for having me. I'm excited to share...

## [00:05:12]

**Speaker 1:** Let's dive into the first topic...
```

#### Alternative output formats

If the user requests a different format:

**SRT subtitles:**
```bash
whisper "{input}" --model turbo --output_format srt --output_dir ./
```

**VTT subtitles:**
```bash
whisper "{input}" --model turbo --output_format vtt --output_dir ./
```

**JSON with word timestamps:**
```bash
whisper "{input}" --model turbo --output_format json --word_timestamps True --output_dir ./
```

**Plain text (no timestamps):**
```bash
whisper "{input}" --model turbo --output_format txt --output_dir ./
```

**TSV (tab-separated, for spreadsheets):**
```bash
whisper "{input}" --model turbo --output_format tsv --output_dir ./
```

## Custom Vocabulary / Prompt Hints

Whisper supports an `initial_prompt` that biases the model toward specific terminology:

```bash
whisper "{input}" --model turbo --language en \
  --initial_prompt "This conversation discusses Kubernetes, GitLab CI/CD, Terraform, and Infrastructure as Code. Names mentioned: Sid Sijbrandij, David Thompson."
```

For cloud APIs:
```bash
# OpenAI - use the prompt parameter
curl ... -F prompt="Technical terms: LLM, RAG, vector database, embeddings. Names: Sid Sijbrandij."

# AssemblyAI - use word_boost
config = aai.TranscriptionConfig(
    word_boost=["Kubernetes", "GitLab", "Sijbrandij", "Terraform"],
    boost_param="high",
)

# Deepgram - use keywords
curl ... "https://api.deepgram.com/v1/listen?keywords=Kubernetes:2&keywords=GitLab:2"
```

**When to use custom vocabulary:**
- Proper nouns (people, companies, products)
- Domain-specific jargon
- Acronyms that might be misheard (e.g., "RAG" vs "rag")
- Non-English words in English speech

## Handling Specific Input Types

### Podcast with intro/outro music

Music segments cause hallucinations. Trim them:
```bash
# Skip first 30s (intro music) and last 30s (outro)
TOTAL=$(ffprobe -v error -show_entries format=duration -of csv=p=0 input.mp3 | cut -d. -f1)
END=$((TOTAL - 30))
ffmpeg -i input.mp3 -ss 30 -to $END -ac 1 -ar 16000 -acodec pcm_s16le trimmed.wav
```

### Multi-track recording (separate speaker mics)

If each speaker has their own audio track:
```bash
# Extract each track
ffmpeg -i recording.mkv -map 0:a:0 -ac 1 -ar 16000 speaker1.wav
ffmpeg -i recording.mkv -map 0:a:1 -ac 1 -ar 16000 speaker2.wav

# Transcribe each separately (no diarization needed)
whisper speaker1.wav --model turbo --output_format json
whisper speaker2.wav --model turbo --output_format json

# Then interleave by timestamps in the markdown output
```

### Stereo recording (L/R = different speakers)

```bash
# Split channels
ffmpeg -i stereo.wav -af "pan=mono|c0=FL" -ar 16000 left.wav
ffmpeg -i stereo.wav -af "pan=mono|c0=FR" -ar 16000 right.wav

# Transcribe each channel as a separate speaker
```

### Video from URL (download + transcribe)

```bash
# Download audio only
yt-dlp -x --audio-format wav -o "%(title)s.%(ext)s" "{url}"

# Then run the standard preprocessing + transcription pipeline
```

## Troubleshooting

### Whisper repeats the same phrase endlessly
The hallucination cascade problem. Fix: use `--condition_on_previous_text False`. If already set, the input likely has long silence or music — preprocess with silence removal.

### Very slow on Apple Silicon
Whisper's Python implementation doesn't use Metal/MPS well. Options:
- Use `whisper.cpp` for Metal GPU acceleration
- Use `--model turbo` instead of `large-v3` (2-3x faster, minimal quality loss)
- Use `--model medium.en` for English-only (4-5x faster)
- Use Groq API (transcribes hours in seconds, nearly free)

### Out of memory
- Use `faster-whisper` with `compute_type="int8"` (halves memory)
- Use a smaller model (`medium` or `small`)
- Chunk the file (see Step 3c)

### pip install fails with "externally-managed-environment"
Modern macOS Python (Homebrew) requires:
```bash
pip3 install --break-system-packages {package}
```

### Word timestamps are inaccurate
Whisper's native word timestamps are approximate. For precise word-level timing, use whisperX which adds forced phoneme alignment.

### Foreign language or accent issues
- Omit `--language` to let whisper auto-detect
- Use `large-v3` (best multilingual model)
- Use `--initial_prompt` with example text in the target language
- For code-switching (multiple languages in one recording), Gemini handles this better than Whisper

## Backend Comparison Quick Reference

| Backend | Install | Diarization | VAD | Speed (1hr file, Apple Silicon) | Cost |
|---------|---------|-------------|-----|-------------------------------|------|
| whisper | `pip install openai-whisper` | No | No | ~20-40 min (turbo) | Free |
| whisperx | `pip install whisperx` | Yes (pyannote) | Yes | ~15-30 min | Free |
| faster-whisper | `pip install faster-whisper` | No | Yes (Silero) | ~10-20 min | Free |
| insanely-fast-whisper | `pip install insanely-fast-whisper` | Experimental | No | ~5-10 min (GPU) | Free |
| whisper.cpp | `brew install whisper-cpp` | Basic | No | ~10-15 min (Metal) | Free |
| OpenAI API | API key | No | N/A | ~1-2 min | $0.006/min |
| Groq API | API key | No | N/A | ~seconds | $0.00004/min |
| Deepgram | API key | Yes (native) | N/A | ~1-2 min | $0.0043/min |
| AssemblyAI | API key | Yes (native) | N/A | ~2-5 min | $0.0062/min |
| Gemini | API key | Prompted | N/A | ~1-3 min | Token-based |
