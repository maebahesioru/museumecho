"""Assemble the MuseumEcho demo video with a real audio track.

Pipeline:
 1. Generate narration segments via the app's own TTS endpoint (meta!).
 2. Place narration + the app's actual audio clips (answer / feedback / brief)
    at the timestamps recorded in demo/marks.json.
 3. Mix into one track, add the title/end cards, burn English subtitles.
"""
import json
import subprocess
import sys
from pathlib import Path

import urllib.request

ROOT = Path(__file__).parent.parent
DEMO = ROOT / "demo"
FFMPEG = "/home/maebahesioru/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
FFPROBE = "/home/maebahesioru/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffprobe"
FONT = "/usr/share/fonts/noto/NotoSans-Regular.ttf"
API = "http://127.0.0.1:7866"


def tts(text: str, out: Path) -> None:
    req = urllib.request.Request(
        f"{API}/api/tts",
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    url = d["audio_url"]
    with urllib.request.urlopen(f"{API}{url}", timeout=120) as r:
        out.write_bytes(r.read())
    print("tts:", out.name, len(out.read_bytes()) // 1024, "KB")


def dur(p: Path) -> float:
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def main() -> None:
    marks = {m["name"]: m["t"] for m in json.loads((DEMO / "marks.json").read_text())}
    print("marks:", marks)
    audio_dir = ROOT / "data" / "audio"
    seg_dir = DEMO / "segments"
    seg_dir.mkdir(exist_ok=True)

    # 1) narration segments (start time, text)
    segs = [
        (0, "MuseumEcho. The audio guide that knows your museum, because it is built from the museum's own guide. Visitors ask in plain language, and every answer is cited, spoken, and honest about what it does not know."),
        (marks.get("uploaded", 10) - 2, "Load the museum guide. Every exhibit keeps its exact source."),
        (marks.get("browsed", 25) - 4, "Or browse every gallery and exhibit."),
        (marks.get("ask1", 60) - 30, "Ask for a thirty minute route, and get the museum's own suggested route, read aloud, with citations."),
        (marks.get("ask2", 100) - 25, "Ask what is good for kids, or where the cafe is."),
        (marks.get("refused", 150) - 5, "Ask something the guide does not cover, and MuseumEcho declines. It never invents exhibits, hours, or prices."),
        (marks.get("end", 180) - 8, "MuseumEcho. Every museum's guide, speaking for itself."),
    ]

    # generate narration files
    narr_files = []
    for i, (start, text) in enumerate(segs):
        f = seg_dir / f"narr_{i:02d}.mp3"
        if not f.exists():
            tts(text, f)
        narr_files.append((start, f))

    # 2) app audio clips (find the newest mp3s = the ones the demo produced)
    app_clips = []
    if audio_dir.exists():
        files = sorted(audio_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime)
        # MuseumEcho flow: question-audio clip + answer clip
        if files:
            app_clips.append((marks.get("food_answered", 60) + 2, files[-1]))
            if len(files) >= 2:
                app_clips.append((marks.get("shelter_answered", 100) + 2, files[-2]))

    # 3) build the mix
    inputs = []
    filters = []
    idx = 0
    for start, f in narr_files + app_clips:
        inputs += ["-i", str(f)]
        delay = int(start * 1000)
        filters.append(f"[{idx}:a]adelay={delay}|{delay},volume=1.0[a{idx}]")
        idx += 1
    mix_in = "".join(f"[a{i}]" for i in range(idx))
    filters.append(f"{mix_in}amix=inputs={idx}:normalize=0[mix]")
    track = DEMO / "audiotrack.m4a"
    cmd = [FFMPEG, "-y"] + inputs + ["-filter_complex", ";".join(filters), "-map", "[mix]",
                                     "-c:a", "aac", "-b:a", "160k", str(track)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        sys.exit(1)
    print("audio track:", dur(track), "s")

    # 4) video + audio + subtitles + cards
    raw = next(DEMO.glob("video/*.webm"))
    title_png = DEMO / "title.png"
    end_png = DEMO / "end.png"
    for png, t1, t2 in [
        (title_png, "MuseumEcho", "understand your medical documents safely"),
        (end_png, "github.com/maebahesioru/echoscholar", "Every answer can be heard. Nothing is invented."),
    ]:
        subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "color=c=0x0b0d12:s=1280x800:d=1", "-frames:v", "1",
                        "-vf", (f"drawtext=fontfile={FONT}:text='{t1}':fontsize=58:fontcolor=white:x=(w-text_w)/2:y=320,"
                                f"drawtext=fontfile={FONT}:text='{t2}':fontsize=28:fontcolor=0x4f8cff:x=(w-text_w)/2:y=420"),
                        str(png)], capture_output=True)

    title_mp4 = DEMO / "title.mp4"
    end_mp4 = DEMO / "end.mp4"
    for png, out, t in [(title_png, title_mp4, "5"), (end_png, end_mp4, "6")]:
        subprocess.run([FFMPEG, "-y", "-loop", "1", "-i", str(png), "-t", t, "-r", "30",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)], capture_output=True)

    # main video: webm -> mp4 with the audio track
    main_mp4 = DEMO / "demo_main.mp4"
    subprocess.run([FFMPEG, "-y", "-i", str(raw), "-i", str(track),
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(main_mp4)], capture_output=True)
    print("main:", dur(main_mp4), "s")

    # concat: title (silent) + main + end (silent)
    silent1 = DEMO / "silence5.m4a"
    silent2 = DEMO / "silence6.m4a"
    for out, t in [(silent1, "5"), (silent2, "6")]:
        subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", t,
                        "-c:a", "aac", str(out)], capture_output=True)
    t2 = DEMO / "title_a.mp4"
    e2 = DEMO / "end_a.mp4"
    subprocess.run([FFMPEG, "-y", "-i", str(title_mp4), "-i", str(silent1), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-shortest", str(t2)], capture_output=True)
    subprocess.run([FFMPEG, "-y", "-i", str(end_mp4), "-i", str(silent2), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-shortest", str(e2)], capture_output=True)

    concat = DEMO / "concat.txt"
    concat.write_text(f"file '{t2}'\nfile '{main_mp4}'\nfile '{e2}'\n")
    final = DEMO / "echoscholar_demo.mp4"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(final)],
                   capture_output=True)
    print("FINAL:", final, dur(final), "s")


if __name__ == "__main__":
    main()
