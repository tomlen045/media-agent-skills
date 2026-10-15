# media-agent-skills 🎬

**中文自媒体全链路 Agent Skills —— 从选题到复盘的生产级技能包。**

不是 prompt 玩具。每一条技能都来自**真实运营账号的实战产线**，包含实测样式数值、ffmpeg 合成配方、实帧验证链、平台规则规避方案——拿去就能跑通，不用自己踩坑。

![覆盖平台](https://img.shields.io/badge/平台-公众号%20·%20抖音%20·%20视频号-blue) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Skills](https://img.shields.io/badge/skills-6%2B-8A2BE2)](#技能清单)

## 为什么不一样

| 市面上的技能包 | 这一套 |
|---|---|
| 一段提示词，效果看运气 | **完整 SOP**：每步有输入/输出/完成标准 |
| 纯文字生成 | **真管线**：TTS → ffmpeg 合成 → 实帧抽检验证 |
| 不知道样式能不能活过微信编辑器 | **实测数值**：在微信编辑器里逐个试出来的存活样式 |
| 发布靠感觉 | **数据复盘**：爆款归因 + 迭代动作闭环 |

## 技能清单

| 技能 | 干什么 | 亮点 |
|---|---|---|
| [`wechat-article-publisher`](skills/wechat-article-publisher/) | 公众号图文发布 | 微信编辑器实测样式数值 + 抗样式剥离写法 + 封面产线 |
| [`douyin-tuwen`](skills/douyin-tuwen/) | 抖音图文图集 | 拆解 → 原创 → 渲染 → 验证完整产线 |
| [`short-video-factory`](skills/short-video-factory/) | 口播短视频合成 | TTS 配音 + 大字幕 + ffmpeg 合成 + 实帧验证 |
| [`douyin-publish-prep`](skills/douyin-publish-prep/) | 发布素材打包 | 封面候选 / 标题标签 / 发布话术 / 上传清单 |
| [`creator-analytics`](skills/creator-analytics/) | 数据复盘 | 爆款归因 + 用户画像 + 迭代动作 |
| [`title-referee`](skills/title-referee/) | 标题评分+标题党检测 | 19 条可解释规则，本地离线引擎 |

## 安装

### 方式一：一键安装（OpenClaw / 兼容技能市场）
```bash
openclaw skills install github:tomlen045/media-agent-skills/wechat-article-publisher
```

### 方式二：npx（WorkBuddy / 通用）
```bash
npx skills add https://github.com/tomlen045/media-agent-skills/tree/main/skills/short-video-factory -g -y
```

### 方式三：手动（任何支持 SKILL.md 的 Agent）
```bash
git clone https://github.com/tomlen045/media-agent-skills.git
cp -r media-agent-skills/skills/wechat-article-publisher ~/.claude/skills/
# Hermes: cp -r skills/<name> ~/.hermes/skills/
```

## 全链路工作流

```
选题 ──▶ 创作 ──▶ 排版/渲染 ──▶ 视频合成 ──▶ 发布打包 ──▶ 数据复盘
 │         │          │             │             │            └ creator-analytics
 │         │          │             │             └ douyin-publish-prep
 │         │          │             └ short-video-factory
 │         │          └ wechat-article-publisher / douyin-tuwen
 │         └ (各技能内置创作规范)
 └ title-referee（标题把关）
```

技能之间**互相咬合**：上一步的输出就是下一步的输入，一条龙跑完一个账号的日常。

## 适合谁

- 公众号 / 抖音 / 小红书运营者：想让 AI Agent 干活而不是出主意的
- 一人媒体公司：一个人跑通过去一个团队的产线
- Agent 玩家：想要**真能跑通**的技能，不是 demo

## 隐私与边界

- 所有技能已**脱敏**：不含运营账号数据、不含任何 token/密钥
- 每条技能的 SKILL.md 都标注了依赖（如 ffmpeg/TTS）与平台边界
- 平台规则类内容（微信/抖音）随平台改版可能失效，欢迎提 issue 一起维护

## License

MIT
