#!/usr/bin/env python3

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import parse_qs, urlparse


DEFAULT_OUTPUT_DIR = str(Path.home() / "Downloads" / "multimodal_output")
DEFAULT_TOP_N = 4
DEFAULT_WHISPER_MODEL = "turbo"
DEFAULT_LANGUAGE = "en"
DEFAULT_IMAGE_WIDTH = 860
DEFAULT_MODE = "swift"
BURST_GAP_SEC = 8.0
BURST_MAX_SPAN_SEC = 20.0
BURST_GRID_IMAGE_WIDTH = 260


def format_elapsed(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"{minutes}m {remainder:.1f}s"


def format_ts(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"


def parse_args(argv):
    positional = []
    language = DEFAULT_LANGUAGE
    whisper_model = DEFAULT_WHISPER_MODEL
    top_n = DEFAULT_TOP_N
    mode = DEFAULT_MODE

    args = argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--language":
            i += 1
            language = args[i]
        elif arg == "--whisper-model":
            i += 1
            whisper_model = args[i]
        elif arg == "--top-n":
            i += 1
            top_n = int(args[i])
        elif arg == "--mode":
            i += 1
            mode = args[i]
        else:
            positional.append(arg)
        i += 1

    source = positional[0] if positional else None
    output_dir = positional[1] if len(positional) > 1 else DEFAULT_OUTPUT_DIR

    return {
        "source": source,
        "output_dir": output_dir,
        "language": language,
        "whisper_model": whisper_model,
        "top_n": top_n,
        "mode": mode,
    }


ARGS = parse_args(sys.argv)


def is_url(value):
    if not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"}


def find_youtube_urls_in_text(text):
    if not text:
        return []
    pattern = r"https?://(?:www\.)?(?:youtube\.com/watch\?[^)\s]+|youtu\.be/[A-Za-z0-9_-]+[^)\s]*)"
    return re.findall(pattern, text)


def extract_video_id_from_youtube_url(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if "youtu.be" in host:
        return parsed.path.strip("/").split("/")[0] or None
    if "youtube.com" in host:
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live"}:
            return parts[1]
    return None


def canonical_youtube_url(url):
    video_id = extract_video_id_from_youtube_url(url)
    if not video_id:
        return None
    return f"https://www.youtube.com/watch?v={video_id}"


def detect_youtube_url(source_value, transcript):
    if is_url(source_value):
        direct = canonical_youtube_url(source_value)
        if direct:
            return direct

    candidates = []
    if isinstance(transcript, dict):
        text = json.dumps(transcript)
        candidates.extend(find_youtube_urls_in_text(text))
    for candidate in candidates:
        normalized = canonical_youtube_url(candidate)
        if normalized:
            return normalized
    return None


def youtube_timestamp_url(base_url, timestamp_sec):
    normalized = canonical_youtube_url(base_url)
    if not normalized:
        return None
    return f"{normalized}&t={max(0, int(timestamp_sec))}s"


def detect_llm_backend():
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return None


def run(cmd, label, cwd=None):
    started = time.time()
    print(f"[{label}] Starting...")
    print(f"[{label}] Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=False)
    elapsed = time.time() - started
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed after {format_elapsed(elapsed)} with exit code {result.returncode}")
    print(f"[{label}] Complete in {format_elapsed(elapsed)}.")


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def require_binary(name):
    if shutil.which(name) is None:
        raise RuntimeError(f"Missing required binary: {name}")


def skill_script_path(relative_parts):
    here = Path(__file__).resolve().parent
    return str((here.parent / relative_parts).resolve())


def resolve_video_source(source, source_dir):
    ensure_dir(source_dir)
    if is_url(source):
        output_template = str(Path(source_dir) / "source.%(ext)s")
        run(
            [
                "yt-dlp",
                "-f",
                "bestvideo+bestaudio/best",
                "--merge-output-format",
                "mp4",
                "-o",
                output_template,
                source,
            ],
            "Download",
        )
        matches = sorted(Path(source_dir).glob("source.*"))
        media = [p for p in matches if p.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov", ".m4v"}]
        if not media:
            raise RuntimeError("Download step completed but no video file was found.")
        return str(media[0].resolve())

    path = Path(source).expanduser().resolve()
    if not path.exists():
        raise RuntimeError(f"Video not found: {path}")
    copied = Path(source_dir) / path.name
    if copied != path:
        shutil.copy2(path, copied)
    return str(copied.resolve())


def preprocess_audio(video_path, audio_dir):
    ensure_dir(audio_dir)
    output_wav = str((Path(audio_dir) / "source_preprocessed.wav").resolve())
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-acodec",
            "pcm_s16le",
            "-af",
            "highpass=f=80,lowpass=f=8000,loudnorm=I=-16:TP=-1.5:LRA=11",
            output_wav,
        ],
        "Preprocess Audio",
    )
    return output_wav


def run_thumbnail_extraction(video_path, visuals_dir, top_n):
    ensure_dir(visuals_dir)
    script = skill_script_path("thumbnail-extraction/thumbnail_extractor.py")
    run(
        [
            "python3",
            script,
            video_path,
            visuals_dir,
            str(top_n),
            "--extract-slides",
        ],
        "Visual Extraction",
    )


def run_whisper(audio_path, transcript_dir, model, language):
    ensure_dir(transcript_dir)
    run(
        [
            "whisper",
            audio_path,
            "--model",
            model,
            "--language",
            language,
            "--verbose",
            "False",
            "--word_timestamps",
            "True",
            "--condition_on_previous_text",
            "False",
            "--output_format",
            "json",
            "--output_dir",
            transcript_dir,
        ],
        "Transcription",
    )
    json_files = sorted(Path(transcript_dir).glob("*.json"))
    if not json_files:
        raise RuntimeError("Whisper completed but no transcript JSON was found.")
    return str(json_files[0].resolve())


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def find_visual_manifests(visuals_dir):
    visuals = Path(visuals_dir)
    candidate_manifest = next(visuals.glob("*_manifest.json"), None)
    slides_manifest = next((visuals / "slides").glob("*_slides_manifest.json"), None)
    return candidate_manifest, slides_manifest


def build_visual_anchors(visuals_dir):
    candidate_manifest, slides_manifest = find_visual_manifests(visuals_dir)
    anchors = []
    if candidate_manifest and candidate_manifest.exists():
        data = load_json(candidate_manifest)
        for item in data.get("candidates", []):
            files = item.get("files", {})
            image_name = files.get("full")
            if not image_name:
                continue
            anchors.append({
                "timestamp_sec": float(item["timestamp_sec"]),
                "timestamp": item["timestamp"],
                "kind": "keyframe",
                "label": f"Key Frame {item['index']}",
                "image_relpath": str(Path("visuals") / image_name),
            })

    if slides_manifest and slides_manifest.exists():
        data = load_json(slides_manifest)
        for item in data.get("slides", []):
            anchors.append({
                "timestamp_sec": float(item["timestamp_sec"]),
                "timestamp": item["timestamp"],
                "kind": "slide",
                "label": f"Slide {item['index']}",
                "image_relpath": str(Path("visuals") / "slides" / item["file"]),
            })

    anchors.sort(key=lambda x: (x["timestamp_sec"], 0 if x["kind"] == "slide" else 1))

    grouped = []
    for anchor in anchors:
        if grouped and abs(anchor["timestamp_sec"] - grouped[-1]["timestamp_sec"]) < 1.0:
            grouped[-1]["images"].append(anchor)
        else:
            grouped.append({
                "timestamp_sec": anchor["timestamp_sec"],
                "timestamp": anchor["timestamp"],
                "images": [anchor],
            })
    return grouped


def cluster_visual_groups(groups):
    clusters = []
    current = None

    for group in groups:
        only_slides = all(image["kind"] == "slide" for image in group["images"])
        if current is None:
            current = {
                "timestamp_sec": group["timestamp_sec"],
                "timestamp": group["timestamp"],
                "images": list(group["images"]),
                "burst": False,
            }
            continue

        current_only_slides = all(image["kind"] == "slide" for image in current["images"])
        gap = group["timestamp_sec"] - current["images"][-1]["timestamp_sec"]
        span = group["timestamp_sec"] - current["timestamp_sec"]

        if only_slides and current_only_slides and gap <= BURST_GAP_SEC and span <= BURST_MAX_SPAN_SEC:
            current["images"].extend(group["images"])
            current["burst"] = True
        else:
            clusters.append(current)
            current = {
                "timestamp_sec": group["timestamp_sec"],
                "timestamp": group["timestamp"],
                "images": list(group["images"]),
                "burst": False,
            }

    if current is not None:
        clusters.append(current)
    return clusters


def ocr_image_text(image_path):
    try:
        proc = subprocess.run(
            [
                "tesseract",
                image_path,
                "stdout",
                "--psm",
                "6",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            errors="ignore",
            check=False,
        )
        text = " ".join(proc.stdout.split())
        return text[:800]
    except Exception:
        return ""


def enrich_slides_with_ocr(output_dir, groups):
    if shutil.which("tesseract") is None:
        return

    tasks = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        for group in groups:
            for image in group["images"]:
                if image["kind"] != "slide":
                    continue
                image_path = str((Path(output_dir) / image["image_relpath"]).resolve())
                image["image_path"] = image_path
                tasks[executor.submit(ocr_image_text, image_path)] = image

        for future in as_completed(tasks):
            image = tasks[future]
            image["ocr_text"] = future.result()


def transcript_text_only(lines):
    texts = []
    for line in lines:
        parts = line.split("] ", 1)
        texts.append(parts[1] if len(parts) == 2 else line)
    return " ".join(texts).strip()


def unique_slide_context_text(group):
    seen = []
    for image in group["images"]:
        text = " ".join(str(image.get("ocr_text", "")).split()).strip()
        if not text:
            continue
        if any(text == prior for prior in seen):
            continue
        seen.append(text)
    return seen


def heuristic_polish(slide_contexts, transcript_lines):
    summary_bits = []
    if slide_contexts:
        summary_bits.append(f"Slides emphasize: {slide_contexts[0][:180]}")
    if transcript_lines:
        summary_bits.append(f"Speech covers: {transcript_text_only(transcript_lines)[:220]}")
    return " ".join(summary_bits).strip()


def llm_polish(slide_contexts, transcript_lines):
    backend = detect_llm_backend()
    if backend != "openai":
        return heuristic_polish(slide_contexts, transcript_lines)

    api_key = os.environ.get("OPENAI_API_KEY")
    prompt = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Write 1-2 short sentences that connect the nearby slide content with the nearby transcript. "
                            "Be concrete, avoid fluff.\n\n"
                            f"Slide context:\n{chr(10).join(slide_contexts[:3])}\n\n"
                            f"Transcript:\n{chr(10).join(transcript_lines[:8])}"
                        ),
                    }
                ],
            }
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(prompt).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = data.get("output_text", "").strip()
        return text or heuristic_polish(slide_contexts, transcript_lines)
    except Exception:
        return heuristic_polish(slide_contexts, transcript_lines)


