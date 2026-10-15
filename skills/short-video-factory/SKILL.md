---
name: short-video-factory
description: "Use when 用户要制作或复刻口播短视频(盘点/榜单类): TTS配音+素材+ffmpeg合成+实帧验证全自动出片。"
version: 1.0.0
author: tomlen045
license: MIT
tags: [video, ffmpeg, tts, short-video, 视频号, automation]
---

# Short Video Factory — 口播短视频自动生产线

从选题到成片全自动化。该方法论已在真实任务中端到端验证：开源项目每日涨星 TOP10 榜单盘点类视频（示例成片 91.7s，1080x1920，含排名字卡/页面实拍 Ken Burns/逐句对轴字幕/片尾卡）。

## 触发场景
- "帮我做个视频作品 / 模仿这类口播视频 / 出一条 TOP 榜盘点"
- 每日定时产视频（cron + 数据源 trending 页）
- 已有成品换文案/配音/片尾再出一版

## 频道固定格式（示例配置）— 改动需账号所有者确认
- **片尾卡（必须）**：大字频道名 + 蓝字一句话定位 + 灰字「关注我 · 明天继续」（模板 `templates/make_cards.py` 的 outro 函数可改文案）
- 配音：`uvx edge-tts --voice zh-CN-YunjianNeural --rate=+8%`（男声解说风）；逐句生成，一句一个 mp3
- 规格：1080x1920@30fps，H.264 crf19；名卡深底 `0x0d1117` + 金色 NO.X `0xffd700`
- 字体：`/System/Library/Fonts/STHeiti Medium.ttc`（新 macOS 无顶层 PingFang.ttc）
- **铁律**：榜单数字必须当日真实抓取（总星/今日涨星），禁止沿用旧视频里的过期数字

## Pipeline（每步都有已验证实现）
1. **数据**：抓目标 trending/榜单页，按"今日涨星"排序取 TOP N → `references/footage-capture.md`
2. **文案**：一句一行 `script.txt`（每行=一段配音+一条字幕）；结构=开头钩子→逐条盘点→一句观点→片尾CTA
3. **配音**：循环 edge-tts → `s_01.mp3...`；`ffprobe` 逐段测时长
4. **时间轴**：LEAD=0.5s 起播，GAP=0.35s 句间；starts 累加；TOTAL=末段止+2.0s
5. **名卡**：drawtext 生成 NO.X 排名卡；中文描述必须 wrap（15字/行），否则左右截断 → `templates/make_cards.py`
6. **实拍素材**：CDP 设 1080x1920 视口逐页面截图 → `references/footage-capture.md`
7. **合成**：`templates/build_graph.py` 生成 filtergraph → python subprocess 出 mp4
8. **验证（必做，缺一步都不算完成）**：
   - ffprobe：视频帧数 ≈ TOTAL*30，音画 duration 相等
   - volumedetect：max_volume 在 -3~-6dB（无削波、非静音）
   - 抽 8 帧按 eq(n,帧号)+tile 2x2 拼图 → vision_analyze 查字幕截断/黑屏/画面错位

## Pitfalls（全部真实踩过，每条都花过真实调试时间）
- **单帧陷阱**：drawtext 链直接挂静帧 PNG 输入 → 产出只有 3 帧的视频。正确架构：静帧先 zoompan 造动效 → xfade/concat 成 `[vbg]` → 字幕链叠 `[vbg]`，同一条链到底后 `format=yuv420p`
- Homebrew `ffmpeg` 主公式（8.x/9.x）**没有 drawtext/subtitles**；`brew install ffmpeg-full` 后必须用 Cellar 全路径 `/opt/homebrew/Cellar/ffmpeg-full/<ver>/bin/ffmpeg`（brew link 不切换 PATH）
- adelay 多输入延迟：`adelay=t1|t2|...:all=1`（竖线分隔）；用 `+` 或 `,` 直接报 "No option name near"
- ffmpeg 9：`-vsync` 已删除 → `-fps_mode vfr`；`tile` 滤镜无 `each_frame` 选项
- zsh 不做变量分词：`ffmpeg ... $INPUTS` 整串变成一个参数 → 一律 python subprocess 数组传参
- terminal 里跑 `python3 <<HEREDOC` 会触发权限审批并卡死超时（两次实测）→ write_file 落盘后 `python3 file.py`
- zoompan 直推原尺寸静帧会抖 → 先 scale 到 ~2.5x 超采样（如 2700x4800）再 zoompan
- xfade offset = 该转场点前累计时长 − 淡化时长(0.8)；链式多次依次推算
- amix 必须 `normalize=0`，否则多段配音音量被压低
- 长合成（>60s 视频）放后台执行并等完成通知，前台 600s 上限会砍任务

## Files
- `references/ffmpeg-video-quirks.md` — 已验证的滤镜语法与参数全集
- `references/footage-capture.md` — trending 解析 / 浏览器竖屏截图 / 微信视频号素材下载
- `templates/build_graph.py` — filtergraph 生成器（改片段表即可复用）
- `templates/make_cards.py` — 排名字卡生成器（读 items json）

> 本技能由真实账号产线脱敏而来，方法论已验证，依赖 ffmpeg/edge-tts，版本更新可能影响参数，欢迎 issue 反馈。
