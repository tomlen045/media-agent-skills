---
name: douyin-tuwen
description: Use when 用户要拆解/复刻/制作抖音图文图集。拆解→原创→渲染→验证→交付产线。
version: 1.0.0
license: MIT
author: tomlen045
---

# 抖音图文产线（拆解 → 原创 → 交付）

全流程已实测跑通（示例：8 页图集零破版交付）。适用三类请求：拆解竞品图文、把一个选题做成原创图集、给已完成的图配滑动预览。

## 流程

1. **抓竞品原图**：从分享链接页面里抓 `douyinpic.com/...~tplv-dy-aweme-images:q75.webp?...x-signature=...` 形式的图片URL（签名与有效期参数只在当次页面里，过期作废）。curl 必须同时带浏览器 UA 和 `-e "https://www.douyin.com/"` referer，缺一拿不到图。抖音图文标准画幅 1440x2400（3:5）。
2. **逐张拆解**：vision_analyze 每张图，固定问三件事——配色/字体/布局结构、逐字转录文案、排版技巧。注意 vision 会把 1440x2400 降到 720x1200，回报坐标需 x2 映射回原图。
3. **定差异化定位**（成败一步）：品类基因全部复用（见内容配方），但内容定位必须与原帖对立或互补，反差从创作者自己的真实素材/能力里找（示例：原帖「装别人的效率工具清单」→ 差异化版「别再只收藏别人的清单，我让 Agent 自己造」）。禁止复用原帖文案。
4. **写文案**：引用的 skill/仓库/数字先在本机验证存在再写（数据100%真实铁律）；「全文约N字·阅读需M分钟」用去标签后的真实字数现算。榜单类数据三源交叉核实：平台 API 实时排序 + 第三方排行站快照 + 逐项页面核实归属（仓库会迁移/改名，别信单一榜单）；会涨的数字（stars/粉丝）正文写「约N万」并标快照时间，页面印实时校验命令（如 `curl -s api.github.com/repos/<owner>/<repo> | jq .stargazers_count`）当信任卖点。
5. **HTML 定版**：每页一个 720x1200 固定尺寸 HTML（body overflow:hidden），共享一份 CSS；用 Python 数据驱动生成（文案 dict → 页面函数 → 循环写文件），改文案只改 dict。版式规范见下。
6. **渲染成图**：用 playwright 缓存的 headless 内核截图。用户 Chrome 开着时 browser_exec 真实 profile 模式会因 Login Data 写锁失败——不要让用户关 Chrome，直接用内核二进制：

   ```bash
   HS=$(ls -d ~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell | head -1)
   "$HS" --headless --disable-gpu --screenshot=p1.png --window-size=720,1200 \
     --force-device-scale-factor=2 --hide-scrollbars --virtual-time-budget=3000 \
     --default-background-color=FFFFFFFF "file://$PWD/p1.html"
   ```

   720 逻辑像素 @2x = 1440x2400，与抖音原生图同规格。二进制目录名是 `chrome-headless-shell-mac-arm64`，可执行文件名是 `chrome-headless-shell`。
7. **逐页 vision 验证**：每张 PNG 都 vision_analyze 查四项——文字溢出/截断、元素重叠、底部块完整、整页平衡。全绿才交付（声明可用前必须实测的用户铁律）。
8. **交付**：`sips -s format jpeg -s formatOptions 88 x.png --out x.jpg` 出上传用 JPG；滑动预览用 `scripts/make_carousel.py` 把整组图打包成自包含 HTML，聊天里 `::preview{file="..."}` 展示，同时给出版式拆解的滑动浏览（竞品原图同一脚本复用）。

## 内容配方（爆款基因，逐条复用）

- **数字承诺**：标题给「N个」，读者知道要滑几页；每页右上角 01/0N 进度角标。
- **权威背书**：每条带数据（stars、实测数），帮读者做「值不值得」决策；榜单逐项页版式：TOP 徽章 → 主体名（等宽字）→ 大号关键数据（≥40px）→ 三枚标签（定位/属性/年份），超长仓库名靠等宽字体自动断行，别手插 `<wbr>`。
- **口诀句式**：每条留一句可截图的对仗（示例：「X 解决怎么干活，Y 解决谁来干活」），这是被转发截图的单元。
- **身份升华**：结尾「普通人…，高阶玩家…」句式触发转发。
- **弱关注强收藏**：干货帖收藏数常大于点赞数——读者拿它当手册存；CTA 动词用「收藏」，封面就放，正文不求关注（关注引导只放尾页一句）。

