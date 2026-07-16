---
name: ai-news-collector
description: 生成可溯源、时效明确、去重精简的 AI 行业周报 PDF，覆盖国内外大模型公司、制造业与 AI、AI 新应用范式和重要行业大会。用于“AI 资讯”“本周 AI 周报”“运行 ai-news-collector”等请求；要求逐项验证事实、真实读取 WaytoAGI 飞书原文、标明时间范围，并输出简洁的 Editorial 风格 PDF。
---

# AI 资讯周报 v3.1

生成一份供快速决策使用的周报。优先保证事实正确和可追溯，其次保证覆盖完整，最后才考虑条目数量和篇幅。

## 不可妥协的原则

1. 不把搜索摘要、聚合页、公司首页或真实 URL 当作事实证据。
2. 不为满足数量、数字或分析模板而补写未经证实的内容。
3. 不把 WaytoAGI 原文等同于已经核实的外部事实；其中的新闻主张仍需交叉验证。
4. 不重复展开同一事件；建立 `event_id` 后只完整解释一次。
5. 不覆盖已有周报。每次使用新的日期目录和文件名。
6. 不在读者版 PDF 中展示内部质量门禁、抓取日志或授权细节。
7. 不在断网或检索链路不完整时运行；禁止用 WaytoAGI、浏览器单页或模型已有知识替代完整互联网采集。

## 输入与时间窗口

- 使用 `Asia/Shanghai` 作为统一时区。
- `cutoff` 使用本次运行开始时间；有上次成功记录时，窗口为 `(previous_cutoff, cutoff]`。
- 首次运行时使用最近 7 个自然日，即 `[cutoff 日期 - 6 天 00:00, cutoff]`。
- 分别记录 `event_at`、`published_at`、`updated_at` 和 `retrieved_at`，不要从 URL 路径猜日期；WaytoAGI 日期段按步骤 6 的专用口径处理。
- 仅当旧事件在本窗口内出现实质性新进展时，才作为延续追踪；标题日期使用本次新进展日期。

## 必读资源

按执行阶段读取以下文件，不要一次加载所有参考资料：

- 开始采集前：[`references/coverage.yaml`](references/coverage.yaml) 和 [`references/source-policy.md`](references/source-policy.md)。
- 读取 WaytoAGI 前：[`references/lark-auth.md`](references/lark-auth.md)。
- 组织正文前：[`references/report-schema.md`](references/report-schema.md)。
- 进入生成环节前：[`references/quality-gates.md`](references/quality-gates.md)。
- PDF 渲染使用 [`assets/pdf-editorial.html`](assets/pdf-editorial.html)。

## 前置依赖

确认以下命令可用，不要在周报执行过程中自动安装或升级：

- `lark-cli`：读取 WaytoAGI Wiki 和子文档。
- `agent-reach`：互联网检索和网页抓取；执行时遵循 agent-reach skill。
- `python3`：运行本目录校验脚本。
- `pandoc` 与 Google Chrome/Chromium：生成 PDF。

在创建运行目录前完成联网预检：`agent-reach doctor --json` 必须可执行；至少一次候选搜索和一次不同域名的官方正文读取必须返回真实内容。只有浏览器单页可访问、只有 WaytoAGI 可读、DNS 可解析但正文超时，均不算通过。任一项失败时停止本次运行，不生成降级周报或 PDF。

## 工作目录

使用独立目录：

```text
<run-dir>/
├── raw/                 # 原始抓取响应，只追加不改写
├── normalized/
│   ├── sources.jsonl
│   ├── claims.jsonl
│   └── events.jsonl
├── audit/
├── report.md
└── report.pdf
```

在 `audit/run.json` 中记录 `window_start`、`cutoff`、时区、模型、命令版本和上次周报路径。

## 执行流程

### 0. 验证互联网采集链路

先运行 `agent-reach doctor --json`，再用当前激活后端执行一条带时间窗口的搜索，并读取至少一个命中事件的官方原文。把后端、检查时间、查询、URL、响应状态和失败原因写入 `audit/network-preflight.json`。搜索和正文读取必须同时成功；失败时立即停止，不得继续 WaytoAGI 预检、正文组织或 PDF 渲染。

### 1. 计算窗口并读取上次周报

优先读取上次成功运行的 `audit/run.json`。不存在时按最近 7 个自然日计算。提取仍需追踪的重大事件，但不要直接复制旧正文。

### 2. 验证飞书读取链路

在采集 Part 3 前运行：

```bash
python3 scripts/preflight_lark.py \
  --doc "https://waytoagi.feishu.cn/wiki/XjxvwwCZ7ijJMxkJ3SucrVEUn4p" \
  --identity user \
  --sample-cites 3 \
  --output <run-dir>/audit/lark-preflight.json
```

必须显式使用 `user`，不能依赖 CLI 的 `auto`。允许 `tokenStatus=needs_refresh` 进入一次真实读取，但读取后必须变成 `valid`。预检检查身份、scope、Wiki 节点、正文长度、revision、正文哈希和子文档下钻。

公开 Wiki 当前可能允许 bot 读取，但不要据此假设私有文档也可读。只有用户明确要求或单独配置了公开源降级策略时才使用 bot，并在审计文件中记录实际身份。

若出现 Keychain 不可访问，不要自动执行 `keychain-downgrade`。优先让调度环境获得 Keychain 访问；降级到本地文件会扩大凭证可读范围，必须由用户明确决定。

### 3. 完成覆盖检索

按 `coverage.yaml` 检查每个目标公司、制造业主体、政策源和大会源。覆盖完整指“所有目标都完成检索并留下结果状态”，不指“每家公司必须写若干条新闻”。

