"""生成口播短视频的 ffmpeg filtergraph（图片动效 + 配音对轴 + 换行字幕）。

已在示例项目上验证：TOP10 视频 91.7s / 23 片段 / 34 字幕行一次通过。
复用步骤：
1. 准备 script.txt（一句一行）与逐句配音 seg 目录（s_01.mp3...）
2. 修改 PIECES 段落表（类型 still_card=卡片缓推 / still_photo=照片漂移）
3. python3 build_graph.py → graph.txt；再用 assemble 脚本（python subprocess 传参）执行
"""
import subprocess, json, os

FF = "/opt/homebrew/Cellar/ffmpeg-full/9.0.1_1/bin/ffmpeg"  # ← 改成你的 ffmpeg-full 全路径
DEMO = os.path.expanduser("~/hermes-videos/demo")  # ← 改成你的工作目录
AUD = f"{DEMO}/top10_audio"                        # ← 配音目录
FPS = 30
GAP = 0.35
LEAD = 0.5
N_SEG = 13                                         # ← 旁白段数

def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(r.stdout.strip())

durs = [dur(f"{AUD}/s_{i:02d}.mp3") for i in range(1, N_SEG + 1)]
starts, t = [], LEAD
for d in durs:
    starts.append(t)
    t += d + GAP
TOTAL = starts[-1] + durs[-1] + 2.0

def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\\\'").replace("%", "\\%")

def wrap(s, n=17):
    return [s[i:i + n] for i in range(0, len(s), n)]

# ── 片段表：每个 (类型, 路径, 开始, 结束)。示例为 TOP10 结构，按需改 ──
pieces = [("still_card", f"{DEMO}/shots/intro.png", 0.0, starts[1])]
for k in range(1, 11):
    s = starts[k]
    e = starts[k + 1] if k < 10 else starts[11]
    pieces.append(("still_card", f"{DEMO}/shots/card{k:02d}.png", s, s + 0.8))
    pieces.append(("still_photo", f"{DEMO}/shots/t{k:02d}.png", s + 0.8, e))
pieces.append(("still_card", f"{DEMO}/shots/opinion.png", starts[11], starts[12]))
pieces.append(("still_card", f"{DEMO}/shots/outro.png", starts[12], TOTAL))

lines = []
for i, (typ, path, s, e) in enumerate(pieces):
    frames = max(2, round((e - s) * FPS))
    if typ == "still_photo":
        pre, zb = "scale=2430:4320:flags=lanczos", "min(zoom+0.00030,1.08)"
        pan = "iw/2-(iw/zoom)/2" if i % 2 == 0 else "(iw-iw/zoom)/2"
    else:
        pre, zb = "scale=1620:2880:flags=lanczos", "min(zoom+0.00025,1.05)"
        pan = "iw/2-(iw/zoom)/2"
    lines.append(f"[{i}:v]{pre},setsar=1,zoompan=z='{zb}':x='{pan}'"
                 f":y='ih/2-(ih/zoom)/2':d={frames}:s=1080x1920:fps={FPS}[p{i}]")
lines.append("".join(f"[p{i}]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=1:a=0[vbg]")

# ── 字幕：script.txt 每行一段，wrap 后逐行 drawtext 对轴 ──
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
script_lines = [l for l in open(f"{DEMO}/script.txt", encoding="utf-8").read().splitlines() if l.strip()]
dt = []
for i, text in enumerate(script_lines):
    w0, w1 = starts[i] + 0.02, starts[i] + durs[i] - 0.02
    segs = wrap(text, 17)
    lh = 64
    y_base = 1560 - (len(segs) - 1) * lh
    for j, segtxt in enumerate(segs):
        dt.append(f"drawtext=fontfile='{FONT}':text='{esc(segtxt)}':fontcolor=white:fontsize=52"
                  f":borderw=5:bordercolor=black@0.88:x=(w-text_w)/2:y={y_base + j * lh}"
                  f":enable='between(t,{w0:.2f},{w1:.2f})'")
lines.append("[vbg]" + ",".join(dt) + ",format=yuv420p[vout]")

# ── 音频：adelay 竖线语法 + normalize=0 ──
delays = "|".join(f"{int(s * 1000)}" for s in starts)
lines.append(f"[{len(pieces)}:a]aformat=sample_rates=44100:channel_layouts=mono,"
             f"adelay={delays}:all=1,apad=whole_dur={TOTAL:.3f}[aout]")

open(f"{DEMO}/graph.txt", "w").write(";\n".join(lines))
json.dump({"total": TOTAL, "starts": starts, "durs": durs},
          open(f"{DEMO}/timeline.json", "w"), indent=1)
print(f"pieces={len(pieces)} total={TOTAL:.1f}s sub_lines={len(dt)} → graph.txt")
