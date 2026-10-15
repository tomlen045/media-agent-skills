# ffmpeg drawtext/lavfi 排雷表（出图/出片滤镜串炸掉时按此查）

> 本文为通用技术事实，无账号相关信息。脱敏声明见文末。

按命中率排序。每条：症状 → 原因 → 正确写法。

1. **text 含 `%`** → `Invalid argument` → 转义要**双反斜杠** `\\%`（单 `\%` 不够；或用全角 ％，或换 PIL 渲染）
2. **`-lavfi` 复杂图 与 `-vf` 简单链 混用** → "Simple and complex filtering cannot be used together" → 渐变底图用 `-f lavfi -i gradients=...` 当普通输入，drawtext 全走 `-vf`
3. **`-filter_complex` 末尾接 `[v]nullsink` 再 `-map [v]`** → "label does not exist"（nullsink 把标签消费掉）→ 静态单图直接走第 2 条的 `-f lavfi -i` + `-vf`，不要 filter_complex
4. **fontfile 路径含空格**（STHeiti Medium.ttc）→ 滤镜解析断裂/参数被拆 → 路径空格转义 `STHeiti\ Medium.ttc`，或换 PIL
5. **zoompan 配 `-loop 1 -t` 输入** → 总时长膨胀数十倍（每输入帧 × d 帧展开）→ 单帧输入（去掉 -loop/-t），时长全靠 zoompan `d=帧数`
6. **纯 Python 渲染替代**：中文多/转义排不掉时，PIL（ImageDraw + STHeiti/Menlo truetype）无任何转义问题，同规格出 PNG——老 PIL（<10）对空文本行/元组 fill 会炸，传参前校验类型

> 本技能由真实账号产线脱敏而来，方法论已验证，平台规则可能随改版失效，欢迎 issue 反馈。
