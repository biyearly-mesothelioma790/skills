# Transcribe Anything

Speech-to-text for audio and video files. Handles files from 30 seconds to 8+ hours with pluggable ASR backends.

## Setup

### Minimum (gets you running)

```bash
brew install ffmpeg
pip3 install --break-system-packages openai-whisper
```

### Recommended (long files + diarization)

```bash
brew install ffmpeg yt-dlp
pip3 install --break-system-packages openai-whisper faster-whisper whisperx curl_cffi
```

For speaker diarization, whisperX needs a Hugging Face token with pyannote access:
1. Accept terms at https://huggingface.co/pyannote/speaker-diarization-3.1 and https://huggingface.co/pyannote/segmentation-3.0
2. Set `export HF_TOKEN=hf_...` in your shell profile

### Cloud APIs (optional)

None required — local whisper works out of the box. Set any of these for cloud backends:

```bash
export OPENAI_API_KEY=sk-...       # Best accuracy, gpt-4o-transcribe ($0.006/min)
export GROQ_API_KEY=gsk_...        # Cheapest + fastest ($0.00004/min turbo)
export DEEPGRAM_API_KEY=...        # Best cloud diarization ($0.0043/min)
export ASSEMBLYAI_API_KEY=...      # Diarization + auto-chapters ($0.0062/min)
export GEMINI_API_KEY=...          # Handles 9.5hr files, flexible prompting
```

### Verify

```bash
which ffmpeg && which whisper && echo "Ready to transcribe"
```

## Problem

Getting a good transcript involves more than running whisper. Long files hallucinate without silence detection. Video needs audio extraction. Different use cases need different backends (local speed vs cloud diarization vs cost). Cloud APIs have 25MB limits that need chunking.

## What This Skill Does

1. Extracts audio from any video/audio format via ffmpeg
2. Preprocesses for optimal ASR (mono 16kHz, loudness normalized, bandpass filtered)
3. Detects and skips silence for long files
4. Transcribes using a pluggable backend
5. Formats output as markdown with periodic timestamps and optional speaker labels

## Backends

| Backend | Best For | Diarization | Speed (1hr, Apple Silicon) |
|---------|----------|-------------|---------------------------|
| whisper (default) | General use | No | ~20-40 min |
| whisperx | Speaker labels | Yes | ~15-30 min |
| faster-whisper | Long files, VAD | No | ~10-20 min |
| whisper.cpp | Metal acceleration | No | ~10-15 min |
| Groq API | Speed + cost | No | seconds |
| OpenAI API | Accuracy | No | ~1-2 min |
| Deepgram | Cloud diarization | Yes | ~1-2 min |
| AssemblyAI | Diarization + chapters | Yes | ~2-5 min |
| Gemini | 9.5hr files, Q&A | Prompted | ~1-3 min |

## Quick Usage

```bash
# Basic local transcription
whisper recording.mp3 --model turbo --language en --output_format json

# Preprocess video for best quality
ffmpeg -i video.mp4 -vn -ac 1 -ar 16000 -acodec pcm_s16le \
  -af "highpass=f=80,lowpass=f=8000,loudnorm=I=-16:TP=-1.5:LRA=11" audio.wav
whisper audio.wav --model turbo --language en --condition_on_previous_text False
```

## Long File Tips

- Always use `--condition_on_previous_text False` on files over 30 min (prevents hallucination cascades)
- Use faster-whisper with `vad_filter=True` to skip silence automatically
- Compress to opus 32kbps before cloud APIs (1hr = ~14MB, under 25MB limit)
- Remove intro/outro music before transcribing

See SKILL.md for the full workflow, all backend commands, custom vocabulary, and troubleshooting.
