# multimodal-extraction

Builds a multimodal Markdown timeline from a video.

Given a local MP4 or a video URL, this skill downloads the media if needed, extracts slide frames and key visual moments, transcribes the audio, and writes one Markdown file that interleaves screenshots with the transcript at the right timestamps.

## What It Produces

- A local video file if the input was a URL
- Thumbnail candidates and slide frames
- A Whisper transcript JSON
- A final Markdown artifact that combines visuals and transcript spans

## Default Pipeline

1. If the input is a URL, download it with `yt-dlp`
2. Run `thumbnail-extraction` with `--extract-slides`
3. Extract and normalize audio with `ffmpeg`
4. Run local `whisper` with JSON output
5. Merge slide/key-frame timestamps with transcript segments into one Markdown timeline

## Modes

The pipeline should support three practical modes. Default to `swift`.

### 1. `swift` (Default)

Fastest end-to-end path.

What it does:
- downloads the video if needed
- extracts slide transitions and key frames with cheap heuristics
- runs local Whisper transcription
- writes the Markdown timeline
- clusters rapid slide bursts in display only, so the document does not spam full-width screenshots

What it does not do:
- no OCR on slides
- no LLM post-processing
- no transcript enrichment from slide text

Tradeoff:
- best speed
- good for quickly making a usable multimodal transcript
- lower semantic accuracy when slides contain important text, charts, or terminology that the transcript would benefit from

Best for:
- first-pass notes
- long videos
- cheap local runs

### 2. `context`

Balanced mode. Best default when you care about usefulness more than raw speed.

What it adds on top of `swift`:
- OCR on extracted slides
- uses slide text as nearby context for the surrounding transcript span
- keeps burst clustering so rapid slide changes are grouped instead of shown as many large images

Tradeoff:
- noticeably more useful than `swift`
- moderate runtime increase
- still mostly heuristic and parallelizable

Best for:
- talks, decks, and webinars where slide text matters
- generating study notes or recap docs
- cases where transcript alone misses chart labels, section titles, or technical terms

### 3. `polish`

Highest quality mode in this family.

What it adds on top of `context`:
- optional LLM cleanup over slide-cluster plus transcript windows
- better association of nearby speech to the most relevant slide content
- can synthesize short captions or contextual headers for each section

Tradeoff:
- slowest
- highest complexity
- best output quality, but no longer the cheapest or fastest path

Best for:
- polished deliverables
- shareable docs
- research or teaching material where the output will be read closely

## Recommended Tradeoff

Use `swift` by default for raw speed.

Use `context` when slide text matters and you still want a mostly local, parallelizable workflow.

Use `polish` only when the final document quality is worth the extra processing and model cost.

## Typical Usage

```bash
python3 multimodal_extract.py /path/to/video.mp4 ~/Downloads/multimodal_output --mode swift

python3 multimodal_extract.py "https://www.youtube.com/watch?v=..." ~/Downloads/multimodal_output --mode context

python3 multimodal_extract.py video.mp4 ~/Downloads/multimodal_output \
  --mode polish \
  --language en \
  --whisper-model turbo \
  --top-n 6
```

## Output Layout

- `source/` — downloaded or copied source media
- `visuals/` — output from `thumbnail-extraction`
- `audio/` — preprocessed WAV for ASR
- `transcript/` — Whisper JSON
- `multimodal_timeline.md` — merged Markdown artifact

## Notes

- This skill is optimized for end-to-end speed, not the most expensive multimodal reasoning path.
- It reuses `thumbnail-extraction` for the visual timeline and `whisper` for the transcript.
- If you need better diarization or a different backend, extend the transcription step later rather than bloating the first version.
- In real slide decks, some transitions happen only a few seconds apart. Those are often better displayed as a clustered burst or small grid rather than many full-width screenshots.
- The best speed/accuracy tradeoff usually comes from extracting visuals cheaply first, then enriching only the ambiguous or high-information parts.
