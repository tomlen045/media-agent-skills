---
name: creator-analytics
description: "Use when 抖音作品数据复盘/爆款归因/用户画像. 采集创作者中心数据并产出迭代动作。"
version: 1.0.0
author: tomlen045
license: MIT
tags: [douyin, 数据分析, 创作者中心, 爆款复盘]
---

# 抖音创作者中心数据复盘

## When to Use

用户丢来 creator.douyin.com 的作品链接并要求"深度分析用户画像 / 复盘 / 爆款归因 / 继续自研爆款"时触发。产出物 = 数据全景 → 用户画像结论 → 可执行迭代动作清单。发布与图文制作规格属于发布产线技能的职责范围，本技能只管数据采集与决策。

## 登录态浏览器(前置, 坑最多)

数据页必须带登录态; 用户 Chrome 开着会锁 profile。按序执行:

1. 检测: `ps aux | grep "Google Chrome" | grep -v grep | grep -v Helper`。
2. 优雅退出: `osascript -e 'tell application "Google Chrome" to quit'`(会话保留)。**禁用批量 kill -9/全量 pkill**: 审批无人批会卡死整轮对话。Agent 框架还可能自动把用户 Chrome 拉起来再次抢锁——所以优先走副本方案而不是反复退用户 Chrome。
3. 副本方案: rsync 复制 `~/Library/Application Support/Google/Chrome/Default/` 到缓存目录(排除 Cache / Code Cache / Service Worker / GPUCache / *ShaderCache / Crashpad, 百 MB 秒级), 再 `open -na "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir=<副本> --no-first-run --no-default-browser-check "<作品URL>"`, `curl -s http://127.0.0.1:9222/json/version` 确认端口活了。
4. 把 Agent 的浏览器 CDP 地址设为 `http://127.0.0.1:9222` 接管(每次浏览器调用重新读配置, 不用重启会话)。**同机同用户下 cookie 加密密钥可用, sessionid 随副本完整可用**。收工后把 CDP 配置还原为空。
5. 副本首次渲染出登录墙先别重建: 用 sqlite 查副本 Cookies 库 `host_key like '%creator.douyin%'` 有 `sessionid` 即登录态在, 刷新或重进 URL 即过。

## 采集流程(一次调用采多个 tab)

- 文本提取主力: `document.body.innerText` — 比截图全、可 diff、不依赖渲染位置。
- 切 tab: `[...document.querySelectorAll("div,span")].filter(e=>e.textContent.trim()==="流量分析"&&e.children.length<=1)`, 取 `els[els.length-1].click()`, sleep 3s 再取 innerText。作品详情页五个 tab: 总览 / 流量分析 / 观众分析 / 评论热词 / 评论管理。
- **总览页「作品诊断」的"播放量较往期+N%"是爆款归因核心数字**; 流量分析页给划走率/平均浏览图片数/各互动率"比往期±%"; 评论管理给评论原文(唯一评论=最贵的需求数据)。
- 截图: 带窗口 Chrome 下常规截图可能不落盘——用 CDP 的 `Page.captureScreenshot`(format=png, captureBeyondViewport=true) 写 base64 到文件, 再交给视觉模型分析本地路径。
- SPA 导航: 作品详情页直接 `location.href=完整URL` 可达; **列表/工作台页整页加载常渲染空白区**, 点侧边栏文字("内容管理")最可靠。URL 必须写全 `creator.douyin.com` — host 写错(如 creator.com)会被拦成"内网地址"。
- 基线对照: 内容管理列表首屏(约 12 条)每条自带 播放/划走率/平均浏览图片数, 直接 innerText 解析即可; 列表懒加载是容器内滚动, `window.scrollTo` 不触发加载。
- 小账号(<1000 粉)观众分析的地域/年龄/热词全是"暂无数据", 别承诺人群画像 — 画像从行为指标反推。

## 指标解读决策表(每次必用)

- 收藏/分享/评论率 ↑ 而点赞率 ↓ = 工具型内容被当"弹药"收藏转发, 点赞降不是失败信号; 汇报时两者分开讲。
- 平均浏览图片数 ≈2/3 = **P1 一张图扛全部转化, P2/P3 视同不存在**; 仓库入口要进 P1 本体和置顶评论, 不能只放在尾页。
- 粉丝播放占比 <1% 且推荐页来源 >95% = 无粉丝基本盘, 爆款是算法单点选中(同批兄弟作品可能 0-3 播放); 爆款不复利, 持续出新才是收入来源。
- 播放量高而 GitHub stars=0 = 种草→仓库转化断裂: 发布后立即评论区置顶仓库直达链接, 下条作品 P1 带口语化 clone 命令。
- 唯一的评论/评论热词 = 最高优先级迭代输入: 尽快修复 → 本地实测(起服务 curl API 看新字段生效) → 推送 GitHub → 下条图文官宣"评论区老哥要的已上线"(修用户关系+得内容素材, 一鱼两吃)。
- 校验/计数口径必须全链路统一: 前端提示、后端限制、结果展示三处同一口径(如"统一按字符数, 汉字也是字"), 用户会拿三处对质。

## 续作与迭代闭环

- 已验证爆款基因公式: **自嘲情绪 × 在线即玩零门槛 × 可晒社交货币(证书/等级/编号/战报海报) × 具象化命名**。新工具按此设计, 复用"输入 → 出结果证书"形态, 单文件零依赖本地起服务。
- 工具改动端到端实测后才算完成: 起服务 → curl 打 API → 自测脚本全绿。
- git push: remote 名可能是 `github` 而非 `origin`, 分支可能是 `main`; SSH 走 443 端口(`ssh -p 443`)可穿透部分受限网络, push 前先 `git remote -v` 确认实际 remote/分支名。
- 本技能产出图文需求单(P1 单图自足、置顶评论文案、标题), 交给发布产线技能执行; 标题发布前用 `title-referee` 技能把关。

## 与其他技能的咬合

- 上游: 发布产线技能产出作品 → 本技能采集其数据。
- 下游: 本技能产出迭代需求单 → 发布技能执行; 标题用 title-referee 预检。

> 本技能由真实账号产线脱敏而来，方法论已验证，不含任何账号私有数据；平台页面结构随版本改版可能失效，欢迎 issue 反馈。