def transcript_text_for_window(segments, start_sec, end_sec):
    lines = []
    for seg in segments:
        seg_start = float(seg.get("start", 0.0))
        seg_end = float(seg.get("end", seg_start))
        midpoint = (seg_start + seg_end) / 2.0
        if midpoint < start_sec:
            continue
        if midpoint >= end_sec:
            break
        text = " ".join(str(seg.get("text", "")).split()).strip()
        if text:
            lines.append(f"[{format_ts(seg_start)}] {text}")
    return lines


def render_images_html(group, youtube_url):
    if group["burst"] and len(group["images"]) > 1:
        chunks = []
        for image in group["images"]:
            link = youtube_timestamp_url(youtube_url, image["timestamp_sec"]) if youtube_url else None
            img_html = (
                f'<img src="{image["image_relpath"]}" alt="{image["label"]}" width="{BURST_GRID_IMAGE_WIDTH}" />'
            )
            caption = f'<div><small>{image["label"]} at {image["timestamp"]}</small></div>'
            if link:
                chunks.append(f'<div style="display:inline-block; margin:8px; vertical-align:top;"><a href="{link}">{img_html}</a>{caption}</div>')
            else:
                chunks.append(f'<div style="display:inline-block; margin:8px; vertical-align:top;">{img_html}{caption}</div>')
        return "<div>\n" + "\n".join(chunks) + "\n</div>\n\n"

    parts = []
    for image in group["images"]:
        image_link = youtube_timestamp_url(youtube_url, image["timestamp_sec"]) if youtube_url else None
        label = f"### {image['label']} ({image['kind']})\n\n"
        if image_link:
            image_html = f'<a href="{image_link}"><img src="{image["image_relpath"]}" alt="{image["label"]}" width="{DEFAULT_IMAGE_WIDTH}" /></a>\n\n'
        else:
            image_html = f'<img src="{image["image_relpath"]}" alt="{image["label"]}" width="{DEFAULT_IMAGE_WIDTH}" />\n\n'
        parts.append(label + image_html)
    return "".join(parts)


