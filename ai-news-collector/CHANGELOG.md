# Changelog

本目录所有 skill 的版本变更记录。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## 版本号规则

- **MAJOR**：不兼容的输出格式变更（PDF 格式变更 / 飞书文档结构变更 / 输出模板改了）
- **MINOR**：新增章节、字段、模板（向后兼容）
- **PATCH**：bug 修复、措辞修正、链接更新

## 效果统计字段

每个版本会记录以下信息（能填则填）：

- **文件大小**：行数 / 字节数变化
- **覆盖范围**：竞品清单、行业范围变化
- **预计效果**：人工校对时间、首次运行成功率（首次跑后回填）
- **运行历史**：见 `runs/` 目录（如有）

---

## [ai-news-collector] - 当前版本

### [3.1.2] - 2026-07-16 **增加联网硬门禁**

- 正式运行前必须验证 `agent-reach`、候选搜索和官方正文读取三项链路。
- 断网、DNS/代理异常或检索链路不完整时立即停止，不生成降级周报或 PDF。
- 明确禁止用 WaytoAGI、浏览器单页或模型已有知识替代完整互联网采集。

### [3.1.1] - 2026-07-16 **修正 WaytoAGI 无年份日期口径**

- WaytoAGI 主知识库默认收录最新资讯；日期标题只有月、日时，直接映射到当前报告窗口内匹配的日期，不再另行核验年份。
- 规范化记录增加 `time_precision=day` 和 `date_basis=waytoagi_latest_heading`，使日期依据可审计。
- 时效校验器对上述 WaytoAGI 记录按报告自然日窗口判断，避免窗口首日 `00:00` 被误判；其他来源仍使用精确时间。
- 该例外仅用于 WaytoAGI 收录窗口；产品发布、融资、数字、评测和政策等外部事实仍按原规则核验来源与实际发布时间。

### [3.1.0] - 2026-07-16 **可信度、时效、去重、飞书授权与 PDF 全链路重构**

#### 变更目标

将旧版“按固定数量堆叠资讯”的规则改为“覆盖必查、事实逐项举证、重点事件精简输出”，解决数量门槛诱导凑数、URL 校验不能证明事实、固定月份查询失效、WaytoAGI 授权假设不准确和 PDF 样式选择器不生效等问题。

#### 核心规则

1. 取消“头部公司至少 4 条、常规公司至少 3 条”和“每条至少 3 个数字”等硬配额；完整性改由覆盖状态审计保证。
2. 将事实拆为 `claim_id`，要求原文引用能在来源证据文本中找到；真实 URL 不再自动等于真实事实。
3. 新增 `source_role` 和 `retrieval_method`，自动拒绝公司首页和搜索摘要作为 claim 证据。
4. 使用 `(previous_cutoff, cutoff]` 和 `Asia/Shanghai`，分别记录事件、发布、更新和抓取时间，不再从 URL 或固定月份查询推断时效。
5. 使用 `event_id` 和 `canonical_key` 去重，同一事件只完整解释一次。
6. 将预测集中到观察清单，并要求依据、期限和置信度；普通事件不再强制生成预测。
7. 将内部质量门禁移到 `audit/quality.json`，不再写入读者版 PDF。

#### 飞书与 WaytoAGI

- 新增 `scripts/preflight_lark.py`，依次验证 Keychain、服务端 token、必需 scope、Wiki 节点、Docx 正文、revision、正文 SHA-256 和最多 3 个子文档引用。
- 默认显式使用 `--as user`，禁止依赖 `auto`；允许真实读取触发自动刷新，并要求读取后 token 变为 `ready/valid`。
- 修正“bot 必然被 ACL 拒绝”的旧假设：2026-07-16 实测中，user 和 bot 均可读取该公开 Wiki；私有资源仍不能据此推断。
- 明确 WaytoAGI 只证明内容来自指定飞书知识库，其中的产品、融资、数字和政策主张仍需官方或独立来源核验。
- 沙箱内实测出现 `keychain not initialized`，在获得沙箱外只读 Keychain 权限后成功；禁止自动执行安全性更弱的 `keychain-downgrade`。
- 实测主文档 revision `5090`、正文约 `470867` 字符，子文档下钻成功；这些数值仅作本次回归记录。

#### 新增文件

- `agents/openai.yaml`：技能界面元数据。
- `references/coverage.yaml`：目标公司、制造业、政策、大会和官方入口。
- `references/source-policy.md`：来源独立性、事实类型和结构化数据规范。
- `references/report-schema.md`：精简的读者版 PDF 结构和 Pandoc class。
- `references/quality-gates.md`：授权、事实、时效、覆盖、去重和 PDF 门禁。
- `references/lark-auth.md`：飞书授权预检和失败处理。
- `scripts/preflight_lark.py`：飞书真实读取预检。
- `scripts/validate_claims.py`：逐条事实与原文引用校验。
- `scripts/validate_freshness.py`：时间窗口与延续事件校验。
- `scripts/deduplicate_events.py`：事件合并和近重复报警。
- `scripts/render_pdf.py`：拒绝覆盖旧文件的 PDF 渲染器。
- `assets/pdf-editorial.html`：新的 Editorial PDF 模板。

#### PDF 模板

- 将模板从 `templates/` 移到 `assets/`。
- 删除无法按文字内容工作的 `:has(⚠️)`、`:has(❋)` 等选择器，改用 `.source`、`.warning`、`.policy-note`、`.method-note` 明确 class。
- 使用 `@page` 页边距和页面背景，移除只对文档首尾生效的 body 分页 padding。
- 允许长表分页，重复表头，并避免单行、标题和引用块不合理断页。
- 链接保持正文颜色，仅用克制的橙色下划线区分。

#### 结构与体积

- `SKILL.md`：`1400` 行 / `65368` 字节缩减为 `198` 行 / `9117` 字节。
- frontmatter 仅保留 `name` 和 `description`，移除校验器不接受的 `version`、`tags`、`triggers` 和 `schedule`。
- 删除对临时 `.trae-cn` 工作目录和缺失 `verify-fetch-date.py` 的运行依赖。
- 保留本目录 `CHANGELOG.md`，因为本次由用户明确要求更新版本记录。

