# 素材采集：Trending 榜单页解析 / 竖屏截图 / 微信视频号下载

## Trending 榜单页 → TOP N 数据
1. `web_extract("https://github.com/trending?since=daily")` — 全文自动落盘缓存目录
2. 行式解析（勿用单正则一把梭，markdown 结构是多行块）：
   - repo 行：`^## \[([^\]]+)\]\((https://github\.com/[^)]+)\)`，名字带 `/\ \` 转义垃圾 → `re.sub(r"\s*/\\+\s*", "/", name)`
   - 星/fork 行：`[stars](…/stargazers) [forks](…/forks)`
   - 涨星行：裸文本 `^([\d,]+) stars today`（无方括号！），**它同时是条目结束哨兵**
   - 状态机：见 repo 开新条目 → 收 desc/stars → 见 "stars today" 收尾入库
3. 按 today 降序取 TOP N；日期用 `date "+%Y-%m-%d %A"` 确认
4. 描述缺失时回 `sed -n` 看原文块补齐

## 浏览器竖屏截图（browser_exec）
```python
ensure_real_tab()
goto_url("https://github.com/OWNER/REPO")
wait_for_load(); import time; time.sleep(2.2)
cdp('Emulation.setDeviceMetricsOverride', width=1080, height=1920, deviceScaleFactor=1, mobile=False)
time.sleep(1.2)
import base64, os
r = cdp('Page.captureScreenshot', format='png')
open(out, 'wb').write(base64.b64decode(r['data']))
```
- 截图落在 harness 工作区（结果里 `workspace` 路径），不是当前 shell cwd —— 合成前先 `cp` 过去
- 会话卡死（IPC timeout）→ `ensure_real_tab()` 恢复再重试

## 微信视频号（channels.weixin.qq.com）素材下载
分享页纯 JS 渲染，web_extract 恒为空。用 browser_exec：
1. `new_tab(url)` + sleep 5 → `document.body.innerText` 即全部文案/作者/互动数
2. 视频：`document.querySelector('video').src`（finder.video.qq.com，长 URL）
3. 下载必须带 `Referer: https://channels.weixin.qq.com/`，否则被拒
4. 验证：`file` 应为 ISO Media MP4，`ffprobe` duration 与页面 player 一致

## 数据新鲜度铁律
文案引用的星数/涨星必须来自本次抓取。实测教训：热门仓库几天就涨几千星，沿用旧数字=数据造假。

> 本技能由真实账号产线脱敏而来，方法论已验证，依赖 ffmpeg/edge-tts，版本更新可能影响参数，欢迎 issue 反馈。