def write_markdown(output_dir, source_value, video_path, groups, transcript_json_path, mode):
    transcript = load_json(transcript_json_path)
    segments = transcript.get("segments", [])
    total_duration = 0.0
    if segments:
        total_duration = float(segments[-1].get("end", 0.0))
    youtube_url = detect_youtube_url(source_value, transcript)

    md_path = Path(output_dir) / "multimodal_timeline.md"
    rel_video_path = os.path.relpath(video_path, output_dir)
    rel_transcript_path = os.path.relpath(transcript_json_path, output_dir)

    with open(md_path, "w") as f:
        f.write("# Multimodal Timeline\n\n")
        f.write(f"- Source input: `{source_value}`\n")
        f.write(f"- Local video: `{rel_video_path}`\n")
        f.write(f"- Transcript JSON: `{rel_transcript_path}`\n")
        f.write(f"- Mode: `{mode}`\n")
        f.write(f"- Visual anchors: `{len(groups)}`\n\n")
        if youtube_url:
            f.write(f"- YouTube URL: {youtube_url}\n\n")

        for idx, group in enumerate(groups):
            start_sec = 0.0 if idx == 0 else group["timestamp_sec"]
            end_sec = groups[idx + 1]["timestamp_sec"] if idx + 1 < len(groups) else total_duration + 0.01
            if idx == 0:
                start_sec = 0.0

            group_link = youtube_timestamp_url(youtube_url, group["timestamp_sec"]) if youtube_url else None
            if group_link:
                f.write(f"## [{group['timestamp']}]({group_link})\n\n")
            else:
                f.write(f"## {group['timestamp']}\n\n")
            if group["burst"]:
                timestamps = ", ".join(image["timestamp"] for image in group["images"])
                f.write(f"_Rapid slide burst: {timestamps}_\n\n")
            f.write(render_images_html(group, youtube_url))

            lines = transcript_text_for_window(segments, start_sec, end_sec)
            if mode in {"context", "polish"}:
                contexts = unique_slide_context_text(group)
                if contexts:
                    f.write("Slide Context:\n\n")
                    for ctx in contexts[:3]:
                        f.write(f"> {ctx[:240]}\n")
                    f.write("\n")
                if mode == "polish":
                    polished = llm_polish(contexts, lines)
                    if polished:
                        f.write("Section Note:\n\n")
                        f.write(f"{polished}\n\n")
            if lines:
                f.write("Transcript:\n\n")
                for line in lines:
                    f.write(f"- {line}\n")
                f.write("\n")
            else:
                f.write("Transcript:\n\n- No transcript text in this interval.\n\n")

    return str(md_path.resolve())