#### 验证结果

- skill-creator `quick_validate.py`：通过，返回 `Skill is valid!`。
- Python 语法、YAML 解析：通过。
- 事实校验：正确的官方发布和双源融资通过；伪造引用、单源市场数字和公司入口页证据均被拒绝。
- 时效校验：窗口内来源通过；事件去重将 3 条输入合并为 2 个事件。
- PDF：Pandoc + Chrome 生成 3 页 A4 PDF，文件签名和元数据正确，页码、表格分页正常；三页边缘像素均为 `#FAF9F5`。
- 飞书预检：`identity=user`、token 前后均为 `ready/valid`，主文档读取成功，识别 `2732` 个 cite，并成功下钻抽样子文档。
- 覆盖保护：渲染器对已有 PDF 返回拒绝覆盖。

---

### [3.0.2] - 2026-07-14 🔴 **Part 3 waytoagi 真实性硬约束（事故复盘 + 永久修复）**

#### 🐛 事故（v3.0.0 + v3.0.1 两次周报 Part 3 失败）
**时间**：2026/07/14 14:43 - 17:30
**问题**：
- v3.0.0 周报 Part 3（7 个主题聚类）的「来源汇总」全部是**公开媒体的二次传播**（今日头条 / 掘金 / CSDN / 博客园）——**不是 waytoagi 原文**
- v3.0.1 周报 Part 3 同样问题
- 核心失败：用 `WebSearch` 搜索「waytoagi AI Agent 范式」→ 拿到的是转述文章 → 假装是 waytoagi 原文
- 违反 G3（waytoagi Top 5 精选 + 原文位置）+ G9（主题聚类 ≥ 7）+ G0.1（URL 可溯源到抓取文件）

**根因**：
- `web_fetch https://waytoagi.feishu.cn/wiki/Xjxv...` 需要登录态 / 鉴权，公开网络工具无法获取
- skill 原设计依赖 v2.3.0 的 `lark-cli docs +fetch`，但**未在执行流程中显式说明「必须用 lark-cli」**
- 缺门禁：G3 没有强制要求每条 H4 含 waytoagi 真实 URL，导致执行者**有空间用其他源拼凑**
- 缺降级流程：抓取失败时没有硬性规定「必须显式标注失败原因 + 禁止填空」

**对比验证**：
- v3.0.0/v3.0.1 Part 3 来源：toutiao.com / juejin.cn / csdn.net / cnblogs.com（**公开媒体转述**）
- v3.0.2 Part 3 来源：waytoagi.feishu.cn/wiki/<doc-id>（**真实原文锚点**）

#### 🔧 永久修复（5 项硬约束）

**1. 新增 G3.1 真实性硬约束**：
- Part 3 每条 H4 的「来源汇总」里**至少 1 个 URL 必须能溯源到 waytoagi 原文**
- URL 格式：`https://waytoagi.feishu.cn/wiki/<doc-id>`
- 判定方法：grep URL 含 `waytoagi.feishu.cn/wiki/`
- **禁止用 WebSearch 拼凑二次传播内容冒充 waytoagi 原文**

**2. 新增 G3.2 抓取失败降级硬约束**：
- `lark-cli docs +fetch` 抓取失败时，**必须**在 Part 3 顶部加 ⚠️ 标注 + 真实原因
- **禁止用任何替代源填空**
- 模板：
  ```
  > ⚠️ **waytoagi 抓取失败**：`lark-cli docs +fetch` 返回 [真实原因]。
  > 本周 Part 3 跳过，G3 / G9 门禁降级为 N/A。
  > 失败原因：[详细错误信息]
  ```

**3. 抓取流程标准化**：
- 必须在执行流程（Part 3 章节）写明完整命令：
  ```bash
  lark-cli docs +fetch \
    --doc "https://waytoagi.feishu.cn/wiki/XjxvwwCZ7ijJMxkJ3SucrVEUn4p" \
    --as user \
    --doc-format markdown \
    > fetch/waytoagi-YYYY-MM-DD-full.json
  ```
- 关键参数：`--as user`（user 身份，绕开 ACL）+ `--doc-format markdown`（结构化输出）

**4. 硬约束清单**：
- ❌ 禁止用 `WebSearch` 抓 waytoagi 内容
- ❌ 禁止用其他媒体的二次报道冒充 waytoagi 原文
- ❌ 抓取失败时禁止用替代源填空
- ✅ 必须用 `lark-cli docs +fetch` 抓取真实原文
- ✅ 每个支撑条目必须含 `https://waytoagi.feishu.cn/wiki/<doc-id>` 锚点
- ✅ 抓取失败时按 G3.2 显式标注降级

**5. 实测验证**：
- 用户机器 `~/.lark-cli/config.json` 已配置 user 身份
- 实测命令：
  ```bash
  lark-cli docs +fetch --doc "https://waytoagi.feishu.cn/wiki/XjxvwwCZ7ijJMxkJ3SucrVEUn4p" --as user --doc-format markdown
  ```
- 返回：✅ 753KB JSON 包含 19774 行 markdown 全文
- 7/7 ~ 7/13 全部 7 天内容完整可读，每条文章有真实 `<cite doc-id>` 锚点

#### 📝 文档变更
- **`SKILL.md`**：
  - 版本号 v3.0.1 → v3.0.2
  - G3 新增 G3.1（真实性硬约束）+ G3.2（抓取失败降级硬约束）
  - Part 3 抓取流程章节完全重写（5 步 lark-cli 流程 + 硬约束清单）
  - 版本历史表新增 v3.0.2 行
- **`fetch/waytoagi-2026-07-14-full.json`**：753KB 真实 waytoagi 全文抓取（本次跑产物）
- **`fetch/waytoagi-2026-07-14-content.md`**：19,774 行可读 markdown 解析

#### ✅ 验证结果
- 实测命令成功：返回 7/4 ~ 7/13 共 10 天内容（7/14 尚未收录，符合 waytoagi 每日更新规律）
- 7/7 ~ 7/13 区间抓取到 30+ 篇文章，全部含真实 `<cite doc-id>` 锚点
- Part 3 重写后，所有「来源汇总」URL 均为 `https://waytoagi.feishu.cn/wiki/<doc-id>` 真实锚点

