#!/usr/bin/env python3
"""终端实拍风格证据图生成器（公众号「证据图」专用）。
用法：复制本文件，改 LINES 数据直接跑 python3 make_shots.py。
每张图 = macOS 窗框 + One Dark 配色 + 分段定位文本，1200x675。
铁律：
- 含中文的行必须用 STHeiti（Menlo 无中文字形 → 豆腐块）——脚本自动检测
- 每张图出完后必须用视觉模型抽查验字
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = "/tmp/demo-shots"
os.makedirs(OUT, exist_ok=True)
FONT_CJK = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_MONO = "/System/Library/Fonts/Menlo.ttc"
W, H = 1200, 675
BG, BAR, LINE = "#1b1d23", "#2a2d35", "#0d1117"
GREEN, WHITE, GREY, RED, GOLD, BLUE = "#98c379", "#e6edf3", "#7f8794", "#e06c75", "#e5c07b", "#61afef"

_fc = {}
def F(size, mono):
    key = (size, mono)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(FONT_MONO if mono else FONT_CJK, size)
    return _fc[key]

def has_cjk(t):
    return any('\u2e80' <= ch <= '\u9fff' or ch in '，。：；「」（）｜→·⏳％' for ch in t)

def shot(name, lines, title="dev — zsh"):
    """lines: [(text, hexcolor, fontsize, mono_bool)]；空行用 ("", color, size, True) 占位"""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 44], fill=BAR)
    d.ellipse([24, 15, 36, 27], fill="#ff5f57"); d.ellipse([44, 15, 56, 27], fill="#febc2e"); d.ellipse([64, 15, 76, 27], fill="#28c840")
    tw = d.textlength(title, font=F(16, False))
    d.text(((W - tw) / 2, 13), title, font=F(16, False), fill="#8b90a0")
    d.rectangle([0, 44, W, 46], fill=LINE)
    y = 78
    for text, color, size, mono in lines:
        if text:
            font = F(size, mono and not has_cjk(text))
            d.text((56, y), text, font=font, fill=color)
        y += int(size * 1.75)
    img.save(f"{OUT}/{name}.png")
    print(name, "OK")

if __name__ == "__main__":
    # ── 示例：改下面 LINES 为你的真实输出 ──
    shot("demo_terminal_output", [
        ("$ bash repro.sh", WHITE, 22, True),
        ("期望 8000, 实际 1064", RED, 26, True),
        ("BUG: 丢失 6936 次打点", RED, 32, True),
        ("", WHITE, 14, True),
        ("E1 已入库 → 必现：并发打点大量丢失", GREEN, 21, False),
    ], title="demo-app — 取证")
    print("改 LINES 后重跑；出图后用视觉模型抽查", len(os.listdir(OUT)), "张")

# 本技能由真实账号产线脱敏而来，方法论已验证，平台规则可能随改版失效，欢迎 issue 反馈。
