#!/usr/bin/env python3
# 公众号封面生成模板 900x383 (2.35:1) — 复制本文件, 改 OUT 与 LINES 文案坐标, 直接运行
# 依赖: ffmpeg-full (brew install ffmpeg-full; 版本号变了用 ls /opt/homebrew/Cellar/ffmpeg-full 确认)
# 中文字体: STHeiti Medium.ttc (macOS 自带)
# ⚠️ 出图后必须用视觉模型验字(截断/重叠/超边/左右平衡), 验过才算完成
# ⚠️ drawtext 无自动换行: 多段文字分段放坐标; 长文案超右边缘会截断, 先估算宽度
import glob
import subprocess
import os
import sys

FF = sorted(glob.glob("/opt/homebrew/Cellar/ffmpeg-full/*/bin/ffmpeg"))[-1]
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
OUT = os.path.expanduser("~/Desktop/cover_new.png")

# 品牌色板: 渐变 #0b0e1a→#1a0f2e · 金 #f0b429 · 警示红 #f85149 · 正文白 · 次级灰 #8b949e
# LINES 每项: (text, x, y, fontsize, color, box_alpha或None)
# 垂直预算参考(383px): 标签y40 / 主行y96·y172 / 右侧数据y92起 / 底部y266·y322
LINES = [
    ("账号名 · 栏目标签", 48, 40, 24, "0xf0b429", None),
    ("主钩子第一行", 48, 96, 58, "white", None),
    ("主钩子第二行", 48, 172, 58, "white", None),
    ("5700★", 620, 92, 62, "0xf0b429", None),
    ("副信息一行", 650, 178, 30, "white", None),
    ("红色重点行(带黑衬底)", 48, 266, 27, "0xf85149", 0.30),
    ("底部信息行", 48, 322, 21, "0x8b949e", None),
]


def dt(text, x, y, size, color, box):
    esc = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\\\\\'")
    s = "drawtext=fontfile={}:text='{}':fontcolor={}:x={}:y={}:fontsize={}".format(
        FONT, esc, color, x, y, size)
    if box is not None:
        s += ":box=1:boxcolor=black@{}:boxborderw=10".format(box)
    return s


def main():
    bg = "gradients=s=900x383:c0=0x0b0e1a:c1=0x1a0f2e:x0=0:y0=0:x1=900:y1=383:d=1"
    # 金竖条锚住主标题左侧; 高度按主行范围调整
    vf = ["drawbox=x=34:y=96:w=5:h=130:color=0xf0b429@0.9:t=fill"]
    vf += [dt(*ln) for ln in LINES]
    # 结构铁律: 渐变用 -f lavfi 当普通输入, 文字走 -vf 简单链
    # (勿用 -lavfi 复杂图与 -vf 混用; -filter_complex 末尾接 [label]nullsink 会消费标签致 map 失败)
    cmd = [FF, "-y", "-f", "lavfi", "-i", bg,
           "-vf", ",".join(vf), "-frames:v", "1", OUT]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG FAILED:\n", r.stderr[-1200:])
        sys.exit(1)
    print("OK:", OUT, os.path.getsize(OUT), "bytes")
    print("下一步: 用视觉模型验字, 叠字/超边改 LINES 坐标重跑")


if __name__ == "__main__":
    main()

# 本技能由真实账号产线脱敏而来，方法论已验证，平台规则可能随改版失效，欢迎 issue 反馈。