#### 🎯 承诺
- **永久闭环**：后续周报 Part 3 必须走 lark-cli 抓取真实原文，禁止降级为 WebSearch
- **每次必跑门禁**：G3.1（URL 溯源检查）+ G3.2（抓取失败标注）
- **本次 PDF 重生成**：Part 3 完全替换为真实 waytoagi 原文支撑条目

---

### [3.0.1] - 2026-07-14 🟢 **PDF 背景底色修复**

#### 🐛 问题（v3.0.0 首跑回归测试发现）
**时间**：2026/07/14 14:43
**问题**：v3.0.0 周报 PDF 生成后，用户反馈「PDF 边上有一圈白色」——即 PDF 四周边缘出现明显白色边框，破坏 Editorial 纸媒风要求的「整页米白底 `#FAF9F5`」。

**根因**：Chrome headless 转 PDF 时，`@page` 的 `margin` 区域是**浏览器的硬性白边**——即使 body 设置了 `background: #FAF9F5`，这个区域也不会继承 body 颜色，永远显示为白色。表现：页面四周出现一圈宽度等于 `@page margin`（2.2-2.8cm）的白色边框。

**验证**：用 Preview 打开 `2026-07-14-MiniMax-M3.pdf`（v3.0.0 首跑版本），四周边缘明显可见一圈白色边框。

#### 🔧 修复方案（4 项 CSS 必须同时满足）
1. **`@page { margin: 0; background: #FAF9F5; }`**——消除硬性白边 + 给页面本身设底色
2. **`@page :first { margin-top: 0; }`**——首页同步
3. **`html { background: #FAF9F5; }` + `body { background: #FAF9F5; padding: 2.2cm 2.8cm 2.8cm 2.8cm; min-height: 100vh; }`**——用 body padding 接管原 margin 的内容边距 + 双层背景保证覆盖（即使一层失效另一层兜底）
4. **`@media print { html, body { background: #FAF9F5 !important; } }`**——打印模式下强制覆盖，避免浏览器默认白色覆盖

**核心思路**：把「页面 margin」转换为「body padding」，让 body 背景色真正控制整个 PDF 区域。

#### ➕ 新增质量门禁
- **G11.1（PDF 背景底色硬约束）**：模板必须同时满足上述 4 项 CSS 要求，缺一不可
- **G11.2（PDF 生成后视觉自检）**：生成 PDF 后必须打开检查 4 项，任一不通过 → 修复模板重生成
  1. PDF 四周边缘底色 = `#FAF9F5` 米白（**非白色**）
  2. 页码仍居中显示在底部（`@bottom-center` 正常）
  3. 内容文字没有因 body padding 变化而错位
  4. 多页文档每页背景色一致（无白边 + 无页面间色差）

#### 📝 文档变更
- **`templates/pdf-editorial.html`**：核心 CSS 改造（@page margin 改为 0、html/body 双层背景、@media print 强制覆盖）
- **`SKILL.md`**：
  - 版本号 v3.0.0 → v3.0.1
  - G11 新增 G11.1（背景底色硬约束）+ G11.2（生成后视觉自检）
  - 排版约束章节标题更新为「v3.0.0 PDF 硬约束 · v3.0.1 背景底色修复」
  - 排版约束清单新增 2 条（✅ PDF 整页底色米白 + ❌ 不在 PDF 中保留浏览器默认白边）
  - 生成前自检清单新增第 5 项（grep 校验模板满足 G11.1）
  - 新增「生成后视觉自检」章节
  - 失败处理表新增 2 条（PDF 四周白边 + PDF 整页白色背景）
  - 版本历史表新增 v3.0.1 行

#### ✅ 验证结果
- 修复后 PDF：`2026-07-14-MiniMax-M3.pdf`（v3.0.1 重生成版本）整页米白底，无白边
- 文件大小：2,209,085 → 2,193,167 字节（-0.7%，差异在内容部分）
- 模板行数：507 → 507 行（结构未变，仅 CSS 调整）

#### 🎯 承诺
- **下一次跑周报**（2026/07/21）必须按 G11.1 + G11.2 自检
- **所有引用 `templates/pdf-editorial.html` 的 skill 复用** 都将获得此修复（无需重复升级）
- **PDF 背景底色问题** 永久闭环，不会再发生

---

### [3.0.0] - 2026-07-11 🟠 **输出格式变更为 PDF（移除全部飞书依赖）**

#### 变更说明
**时间**：2026/07/11
**问题**：输出格式为飞书文档，依赖 lark-cli 和飞书 API，使用门槛高。用户要求：
- 输出格式改为 PDF
- 保留 claude 浅色暖系 + Editorial 纸媒风排版风格
- 去除所有飞书文档相关格式要求

#### 🔧 变更内容
1. **输出格式**：飞书文档 → **PDF 文档**
2. **渲染管道**：lark-cli `docs +create` → **pandoc + Chrome headless 转 PDF**
3. **排版模板**：飞书结构化 Markdown → **`templates/pdf-editorial.html`**
4. **排版约束**：飞书渲染约束 → **PDF 渲染约束**（保留所有视觉风格）

#### 已删除的飞书内容
- 全部 `lark-cli` 命令和引用
- 飞书 wiki 节点 token（`LCFAwX7...`、`space_id` 等）
- "飞书写入"章节（含三不原则、创建前自检、API 限制）
- 附录 C（lark-cli 备查）
- 附录 F.4（验证 lark-cli）
- 数据源中的"飞书源"方式（waytoagi 改为 `web_fetch`）
- 执行流程中的飞书步骤
- 排版纪律中的飞书渲染约束
- 设计规范中的"飞书块类型"列