def main():
    started = time.time()
    source = ARGS["source"]
    if not source:
        print("Usage: python3 multimodal_extract.py <video_or_url> [output_dir] [--mode swift|context|polish] [--language en] [--whisper-model turbo] [--top-n 4]")
        sys.exit(1)
    mode = ARGS["mode"].lower()
    if mode not in {"swift", "context", "polish"}:
        raise RuntimeError(f"Unsupported mode: {ARGS['mode']}")

    require_binary("ffmpeg")
    require_binary("yt-dlp")
    require_binary("whisper")

    output_dir = str(Path(ARGS["output_dir"]).expanduser().resolve())
    source_dir = str(Path(output_dir) / "source")
    visuals_dir = str(Path(output_dir) / "visuals")
    audio_dir = str(Path(output_dir) / "audio")
    transcript_dir = str(Path(output_dir) / "transcript")

    ensure_dir(output_dir)

    print("=== Multimodal Extraction ===")
    print(f"Output dir: {output_dir}")
    print(f"Mode: {mode}")

    video_path = resolve_video_source(source, source_dir)
    run_thumbnail_extraction(video_path, visuals_dir, ARGS["top_n"])
    audio_path = preprocess_audio(video_path, audio_dir)
    transcript_json_path = run_whisper(audio_path, transcript_dir, ARGS["whisper_model"], ARGS["language"])
    groups = cluster_visual_groups(build_visual_anchors(visuals_dir))
    if mode in {"context", "polish"}:
        enrich_slides_with_ocr(output_dir, groups)
    markdown_path = write_markdown(output_dir, source, video_path, groups, transcript_json_path, mode)

    print(f"Markdown: {markdown_path}")
    print(f"Total runtime: {format_elapsed(time.time() - started)}")


if __name__ == "__main__":
    main()