## 版式规范（720x1200 实测定稿）

- 底色 #E8EDF3 + 24px 点阵暗纹；内纸张 #FBFCFD、边框 #D9E1EB、微投影——「笔记本纸」知识感。
- 标题/强调 #1B57A6 深蓝衬线（Songti SC 900），正文 27px #2F3A45 行高 1.76，眉标 12px 字距 .14em；章节路标格式「2. 名称 | 约 Nk stars」（数字用实时核实值填充，示例：`约 3k stars`）。
- 签名元素：页底终端块 #0F141B 圆角14，命令绿 #8BE28B 带 `$ ` 前缀，注释灰 #5A6673，`margin-top:auto` 钉底——契合程序员受众、与市面图文拉开差异；封面同元素放大成清单卡（绿点 ● + 名称 + 灰注释）。
- 封面 CTA：金框金字 #C8871B，动词「收藏」。
- 内页节奏：每页 1-2 章节、段落 1-3 行、大留白；行数最多的页优先复查溢出。

## 照片图集变体（把已有成图打包成图集）

- 页面 JSON 驱动（文案 dict 的照片版）：`{type: cover|photo|end, img, title, body}`，Python 循环写 720x1200 HTML，共享同一份 CSS。照片页版式 = 图（`max-width:100%; max-height:760px` 自适应）+ 衬线大字标题 + 一句 30px 文案；封面大标题 + 金底 CTA「收藏」；尾页收获感文案 + CTA + 关注一句。
- 渲染前先验证每个 img 文件名真实存在——按 id 猜文件名会错（前缀命名拿不准就先 glob 确认），错名到 headless 截图才暴露，白渲一页。天坑变体：同一项目里历史文件名前缀规则变过（示例：`img10`/`pic10` 混用），只 glob 一次还不够——每个文件名都要确认 glob 命中且路径存在，别用「应该是」的路径。
- 整组 base64 内嵌 widget 12 页约 7MB，聊天里嫌重就先出前 4 页轻量版（约 2MB）作 ::preview，完整版 JPG 落盘交付。

## 陷阱

- 复杂正文页先算总行数：27px 正文 + 多段落 + 终端块在 1200 高度内余量有限，超了就拆两页，不要缩字号（正文低于 14px 违反可读性字级底线）。
- vision 验证要明确问「是否被裁切/重叠」，只问「有没有问题」容易漏掉底部块被吃掉的情况。
- kicker 页码分母 = 封面 1 + 条目数 N；生成后先数实际文件数再写分母（N 条榜单写成「/N」实际 N+1 页，每轮都犯）。
- 段落末尾的 emoji 会孤行坠到下一行——emoji 只放进标签/徽章，不放段尾。
- 单页改版只重渲该页并重建滑动 widget，重建后必须再验一眼改动页（widget 里嵌的是旧图的风险）。

## 抖音「发布文章」Web 端自动化（实测到 90% 的边界）

creator.douyin.com 的文章发布器可以自动化到「标题+摘要+正文+发布设置全填好」，但图片上传组件过不去，剩余步骤必须交还用户。流程：

1. 登录态走用户本机 Chrome（browser_exec local=true）→ creator.douyin.com → 顶部「发布文章」选项卡（JS 按 textContent 找元素拿坐标后 CDP 点击）→「我要发文」。
2. 标题/摘要是普通 semi-input，`fill_input` 直接填。正文是 contenteditable 富文本——剪贴板 Cmd+V 走 osascript 会因焦点丢失失败，改用 JS 按 `\n\n` 拆段落、逐段 createElement('p') appendChild + dispatchEvent('input') 注入，字数统计即时生效。
3. **图片上传是硬边界**：Semi Upload 组件的 file input 动态创建、不挂 React props、change 监听在闭包里，合成事件（isTrusted=false）被忽略；CDP `DOM.setFileInputFiles` 能注入文件但触发不了组件回调；`fi.click()` 需要页面焦点而 osascript 键盘注入会打到前台的其他应用（真机上聊天窗/输入法面板随时抢焦点）。别再重复这些尝试——直接把「点上传→选本地图→点发布」这两步交还用户，图先做好放固定路径。
4. 标题 ≤30 字、摘要 ≤30 字硬限制，写文案时就按这个长度写。
5. 正文外链会被弱化：发布后验证链接是否可点，不可点就把链接挪到评论区置顶。

> 本技能由真实账号产线脱敏而来，方法论已验证，平台规则可能随改版失效，欢迎 issue 反馈。