#### 已保留的内容
- 全部质量门禁 G0-G20（G0 防幻觉、G10 时间区间、G12-G20 月报质量）
- 数据源和竞品清单
- 每条信息 Markdown 模板 A/B/C/D
- 标题层级规则（H3/H4 + 编号 ① ② ③）
- H4 4 段式模板（核心判断/支撑数据/影响范围/未来 N 天预判）
- Claude 浅色暖系排版风格（#FAF9F5, #C75A2A, #2A2520 等）
- 方案 C Editorial 纸媒风（Georgia 衬线 + ❋ 三星分隔线）
- 执行流程、行业大会追踪、G0 防幻觉硬约束、验证脚本

#### 已新增的内容
- **PDF 生成章节**：pandoc 转 HTML + Chrome headless 转 PDF 的完整命令和说明
- **PDF 排版约束**：6 条 ✅ 规则 + 6 条 ❌ 规则
- **`templates/pdf-editorial.html`**：PDF 渲染模板（claude 浅色暖系 + Editorial 纸媒风）
- 依赖安装更新：pandoc 和 Chrome 依赖项

#### 文档变更
- `SKILL.md`：版本号 v3.0.0，描述行标注输出格式变更
- `SKILL.md`：新增"PDF 生成"章节（替换原"飞书写入"章节）
- `SKILL.md`：排版纪律改为 PDF 渲染约束
- `SKILL.md`：G11 更新为 PDF 排版方案统一
- `SKILL.md`：附录 B/C/D/E/F 全面更新
- `templates/pdf-editorial.html`：新增（PDF 渲染模板）

#### 版本号规则更新
- MAJOR：不兼容的输出格式变更（PDF 格式变更 / 飞书文档结构变更）

#### 承诺
- **下一次跑周报**（2026/07/18）严格按 v3.0.0 流程走，输出为 PDF 文件
- **所有验证脚本**（verify-citations.py、verify-date-range.py）继续使用
- **本地备份**：`~/Documents/ai-weekly-reports/YYYY-MM-DD-模型版本.pdf`

---

### [2.9.0] - 2026-07-10 🔴 **月报质量硬约束（G12-G20，9 个新门禁）**

#### 🚨 严重问题（用户对照月报反馈）
**时间**：2026/07/10 晚
**问题**：用户对照月报 `BkZlwdFQNieCOZkKLhvcWQRvnMh`（55,809 字符 / 176 URL / 373 数字实例 / 78 处来源汇总）后发现：
- 周报 v2.8.2（15,148 字符 / 114 URL / 85 数字）**只有月报 27% 的字符量**
- 周报**完全没有"分析层"**：核心判断 / 支撑数据 / 影响范围 / 未来 N 天预判 全部缺失（0 处）
- 周报只有"事件清单"，不是"分析报告"
- 缺失 6 大分析章节：执行摘要 / 关键数字 Top 10 / 资源消耗 / 本周趋势 / 跨周时间线 / 大会复盘
- 用户原话："信息质量远不如月报"

#### 🔧 修复（9 个新硬约束 G12-G20）
1. **G12 头部公司 ≥ 4 条 + 常规公司 ≥ 3 条**（月报头部 6 条、常规 3-6 条）
2. **G13 每条 H4 4 段式必填**：
   - 核心判断：一句话定性
   - 支撑数据：≥ 3 个具体数字
   - 影响范围：≥ 2 个受影响主体
   - 未来 N 天预判：时间窗口 + 具体事件
3. **G14 每条 H4 结尾「来源汇总」段 ≥ 2 URL**
4. **G15 必须有执行摘要 ≤ 300 字**
5. **G16 必须有「关键数字 Top 10」表格**
6. **G17 必须有「资源消耗」章节**
7. **G18 必须有「本周趋势分析」≥ 4 个趋势**
8. **G19 必须有「跨周时间线」≥ 3 条**
9. **G20 必须有「本周行业大会复盘」**

#### 文档变更
- `SKILL.md`：新增 G12-G20 + H4 4 段式模板（基于月报 78 处样本）
- `verify/verify-citations.py`：扩充官方入口白名单（seedream/seed-asr/minimax 等）
- `render/build-v290.py`：v2.9.0 周报生成器（含 6 大分析章节）

#### 验证结果（v2.9.0 周报）
- 字符：15,148 → **24,724**（+63%）
- 数字实例：85 → **109**（+28%）
- 来源汇总：0 → **48 处**（从无到有 ⭐⭐⭐）
- 核心判断：0 → **48 处**（从无到有 ⭐⭐⭐）
- 支撑数据：0 → **48 处**（从无到有 ⭐⭐⭐）
- 影响范围：0 → **48 处**（从无到有 ⭐⭐⭐）
- G0.1 + G10 验证：✅ 全部通过

#### 承诺
- **下一次跑周报**（2026/07/17）严格按 G0-G20 走，每条 H4 强制 4 段式
- **6 大分析章节**必须齐全（执行摘要 / 关键数字 / 资源消耗 / 本周趋势 / 跨周时间线 / 大会复盘）
- **数字密度**目标：≥ 200 个 / 周报（vs v2.8.2 的 85）

---

### [2.8.2] - 2026-07-10 🔴 **时间区间硬约束 + 信息源验证三道关卡**

#### 🚨 严重问题（v2.8.1 残留）
**时间**：2026/07/10 下午
**问题**：v2.8.1 周报虽然修了"URL 幻觉"，但**仍混入了非本周信息源**——5 月 8 日（阶跃融资）、5 月 28 日（MiniMax 商业化）、5 月 29 日（Step 3.7 Flash）、4 月 14 日（腾讯网）、1 月 7 日（八部门政策）等。用户校验发现：**覆盖区间声明 7/3-7/10，但内容混入 1-6 月**。

#### 🔧 修复
1. **新增 G10 时间区间硬约束**（与 G0 同级，最高优先级）：
   - G10.1 H4 标题日期必须落在 [start, end] 区间
   - G10.2 来源 URL 路径里的日期也必须在区间内
   - G10.3 跨月延续追踪允许但要标前缀（≤ 20% 总 H4）
   - G10.4 历史背景禁止作为 H4 头条
   - G10.5 验证脚本 verify-date-range.py
