# ffmpeg 视频/滤镜已验证语法（本机 ffmpeg-full 9.0.1）

全路径调用：`/opt/homebrew/Cellar/ffmpeg-full/<ver>/bin/ffmpeg`（brew 主公式无 drawtext；ffmpeg-full 装完不会切换 PATH）

## 静帧→动效视频（Ken Burns）
```.filter
# 超采样 2.5x 后 zoompan，避免直推静帧的抖动
[0:v]scale=2700:4800:flags=lanczos,setsar=1,zoompan=z='min(zoom+0.0004,1.10)':x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':d=447:s=1080x1920:fps=30[v0]
```
- `d=帧数` = 该片段输出帧数；横移用 x 表达式 `(iw-iw/zoom)*0.25`（0~1 从左到右）
- 片段间叠化：`[vA][vB]xfade=transition=fade:duration=0.8:offset=<前段累计-0.8>[x]`，链式多段依次推
- 非重叠拼接：`concat=n=N:v=1:a=0`

## 单帧陷阱（最贵的一课）
字幕 drawtext 链若直接挂静帧输入（不经 zoompan/concat），输出只剩 3 帧、时长 0.1s。
正确架构：所有图片→zoompan→xfade/concat→`[vbg]`；字幕链叠 `[vbg]`；同链末尾 `format=yuv420p[vout]`；`-map [vout] -map [aout]`。

## drawtext 中文大字幕
```
drawtext=fontfile='/System/Library/Fonts/STHeiti Medium.ttc':text='…':fontcolor=white:fontsize=58:borderw=5:bordercolor=black@0.85:x=(w-text_w)/2:y=1500:enable='between(t,5.00,9.20)'
```
- 转义：`\:` `\'` `\\` `%`；中文描述一行超 ~17 字（fontsize 52-58）必截断 → 先 wrap 成多行，行高 ≈ fontsize+8
- ffmpeg 9 的 tile 无 `each_frame` 选项；`-vsync` 已删 → `-fps_mode vfr`

## 多段配音时间轴拼接
```
adelay=500|5002|13512:all=1,amix=inputs=N:normalize=0,apad=whole_dur=<TOTAL>
```
- 分隔符是竖线 `|`；逗号/加号直接报 "No option name near"
- `normalize=0` 必加，否则音量被均分压低
- 对轴：LEAD=0.5 起，GAP=0.35 句间，starts 累加；每次改文案重算
- 字幕窗口 = [start+0.02, start+dur-0.02]

## 验证命令（成片后必跑）
```bash
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_type,nb_frames out.mp4
ffmpeg -i out.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
# 抽帧拼图（帧号=秒*30）
ffmpeg -i out.mp4 -vf "select='eq(n\,60)+eq(n\,480)',scale=360:640,tile=2x2" -fps_mode vfr -frames:v 1 check.png
```
标准：音画 duration 相等；max_volume −3~−6dB；抽查帧字幕完整、画面类型正确。

## 探测
```bash
ffmpeg -hide_banner -filters | grep -E "\b(drawtext|subtitles|zoompan|xfade)\b"
```

> 本技能由真实账号产线脱敏而来，方法论已验证，依赖 ffmpeg/edge-tts，版本更新可能影响参数，欢迎 issue 反馈。
