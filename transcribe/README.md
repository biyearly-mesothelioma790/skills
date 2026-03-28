# Transcribe

Speech-to-text for audio and video files. Handles files from 30 seconds to 8+ hours.

## Problem

Getting a good transcript from a media file involves more than just running whisper. Long files need silence detection to avoid hallucinations, video files need audio extraction, private/unlisted embeds need the right headers, and different use cases need different backends (local speed vs cloud diarization vs cost).

## What This Skill Does

1. Extracts audio from any video/audio format via ffmpeg
2. Preprocesses for optimal ASR quality (mono, 16kHz, normalized, bandpass filtered)
3. Detects and skips silence for long files
4. Transcribes using a pluggable backend
5. Formats output as markdown with periodic timestamps and optional speaker labels

## Prerequisites

```bash
brew install ffmpeg
pip3 install --break-system-packages openai-whisper  # default backend
```

## Quick Usage

```bash
# Basic transcription (uses whisper turbo model)
whisper recording.mp3 --model turbo --language en --output_format json

# From video
ffmpeg -i video.mp4 -vn -ac 1 -ar 16000 -acodec pcm_s16le \
  -af "highpass=f=80,lowpass=f=8000,loudnorm=I=-16:TP=-1.5:LRA=11" audio.wav
whisper audio.wav --model turbo --language en --condition_on_previous_text False
```

## Backends

| Backend | Best For | Diarization |
|---------|----------|-------------|
| whisper (default) | General use, already installed | No |
| whisperx | Speaker labels + word alignment | Yes |
| faster-whisper | Long files, VAD silence skip | No |
| Groq API | Speed + cost ($0.00004/min) | No |
| OpenAI API | Accuracy (gpt-4o-transcribe) | No |
| Deepgram / AssemblyAI | Cloud-native diarization | Yes |
| Gemini | Flexible, handles 9.5hr files | Prompted |

## Long File Tips

- Always use `--condition_on_previous_text False` on files over 30 min (prevents hallucination cascades)
- Use faster-whisper with `vad_filter=True` to skip silence automatically
- Compress to opus 32kbps before sending to cloud APIs (1hr = ~14MB, under the 25MB limit)
- Remove intro/outro music segments before transcribing

See SKILL.md for the full workflow, all backend commands, and troubleshooting guide.