2. **新增 G11 排版方案统一**（方案 C · Editorial 纸媒风：Georgia 衬线 + 橙红 accent + ❋ 三星分隔线）
3. **新增信息源验证三道关卡**（详见 SKILL.md "信息源验证完整流程"）：
   - 关卡 1：抓取后 — verify-fetch-date.py
   - 关卡 2：装订 MD 后 — verify-citations.py + verify-date-range.py
   - 关卡 3：写飞书前 — 同上重跑
4. **fetch 脚本升级**：所有 Exa query 强制带 `after:YYYY-MM-DD before:YYYY-MM-DD` 后缀
5. **verify-citations.py 升级**：合并多个 fetch 目录（`fetch/` + `fetch-v282/`），更宽容的"前缀匹配 + 官方入口白名单"
6. **新增 verify-date-range.py**：自动检查所有 H4 日期，支持"精确日"和"月份"两种粒度

#### 文档变更
- `SKILL.md`：新增 G10 / G11 质量门禁 + 信息源验证完整流程（含 ASCII 流程图）
- `SKILL.md`：fetch 脚本示例加日期范围
- `verify/verify-date-range.py`：新增
- `verify/verify-citations.py`：合并多 fetch 目录
- `fetch/01-part1-domestic-v282.sh` / `02-part23-v282.sh`：v2.8.2 抓取脚本（带日期范围）

#### 承诺
- **下一次跑周报**（2026/07/17）严格按 G0-G11 走，三道关卡任何一道失败立即停止
- **任何超出 [start, end] 的日期**必须带"→ 延续追踪"或"⚠️"标记

---

### [2.8.1] - 2026-07-10 🔴 **紧急修复 - 防幻觉**

#### 🚨 严重问题（v2.8.0 首跑）
**时间**：2026/07/10 上午
**问题**：跑出 v2.8.0 首版周报后，用户抽查链接发现大量"看起来真实但不是文章原文"的 URL —— 即**幻觉链接**。

**具体表现**：
- ❌ 捏造 URL：用了真实域名（如 36kr.com / 钛媒体 / 财新 / 路透）但 URL 路径是**编造的**（如 `3973862.html` `8056379.html`）
- ❌ 编造标题：例如 "GPT-5 价格 $1.25 / 1M tokens"、"SWE-bench 78.4%" 这些数字**不在任何抓取结果里**
- ❌ 编造事件：例如 "腾讯元宝 DAU 1500 万"、"智谱涨价 20%"、"百川 8 月发布" 这些事件**完全虚构**
- ❌ 编造来源：用"OpenAI Blog / TechCrunch"等真实域名当来源，但**实际未抓到这些报道**

**根因**：抓取数据不足（部分公司只搜到 1-2 条），但 G1.1 硬性要求头部公司 ≥ 3 条 → **违反 G5 "宁可标本周无重大更新，也不要编内容"** → 选择"凑数 + 编造"。

**这是对用户的欺骗**，严重违反 trust。

#### 🔧 修复
1. **召回 v2.8.0 首跑文档**：
   - MD / HTML / PDF / PNG 全部移至 `~/ai-weekly-archive-2026-07-10-DISCARDED/`
   - 在该目录写 `README.md` 记录问题清单 + 修复方案
2. **新增 G0 防幻觉硬约束**（最高优先级，高于 G1-G9）：
   - **G0.1**：每条 H4 的 URL 必须出现在抓取文件 `fetch/part*/` 里（**例外**：纯官方入口页 `openai.com/news` 等）
   - **G0.2**：每条标题 / 数字 / 事件必须能在抓取结果的 `Title:` / `Highlights:` 字段里找到
   - **G0.3**：抓取数据不足时宁可不写 + 标 ⚠️，**严禁凑数**
   - **G0.4**：来源行至少 1 个 URL 可溯源
   - **G0.5**：`verify-citations.py` 自动验证脚本，跑在"装订 MD 前 / 写飞书前 / 转 HTML/PDF 前"三道关卡
3. **修改 G1.1**：「头部公司 ≥ 3 条」→「**≥ 真实抓到的条数**」（真实只有 1 条就写 1 条 + ⚠️）
4. **补齐 G7 / G8 / G9**：原版本表里漏的 3 条门禁加上

#### 文档变更
- `SKILL.md`：新增 G0 防幻觉段（5 个子规则 + 验证脚本说明 + 反面案例）
- `SKILL.md`：G1.1 失败时的补抓流程新增第 7 条"🚫 严禁凑数"
- `SKILL.md`：版本表追加 v2.8.1 段

#### 承诺
- **下一次跑周报**（2026/07/17）将严格按 G0 走，三道验证关卡任何一道失败立即停止
- **所有 H4 条目**都会标注 `[证据: fetch/part*/xxx.json]` 让用户可追溯
- **数量上宁可少、不可假**：真实抓不到 3 条 → 只写 1 条 + ⚠️，绝不编 2 条凑数

---

### [2.8.0] - 2026-07-10

#### Added - claude 浅色暖系排版（v1）
- **设计规范**：claude 浅色 + ember orange accent。配色：底色 `#FAF9F5`、主文字 `#2A2520`、强调色 `#C75A2A`、警示色 `#B58A2E`。
- **H1 标题**：右侧加橙色 tag 徽章（模型版本），用 `` `code` `` 包裹。
- **H2 大部分**：`01 / 02 / 03` 数字前缀 + 暖灰下划线（"01 · AI 前沿动态"）。
- **H3 公司名**：左侧 3px 橙色竖条（视觉对齐 claude 风格）。
- **H4 子条目**：日期用灰色后缀弱化。
- **来源行**：从正文里独立成 `> ` 引用块（飞书渲染为左侧细灰条）。
- **待核实**：`> ⚠️ **待核实**` callout 块（飞书渲染为左侧黄条）。
- **重要提示**：`> 📋 **政策跟踪**` / `> 📌 **重要行业大会**` 统一 callout 块。
- **关键数字**：用 `` `code` `` inline 包裹（飞书渲染为浅灰底）。
- **末尾自查**：10 行 ✅ 实心勾（强调"已通过"）。
- **emoji 小标**：🟧 📅 🎨 ⚠️ 📋 📌 ✅（克制，每节最多 1-2 个）。

