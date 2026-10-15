"""排名字卡 + 片尾卡生成器（drawtext，1080x1920）。

已在示例项目上验证：TOP10 全部 10 张名卡 + 频道片尾卡一次通过（vision 抽查无截断）。
关键：中文描述必须 wrap(15字/行)，否则左右截断。
输入：items.json = [{"rank":1,"repo":"owner/name","zh":"中文一句话","today":1234,"stars":"5.6万"},...]
（today/stars 为当日真实抓取值，示例数字仅示意格式）
"""
import subprocess, json, os

FF = "/opt/homebrew/Cellar/ffmpeg-full/9.0.1_1/bin/ffmpeg"  # ← 改成你的 ffmpeg-full 全路径
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
OUT = os.path.expanduser("~/hermes-videos/demo/shots")  # ← 改成你的输出目录

def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\\\'").replace("%", "\\%")

def wrap(s, n=15):
    return [s[i:i + n] for i in range(0, len(s), n)][:3]

def card(items):
    for it in items:
        rank, repo = it["rank"], it["repo"]
        y = 430
        vf = [
            f"drawtext=fontfile='{FONT}':text='NO.{rank}':fontcolor=0xffd700:fontsize=190:borderw=6:bordercolor=black@0.9:x=90:y={y}",
            f"drawtext=fontfile='{FONT}':text='{esc(repo)}':fontcolor=white:fontsize=50:borderw=5:bordercolor=black@0.9:x=(w-text_w)/2:y={y+270}",
        ]
        dy = y + 390
        for seg in wrap(it["zh"], 15):
            vf.append(f"drawtext=fontfile='{FONT}':text='{esc(seg)}':fontcolor=0xe6edf3:fontsize=44:borderw=5:bordercolor=black@0.9:x=(w-text_w)/2:y={dy}")
            dy += 66
        vf.append(f"drawtext=fontfile='{FONT}':text='今日 +{it['today']:,} 星 · 总星 {esc(str(it['stars']))}'"
                  f":fontcolor=0xffb13b:fontsize=48:borderw=5:bordercolor=black@0.9:x=(w-text_w)/2:y={dy+60}")
        out = os.path.join(OUT, f"card{rank:02d}.png")
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                        "-i", "color=c=0x0d1117:s=1080x1920:d=1", "-frames:v", "1",
                        "-vf", ",".join(vf), "-y", out], check=True)
        print(f"card{rank:02d}.png OK", repo)

def outro_channel(channel_name, tagline):
    """频道片尾卡模板 — 传入你自己的频道名与一句话定位"""
    vf = [
        f"drawtext=fontfile='{FONT}':text='{esc(channel_name)}':fontcolor=white:fontsize=150:borderw=6:bordercolor=black@0.9:x=(w-text_w)/2:y=700",
        f"drawtext=fontfile='{FONT}':text='{esc(tagline)}':fontcolor=0x58a6ff:fontsize=56:borderw=5:bordercolor=black@0.9:x=(w-text_w)/2:y=940",
        f"drawtext=fontfile='{FONT}':text='关注我 · 明天继续':fontcolor=0x8b949e:fontsize=44:x=(w-text_w)/2:y=1100",
    ]
    out = os.path.join(OUT, "outro.png")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                    "-i", "color=c=0x091120:s=1080x1920:d=1", "-frames:v", "1",
                    "-vf", ",".join(vf), "-y", out], check=True)
    print("outro.png OK")

if __name__ == "__main__":
    card(json.load(open(f"{OUT}/../top10_full.json"))["items"])
    # 示例：outro_channel("你的频道名", "一句话频道定位")