动态生成查询，始终带 `window_start` 和 `cutoff`。每家公司至少检查：

- 对应事件的官方发布页或官方博客；
- 产品/技术、商业/资本、合作/客户三个维度；
- 至少一个独立媒体或监管/研究来源，若该类事实需要交叉确认。

将每次查询、命中数、失败原因和最后检查时间写入覆盖审计。无重大动态只在覆盖状态表中标记，不创建空章节。

### 4. 规范化来源、事实和事件

将抓取结果写为结构化 JSONL：

- `sources.jsonl`：来源元数据、发布时间、抓取时间、原文证据文本和内容哈希。
- `claims.jsonl`：最小事实单元、证据引用、证据状态和风险类型。
- `events.jsonl`：用于去重和正文组织的事件记录。

字段定义和来源判定见 `source-policy.md`。不要先写报告再倒推来源。

### 5. 执行确定性校验

```bash
python3 scripts/validate_freshness.py \
  --sources <run-dir>/normalized/sources.jsonl \
  --start <ISO-8601> --cutoff <ISO-8601>

python3 scripts/validate_claims.py \
  --sources <run-dir>/normalized/sources.jsonl \
  --claims <run-dir>/normalized/claims.jsonl

python3 scripts/deduplicate_events.py \
  --input <run-dir>/normalized/events.jsonl \
  --output <run-dir>/normalized/events-deduped.jsonl
```

任一脚本退出码非 0 时停止生成 PDF。修复数据或删除证据不足的内容，不要通过放宽白名单绕过失败。

### 6. 处理 WaytoAGI

预检通过后，从主文档中只提取时间窗口内的日期段，按主题聚类并筛选 Top 5。WaytoAGI 主知识库默认收录最新资讯；日期标题只有月、日而没有年份时，直接对应到当前报告窗口内匹配的日期，不再另行核验年份，也不因缺少年份丢弃条目。将该日期按 `source-policy.md` 归一化并记录日期依据。每个入选主题必须保留真实 `waytoagi.feishu.cn/wiki/<doc-id>` 子文档链接，并至少抽查一个子文档正文。

上述日期例外只用于确定 WaytoAGI 的收录窗口。WaytoAGI 仍只证明“该内容确实来自指定知识库”；其中涉及产品发布、公司数字、融资、评测或政策时，按 `source-policy.md` 继续寻找官方或独立来源，并按外部来源的实际发布时间判断时效。

若飞书预检失败：

```markdown
::: {.warning}
**WaytoAGI 读取失败**：说明真实错误类型和发生时间。本期不生成 Part 3，禁止用搜索结果冒充原文。
:::
```

### 7. 选择内容并去重

按相关性、影响、创新性和证据质量各 0-2 分评分。总分至少 5 分才进入正文；重大政策、安全事件或用户明确关注项可人工保留，但必须说明原因。

- 普通事件：事实摘要、影响一句话、来源。
- 重点事件：核心判断、关键证据、影响范围。
- 预测：只放入观察清单，标明期限、依据和低/中/高置信度。
- 相同事件在执行摘要、关键数字、趋势和大会段中使用简短引用，不重复整段正文。

### 8. 生成报告

严格按 `report-schema.md` 编排。执行摘要最多 5 条；关键数字仅保留真正有决策价值的 5-10 个；趋势最多 3 个；观察清单最多 3 项。证据不足时允许少于上限。

来源使用短标题和可点击链接。事实与分析分开写；冲突数字并列展示并说明来源，不自行合并成一个确定值。

### 9. 通过质量门禁

按 `quality-gates.md` 逐项检查，并把结果写入 `audit/quality.json`。门禁结果不进入读者版 PDF。

### 10. 渲染 PDF

```bash
python3 scripts/render_pdf.py \
  --input <run-dir>/report.md \
  --output <run-dir>/report.pdf \
  --title "AI 行业周报 · YYYY/MM/DD"
```

渲染器拒绝覆盖已有文件。生成后检查首页、中间页和末页：背景一致、页码可见、表格能分页、标题不孤立、链接可点击、没有文字溢出或空白页。

## 发布要求

同时保留：

- 最终 PDF；
- Markdown 源文件；
- `audit/` 校验结果；
- `normalized/` 结构化事实和来源；
- 原始抓取文件及内容哈希。

向用户交付 PDF 路径，并简要说明覆盖窗口、收录事件数、待核实项和跳过章节。不要把内部 token、open_id、授权链接或完整 CLI scope 输出到报告。

## 失败处理

| 场景 | 处理 |
| --- | --- |
| 断网、DNS/代理异常、搜索或正文链路不可用 | 立即停止，不运行本技能，不用 WaytoAGI 或浏览器单页生成降级周报 |
| 单个来源失败 | 记录失败并使用同类备用源；关键类别全部失败则标覆盖缺口 |
| 用户 token 过期 | 停止 Part 3，按 lark-shared 的最小 scope 授权流程处理 |
| Keychain 不可访问 | 修复调度环境权限；禁止静默降级凭证存储 |
| WaytoAGI 主文档可读、子文档不可读 | 丢弃无法下钻的候选条目并记录 ACL 缺口 |
| 事实来源冲突 | 标记 `conflicting`，并列数字与来源 |
| 事实校验失败 | 删除或降级为待核实，不进入确定性结论 |
| PDF 生成失败 | 保留 Markdown 和审计文件，不发布旧 PDF 冒充新版本 |

## 版本

当前规范版本：`3.1.2`。变更记录见 [`CHANGELOG.md`](CHANGELOG.md)。