#### Changed
- 输出格式从"纯 Markdown 段落"升级为"**飞书结构化 Markdown**"（标题 + 段落 + 列表 + callout + 引用）。
- H2 命名："第一部分 / 第二部分 / 第三部分" → "01 / 02 / 03" 数字前缀。
- 来源行：从混在正文改成 `> ` 引用块独立列出。

#### Triggered by
- 用户反馈："把输出格式改为 HTML，保留飞书结构，整体走 claude 浅色风格，不要太夸张。"
- 实际原因：lark-cli `docs +create` 不接受 HTML/CSS（实测会原样显示 `<div>`），所以**走飞书 Markdown 富文本扩展**（callout/quote/code/emoji）来达到同样的视觉。
- 折中：保留 Markdown 作为源文件（git diff 友好），飞书端用 callout 块出 claude 浅色风格；可选 pandoc 渲染为离线 HTML 备份。

#### Effect
- 飞书视觉：暖白底 + 橙色 accent + callout 块，与之前"黑字白底"差异明显但不夸张
- 文件行数：约 1100 → 约 1150（+5%）
- 预计人工校对时间：基本不变
- 预计运行耗时：+1-2 分钟（多写几行 callout 包装）

#### Design Principles
> **克制不夸张**——v2.8.0 是"换视觉不换骨架"。

- ✅ 飞书结构层次不变（H1/H2/H3/H4 标题层级保留）
- ✅ 编号 ① ② ③ 区分头部公司多条目（保留 v2.5.1 规则）
- ✅ 排版 5 个 emoji 内（克制）
- ❌ 不在 markdown 里写原始 HTML（飞书不渲染）
- ❌ 不改原有标题层级结构

#### Reference
- HTML 预览样例：`/Users/st/ai-news-collector-preview.html`（claude 浅色 v1 完整渲染）
- 飞书 Markdown 样例：`/Users/st/.trae-cn/work/6a50838bdd37648d39fa487b/weekly-preview/sample-feishu.md`

---

### [2.7.0] - 2026-07-03

#### Changed - 推翻 overwrite 模式
- **核心原则**：用户明确要求**绝不允许覆盖任何已有的飞书文档**。每周的周报都是新文档。
- **目标 wiki 改为 `LCFAwX7NmiepiIkU52AcoYUAnoh`**（用 user 身份能 API 创建子文档的 wiki）
- **默认操作改为 `docs +create`**（不是 `docs +update overwrite`）
- 之前目标 wiki `KRltwXjqQi7GtbkSneQcVAj6nj6`（"AI前沿资讯"）API 创建子文档返回 3380004（Permission denied），改用 LCFAwX7... 这个能创建成功的 wiki
- 删除 v2.5.0~v2.6.1 的"飞书写入自检机制"（已不需要，因为 create 不会 silent fail）

#### Removed
- 三重验证逻辑（字节数 / 内容首行 / revision 递增）—— 不再需要
- 自动重试 3 次策略 —— 不再需要
- obj_token 锁定步骤 —— 不再需要
- "目标 docx obj_token（overwrite 用）" —— 已不存在

#### Added
- "三不原则"（不覆盖 / 不重复 / 不信 success）作为 v2.7.0 的硬约束
- 飞书 API 限制实测（必须 user 身份 + 某些 wiki 节点禁止 API 创建）
- 创建前自检（确认目标 wiki + 防止重复创建）

#### Triggered by
- 用户反馈："不要随便动我的历史文档！我要求你每次新建资讯都用新创建的文档，不要覆盖我的老文档！"
- 实际原因：之前 lark-cli 用错账号（企业 vs 个人）时多次 "success" 实际未写入，但**返回值的不可信性**让用户对 overwrite 模式彻底失去信任
- 客观原因：`KRltwXjqQi7GtbkSneQcVAj6nj6` wiki 持续 3380004（不能 API 创建子文档），原本想"覆盖"的方案在物理上就不可行

#### Effect
- 飞书端：每周 1 个新文档，不会动老文档
- 历史：06/18 老周报 `RlHHdgzOsoYVc5xuzSdcWa8Pn5f` 完整保留（17KB 原貌）
- 风险：飞书会出现"一堆周报"（每周一份），但用户接受

---

### [2.6.1] - 2026-07-03

#### Added - 飞书写入自检机制
- **三重验证**（写入后**必跑**，不能只信 "success"）：
  1. **字节数差异**：实际 ≥ 本地 90%
  2. **内容首行**：应是新日期，不能是"基模-Qwen3.7Max"
  3. **revision_id 递增**：避免被静默拒绝
- **自动重试 3 次**：每次间隔 2 秒（给飞书 API 同步时间）
- **obj_token 锁定步骤**：dry-run overwrite 先看 API 请求 URL 确认指向正确 obj_token
- **用户一次性操作**：建议把 wiki 节点标题从"2026/06/18-Qwen3.7Max"改为"AI 行业周报"（lark-cli 不能改标题，需飞书网页手动）

#### Triggered by
- v2.6.0 实跑返回 `"result":"success", "revision_id":184`，但 fetch 后发现内容仍是旧版（revision 跳到 186）。**仅靠返回值不可信**。

#### Effect
- 文件行数：约 950 → 约 1100（+15%）
- 写入成功率：估计从 80% → **99%+**（自检 + 重试）
- 历史损失风险：↓ 显著

---

### [2.6.0] - 2026-07-03

#### Changed - 全面反思流程
- **执行流程重写**：基于 trae 对比（user-agent 写的同主题周报），发现当前流程在信息深度、多源覆盖、政策跟踪、waytoagi 主题化上严重不足。
- **每家公司 query 数**：1 → **5-8**（多角度深抓）
- **抓取后处理**：只读标题 → **必读 highlights**，提炼数字/参数/客户名
- **每条来源数**：1 → **2-3**（官方 + 媒体 + 第三方）
- **每条信息源标签**：新增【官方】/【媒体】/【官方+媒体】/【待核实】四态
- **"无更新"**：加回溯上下文（"距上次 X 月余"）

#### Added
- Part 2 大幅扩充：
  - 头部公司：3 条 → 仍是 3 条但加细节
  - 方法论/案例：1 条 → **7 条**（灯塔工厂、具身智能、工业大模型案例等）
  - 政策：1 条 → **7 条**（八部门联合印发、网信办专项行动、十五五、模数共振行动、江苏/工信部+国资委等）
- Part 3 waytoagi 主题聚类：
  - 5 个单条 Top 5 → **7-8 个主题**（Agent Skill / Agentic Engineering / OPC / Vibe Coding / AI Engineer / 工具链 / 融合）
  - 每主题配 5-10 个支撑条目（不只列 1 条）
- 3 个新质量门禁：
  - **G7**：每条 ≥ 2 个独立来源
  - **G8**：必含具体数字/参数/客户名
  - **G9**：waytoagi 主题聚类 ≥ 7 个
- 抓取策略详细表（每家公司 query 模板）
- 末尾自查清单标准化（9 项）

#### Effect
- 文件行数：790 → 约 950（+20%）
- 单条目信息密度：估计 ↑ 100-200%
- Part 1 总条目：21 → 30+ （加 9 条"无更新"但有回溯上下文）
- Part 2 总条目：4 → 17+（方法论/政策扩 7 倍）
- Part 3：5 单条 → 7-8 主题 × 5-10 支撑条目 ≈ 40-80 个引用
- 总条目：31 → 90+
- 预计运行耗时：↑ 30-50%（多 query 多源）

#### Triggered by
- user 对比 trae（用相同模型写的同主题周报），发现 trae 质量明显更高
- trae 的优势：多 query 抓取 + 完整 highlights 阅读 + 多源引用 + 主题聚类 + 政策密集跟踪

---

### [2.5.1] - 2026-07-03

#### Added
- 「标题层级规则」章节：定义 H3 / H4 在 Part 1 各公司的使用规范
- 头部公司（≥3 条）合并为 H3 段 + 编号 H4 子条目（① ② ③ 中文圆圈数字）
- 常规公司 1 条 H4，格式 `公司名 · 类型 · 日期`
- 「本周无更新」降噪处理：用 ⚠️ 一行描述，不展开正文模板
- 视觉对比示例（❌ 不推荐 / ✅ 推荐）

#### Changed
- 无 H4 标题结构变更（仅写法规则化）
- 总条目数计算方式不变

#### Effect
- 文件行数：715 → 约 790（+10%）
- 视觉清晰度：估计 ↑ 40%（头部公司"3 个 H4" → "1 个 H3 + 3 个 H4"）
- 飞书目录可读性：↑ 显著
- 跑 skill 耗时：基本不变

#### Triggered by
- 用户反馈：「国内大厂有 3 个 `#### 字节跳动` 这种标题显得割裂」

---

### [2.5.0] - 2026-07-03

#### Changed
- **默认飞书输出策略**：`docs +update --command overwrite`（替换唯一目标 wiki 内的 docx 内容）
- **唯一目标 wiki**：
  - node_token: `Czj0w4LIHiJNsykRhhWcYvvQnVh`
  - obj_token: `RlHHdgzOsoYVc5xuzSdcWa8Pn5f`（overwrite 用）
  - space_id: `7651908426297002965`
- **去掉**「复制到新空间」的脚本/流程（之前在用户多空间测试时引入）
- **附录 B** 重写：飞书输出地址 + 三个 token 都列出来
- **附录 C** 更新 lark-cli 命令示例：默认 overwrite 而非 create
- **附录 D 强调**：本地 Markdown 备份为唯一历史归档渠道

#### Removed
- 之前误加的"把 12 篇 wiki 复制到新空间"run.sh 脚本（在 `/Users/st/Documents/ai-weekly-reports/copy-tmp/`）—— 与本次"只保留一份"目标相悖

#### Effect
- 飞书文档数量：12+ → **1**（用户在 2026-07-03 主动删除了重复空间内的所有副本）
- 下次跑写飞书：1 次 overwrite，不创建新文档
- 历史周报：靠本地 `~/Documents/ai-weekly-reports/` 备份

#### Migration
- 用户应在飞书网页端确认「AI前沿资讯」空间里只剩一篇 `2026/06/18-Qwen3.7Max` wiki
- 下次跑时跑 `lark-cli docs +update --command overwrite --doc RlHHdgzOsoYVc5xuzSdcWa8Pn5f ...`
- 如果用户保留了删除前的旧空间，本脚本无需任何修改即可正常工作（overwrite 的对象是固定 obj_token）

#### Triggered by
- 用户反馈：飞书空间内有重复内容，决定只保留一份

---

### [2.4.1] - 2026-07-03

#### Added
- 头部公司规则：字节 / 阿里 / 智谱 / MiniMax 每家 ≥ 3 条
- Part 1 「3 条内容维度」模板：模型/技术 + 商业/资本 + 战略/行业
- 质量门禁 G1.1：硬性要求头部公司条目数
- G1.1 失败时的「补抓流程」：6 步补救（site 限定 / 子品牌 / 资本线 / 第三方 / CXO 演讲）

#### Changed
- 头部公司不应该被"本周无重大更新"带过 — 加 ⚠️ 标注保留

#### Effect
- Part 1 总条目：12 → 21（+75%）
- 总条目：22 → 31（+41%）
- 头部公司覆盖深度：估计 ↑ 60%
- 预计运行耗时：基本不变（仍以并行抓取为主）

#### Triggered by
- 用户反馈：头部公司资讯过少

---

### [2.4.0] - 2026-07-03

#### Added
- 「必抓官方源清单」：12 家大模型公司 + 3 家制造业的官方 news/blog 入口
- 「行业大会追踪」维度：9 个重要行业大会清单 + 处理规则（每周必扫，作为 Part 1 "重要行业大会" 段独立列出）
- 「Part 3 精选评分规则」：4 维评分（创新 40% + 操作 30% + 时效 20% + 传播 10%），≥ 7.0 才入选，Top 5 输出

#### Changed
- 质量门禁：G3 从"至少 1 个新范式"改为"Top 5 精选 + 含日期 + 原文位置"
- 质量门禁：新增 G6 "已扫过本周行业大会清单"
- Part 3 描述：从"至少 1 个新范式"改为"每周精选 Top 5"

#### Removed
- 「避免列出来太多」缺陷：之前 Part 3 列了 11 条过载，现在强制 Top 5

#### Effect
- 文件行数：575 → 约 700（+22%）
- 字节数：约 20KB → 约 25KB（+25%）
- Part 3 输出：11 条 → 5 条（精选，质量提升）
- 漏抓率：估计 ↓ 30%（行业大会维度 + 官方源清单）
- 预计运行耗时：基本不变

#### Triggered by
- 实战经验：FORCE 大会漏抓 + Part 3 列出来太多

---

### [2.3.0] - 2026-07-03

#### Added
- waytoagi 链接更新：QPe5...pn8e（"通往AGI之路"） → Xjxv...Un4p（"WaytoAGI每日知识库更新"）
- 实战确认：`lark-cli docs +fetch` 能用 user token 直接抓 waytoagi 完整内容（693KB / 19240 行）

#### Changed
- 飞书输出方式：从"始终新建文档"改为"优先 `docs +update --command overwrite` 更新上周文档"

#### Effect
- 抓取成功率：waytoagi 从 ❌ web_fetch 鉴权墙挡 → ✅ lark-cli 直接抓到完整内容
- 首次运行成功率：估计 ↑ 50%（Part 3 不再降级）

#### Triggered by
- 用户需求：解决 waytoagi 抓取问题

---

### [2.2.0] - 2026-07-03

#### Added
- 「飞书权限」实战记录：docx scope / wiki 节点 ACL / lark-cli `+member-add` / `+apply-permission` / 路径必须相对

#### Changed
- 飞书创建方式：从 `--as bot` 改为 `--as user`（user token 有 docx:document:create + write_only scope）

#### Effect
- 飞书写入成功率：0% → 90%+（个人空间 / 部分 wiki）
- 踩坑文档化：特殊 wiki（如 AI前沿资讯 `KRltwXjqQi7GtbkSneQcVAj6nj6`）有 ACL 限制，需改目标

#### Triggered by
- 实战经验：飞书创建文档全部 3380004 失败

---

### [2.1.0] - 2026-07-03

#### Added
- 附录 F「前置依赖安装」：完整列出 agent-reach / Exa / lark-cli / yt-dlp / gh 等依赖
- 附录 F.5「一键安装脚本」：从零装齐所有依赖
- 附录 F.6「故障排查」：常见错误 + 修法（PEP 668 / Jina search 失败 / 飞书抓空等）
- F.2 venv 隔离安装指南（因 Homebrew Python 启用 PEP 668）
- F.3 Exa 语义搜索配置（替代不可用的 Jina search）

#### Changed
- 附录 C「lark-cli 备查」：修正为真实语法 `lark-cli docs +create --content @file.md --doc-format markdown --parent-token <token>`
- 移除附录 C 里的旧语法 `lark-cli docs create --folder`（已过时）

#### Effect
- 文件行数：429 → 575（+34%）
- 字节数：14713 → 约 20KB（+35%）
- 首次跑前必须装齐：agent-reach + mcporter + Exa + lark-cli（详见附录 F）
- 预计首次运行成功率：**待 v2.1 首次跑后回填**

#### Migration
- 兼容 v2.0.0：仅新增附录，章节顺序无变化

---

### [2.0.0] - 2026-07-03

#### Changed
- Frontmatter 补全：新增 `version` / `tags` / `triggers` / `schedule` 字段
- 数据源分层：**核心源**（必用）+ **备用源**（按需）
- 竞品清单修正：补充阶跃星辰，修正 MiniMax 公司描述
- 执行流程：流水账 → ASCII 流程图
- 飞书链接：标注"以 lark-cli --help 为准"

#### Added
- 4 种 Markdown 输出模板（常规 / 延续追踪 / 无动态 / 待核实）
- 5 项质量门禁（G1–G5），未通过不允许写飞书
- 失败恢复机制（检查点文件 + 降级策略）
- 样例输出片段（OpenAI / 智谱）
- 附录 A–E（速查清单 / 链接清单 / 命令备查 / 备份路径 / 版本历史）

#### Effect
- 文件行数：185 → 429（+132%）
- 字节数：6033 → 14713（+144%）
- 预计人工校对时间：↓ 约 30%（输出标准化）
- 预计首次运行成功率：**待首次跑后回填**
- 运行历史：见 `runs/2026-07-03.log`（如已记录）

#### Migration
- 兼容 v1.0.0：竞品清单、章节结构、链接清单均保持向后兼容
- 旧版本输出模板可继续使用，但**建议升级到 v2 模板**以获得门禁校验

---

### [1.0.0] - 2026-07-03

#### Added
- 初版：AI 行业资讯周报收集 skill
- 覆盖 12 家大模型公司（国内 9 + 国外 3）+ 3 家制造业公司
- 基础质量自查清单（5 项）
- 飞书输出基础流程

#### Effect
- 文件行数：185
- 字节数：6033
- 首次运行成功率：**待回填**

---

## 其他 skill

- `example-skill/`：示例，v1.0.0，无功能变更

---

## 如何添加新版本记录

每次修改 skill 后：

1. 编辑对应 `SKILL.md` 的 `version` 字段
2. 在本文件顶部追加新版本（**不要改历史记录**）
3. 填写 Effect 段（已知信息先填，运行时数据后补）
4. 提交：

```bash
git add <skill-dir>/
git commit -m "release(ai-news-collector): v2.1.0 简要说明"
```

## 查看历史

```bash
git log --oneline                    # 提交历史
git log -p SKILL.md                  # 单文件 diff 历史
git diff v1.0.0..v2.0.0 -- SKILL.md  # 两版本间 diff
```

---

## 补充资料

- [loop-improvements.md](./loop-improvements.md) — ai-news-collector v1.0 → v2.6.0 迭代全过程：版本时间线、对比 trae 的 8 个差距、Loop 改进模式、下一步方向（2026/07/03 建立）
