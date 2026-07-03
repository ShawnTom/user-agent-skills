---
name: ai-news-collector
version: 2.4.0
description: AI 行业资讯周报生成。覆盖国内外大模型公司动态、制造业+AI 行业、AI 新应用范式（Top 5 精选），输出为飞书文档。
tags: [ai, news, weekly-report, feishu, manufacturing]
triggers:
  - "跑一下 ai-news-collector"
  - "出本周 AI 周报"
  - "开始这周的 AI 资讯"
  - "AI 资讯"
schedule: "每周五 08:40（依赖 catui-agent 客户端在线）"
---

# AI 资讯周报收集 v2

> 每周一次的 AI 行业情报整理。覆盖**国内外大模型公司**、**制造业 + AI**、**AI 新应用范式**三大板块，最终输出到飞书知识库。

---

## 任务卡（TL;DR）

| 项 | 值 |
| --- | --- |
| **输入** | 当前日期 + 上次周报（如有） |
| **输出** | 一份飞书文档，写入目标知识库 |
| **覆盖范围** | `today - 7` ~ `today`（含追踪延续） |
| **覆盖公司** | 国内 9 家 + 国外 3 家 + 制造业 3 家 |
| **质量门禁** | 5 项硬性自查，必须全过 |
| **预计耗时** | 10–20 分钟（含网络抓取） |

---

## 输入约定

### 时间窗口

- **默认范围**：`today - 7` ~ `today`（含端点）
- **追踪延续**：上一周已报道的重大事件，本周有后续进展（产品正式发布/延期/政策变化）必须**延续追踪**
- **超期事件**：超过 1 周但仍在产生后续影响 → **标注原始日期**，并写明"最新进展（YYYY/MM/DD）"

### 上下文

执行前应**先询问用户**或**读取**以下信息：

1. **当前日期**（用于计算时间窗口）
2. **上次周报链接**（如存在 → 用于"延续追踪"）
3. **本次执行是否要写飞书**（默认是；可指定 dry-run 仅生成 Markdown）

---

## 数据源

### 核心源（必用）

| 类别 | 信息源 | 抓取方式 |
| --- | --- | --- |
| 官方动态 | OpenAI / Anthropic / Google DeepMind / Meta AI 官方博客 | `web_fetch` + 日期过滤 |
| 官方动态 | 字节火山引擎 / 阿里通义 / 腾讯混元 官方公告 | `web_search` 限定站点 |
| 行业动态 | TechCrunch / The Verge / 36kr AI 频道 | `web_search` + 时间过滤 |
| 飞书源 | waytoagi 知识库 | `web_fetch` 拉取 |
| 制造业 | 西门子 / GE / 施耐德 官方 newsroom | `web_fetch` |
| 政策 | 网信办 / 工信部 / 发改委 官网公告 | `web_fetch` |

### 备用源（按需选用）

| 类别 | 信息源 | 用途 |
| --- | --- | --- |
| 论文 | arXiv (cs.AI / cs.CL / cs.LG) | Part 1 末尾"本周值得关注的论文"补充段 |
| 社区 | HackerNews / Reddit r/MachineLearning | 社区热度补充 |
| 财经 | 36kr / 虎嗅 / IT 桔子 | 融资/估值信息补充 |
| 智库 | 中国信通院 / Gartner / IDC | 行业方法论/报告引用 |

> ⚠️ 备用源**不强制要求覆盖**某家公司，但**如能找到相关条目应优先采用**（尤其是融资、论文这种非新闻源信息）。

---

## 必抓官方源清单（每家公司至少 1 个官方入口）

> **新增于 v2.4.0**：吸取"FORCE 大会漏抓"教训，整理每家公司的官方新闻入口，跑前必查。

| 公司 | 官方 news / 博客 | 重要活动页 |
| --- | --- | --- |
| **字节 / 火山引擎** | https://www.volcengine.com/news / https://seed.bytedance.com/zh/ | https://www.volcengine.com/event |
| **阿里 / 通义** | https://developer.aliyun.com/news / https://qwen.ai/news | https://yunqi.aliyun.com |
| **腾讯 / 混元** | https://cloud.tencent.com/product/tclm | — |
| **智谱** | https://docs.bigmodel.cn/cn/update/new-releases | — |
| **月之暗面** | https://www.moonshot.cn/ | — |
| **MiniMax** | https://www.minimaxi.com/news | — |
| **百川** | https://www.baichuan-inc.com/ | — |
| **零一万物** | https://www.lingyiwanwu.com/ | — |
| **阶跃星辰** | https://platform.stepfun.com/ | — |
| **Google DeepMind** | https://deepmind.google/discover/blog/ | https://io.google |
| **Anthropic** | https://www.anthropic.com/news | — |
| **OpenAI** | https://openai.com/news | — |
| **Meta AI** | https://ai.meta.com/blog/ | — |
| **西门子** | https://www.siemens.com/global/en/products/newsroom.html | — |
| **GE Vernova** | https://www.ge.com/news/ | — |
| **施耐德** | https://www.se.com/ww/en/about-us/newsroom/ | — |

> 跑 skill 时，**每家至少 1 个 query 要限定到该官方域名**（如 `site:volcengine.com`），确保不漏。

---

## 行业大会追踪（每周必扫）

> **新增于 v2.4.0**：FORCE 大会这种"事件级别"信息，单条 query 不一定能覆盖，需作为独立维度。

### 重要行业大会清单

| 大会 | 主办 | 常见时间 | 官方页 |
| --- | --- | --- | --- |
| **FORCE 原动力大会** | 火山引擎 | 6 月 / 12 月 | https://www.volcengine.com/event |
| **百度世界大会** | 百度 | 11 月 | https://baiduworld.baidu.com |
| **云栖大会** | 阿里云 | 11 月 | https://yunqi.aliyun.com |
| **华为全联接大会 (HDC)** | 华为 | 9 月 | https://www.huawei.com/cn/events/hdc |
| **腾讯云峰会** | 腾讯 | 不定期 | https://cloud.tencent.com/act |
| **OpenAI DevDay** | OpenAI | 10-11 月 | — |
| **Google I/O** | Google | 5 月 | https://io.google |
| **Anthropic Build** | Anthropic | 不定期 | — |
| **Microsoft Build / Ignite** | Microsoft | 5 月 / 11 月 | — |

### 处理规则

1. **每周跑时先扫**：本周有哪个大会召开（用 Exa 搜"行业大会 6 月"或直接查官方页）
2. **作为 Part 1 的"重要行业大会"段**单独列出（不与公司动态混在一起）
3. **覆盖内容**：核心发布清单 + 关键人物表态 + 市场地位数据 + 至少 1 个一手来源链接
4. **整理公司动态时**：对应公司的发布若属于该大会，要在公司条目里**指向**大会段（如"详见行业大会段"）

---

## 竞品清单

### Part 1：AI 前沿动态

**国内（9 家，每家至少 1 条）**：
- 字节跳动（豆包 / 即梦 / 视频生成）
- 阿里巴巴（通义千问 / 通义万相）
- 腾讯（混元）
- 智谱 AI（GLM）
- 月之暗面（Kimi）
- MiniMax（MiniMax / 海螺 / 星野）
- 百川智能
- 零一万物（Yi）
- 阶跃星辰（Step）

**国外（3 家，每家至少 1 条）**：
- Google DeepMind（Gemini / Veo / Imagen）
- Anthropic（Claude）
- OpenAI（GPT / Sora）

**附属小节**（国内 9 家后追加）：
- "本周值得关注的论文"（3–5 条 arXiv 热门）
- "本周值得关注的融资/估值"（2–3 条）

### Part 2：制造业行业动态

- 西门子（Siemens）
- 通用电气（GE）
- 施耐德电气（Schneider Electric）
- AI + 制造新方法论/成果
- 国内"制造业 + AI"十五五规划政策

### Part 3：AI 新应用范式

来源（**优先用 lark-cli 抓取**）：https://waytoagi.feishu.cn/wiki/XjxvwwCZ7ijJMxkJ3SucrVEUn4p
- 每周精选 **Top 5**（不是全量罗列）
- 标注日期 + 在原文中的位置（小节标题 / 锚点）

#### Part 3 精选评分规则（v2.4.0 新增）

> 解决"列出来太多、质量参差"问题。每次跑必须**按以下标准评分后**取 Top 5。

**评分维度（总分 10）**：

| 维度 | 权重 | 评分依据 |
| --- | --- | --- |
| **创新性** | 40% | 提出新概念 / 改变共识 / 跨范式融合；反之若是已知概念重新包装 → 低分 |
| **可操作性** | 30% | 有具体方法论 / 决策树 / 代码示例；纯理论 → 低分 |
| **时效性** | 20% | 本周首发 / 反映最新趋势；老话题翻炒 → 低分 |
| **传播性** | 10% | 行业有讨论 / 多人引用；无人问津 → 低分 |

**入选标准**：

- 总分 ≥ 7.0 才考虑入选
- 入选 Top 5 时**优先保证多样性**（不要 5 条全是"Agent 架构"主题）
- 优先选**有原文 + 可点击链接**的条目

**剔除规则（直接 0 分）**：

- ❌ 纯趋势研究 / 宏观预测（除非是当周新发布的）
- ❌ 单一产品发布（无新概念）
- ❌ 工具使用细节（除非该工具本周发生重大变化）
- ❌ 已知概念的二次解读

**输出格式**：每条标注 `⭐ Top N` 排名 + 总分（可选）+ 简短的"为什么值得关注"段（不超 3 句）。

---

## 每条信息 Markdown 模板

> **标准化输出，避免五花八门。**

### 模板 A：常规动态

```markdown
#### [公司名] · [动态类型] · [YYYY/MM/DD]

**标题**：[事件标题（中文，必要时附英文原文）]

**摘要**：[2–3 句话说明发生了什么]

**来源**：[媒体名 / 官方发布](https://完整URL)

**影响**：[1 句话点评：对行业/竞品/格局的意义，可选]
```

### 模板 B：延续追踪

```markdown
#### [公司名] · [事件延续] · [原始日期 YYYY/MM/DD] → [最新日期 YYYY/MM/DD]

**背景**：[1 句话回顾上周发生了什么]

**最新进展**：[本周的新变化]

**来源**：[媒体名](https://URL)

**影响**：[1 句话]
```

### 模板 C：暂无动态

```markdown
#### [公司名]

> 本周无重大更新。
```

### 模板 D：待核实

```markdown
#### [公司名] · [YYYY/MM/DD]

**标题**：[标题]

**摘要**：[内容]

**来源**：[来源](https://URL)

⚠️ **待核实**：[说明待核实的原因，如"仅单一来源 / 仅社区讨论 / 官方未确认"]
```

---

## 输出文档模板

```markdown
# AI 行业周报 · yyyy/mm/dd

> 数据采集时间：YYYY/MM/DD HH:MM (GMT+8)
> 使用模型：MiniMax-M3
> 覆盖区间：YYYY/MM/DD ~ YYYY/MM/DD

---

## 第一部分：AI 前沿动态

### 国内大模型公司

#### 字节跳动 · [类型] · [日期]
...

#### 阿里（通义） · ...
...

[国内 9 家全部]

#### 阶跃星辰
> 本周无重大更新。

### 国外大模型公司

#### Google DeepMind
...
[Google / Anthropic / OpenAI 三家]

### 本周值得关注的论文
1. [论文标题](arxiv URL) · 简评
2. ...

### 本周值得关注的融资/估值
- [公司] · 轮次 · 金额 · 投资方
- ...

---

## 第二部分：制造业行业动态

### 西门子
[模板 A]

### 通用电气（GE）
[模板 A 或 C]

### 施耐德电气
[模板 A 或 C]

### AI + 制造新方法论/成果
- ...

### 国内"制造业 + AI"政策
- ...

---

## 第三部分：AI 新应用范式

### [范式名称] · [YYYY/MM/DD]

**核心思想**：[1–2 句话]

**与现有范式差异**：[1 句话]

**来源**：[waytoagi 知识库 - 章节名](https://完整URL)

**点评**：[为什么值得关注]

---

> 文档生成时间：YYYY/MM/DD HH:MM
> 生成模型：MiniMax-M3
```

---

## 质量门禁（硬性，必须全过）

> ⚠️ **未通过则不允许写飞书**。回到执行流程补齐。

- [ ] **G1**：Part 1 国内 9 家 + 国外 3 家**全部有条目**（无动态用模板 C）
- [ ] **G2**：Part 2 至少检查了**西门子、GE、施耐德 3 家**
- [ ] **G3**：Part 3 **Top 5 精选**（按创新+操作+时效+传播评分），含日期 + 原文位置
- [ ] **G4**：每条非空条目**都有日期 + 可点击的完整 URL**
- [ ] **G5**：所有推测/单一来源内容**已加「待核实」标签**
- [ ] **G6**（v2.4.0 新增）：**已扫过本周行业大会清单**，如有相关事件已独立列出

通过 → 进入"飞书写入"环节。
未通过 → 列出缺失项，回到对应步骤补齐。

---

## 执行流程

```
┌─────────────────────────────────────────────────────────┐
│  ① 准备                                               │
│  - 确认 today / today-7 时间窗口                      │
│  - 询问/读取上次周报链接（用于延续追踪）             │
│  - 确认本次是否 dry-run                               │
└─────────────────────┬─────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│  ② 并发抓取（所有源并行，节省时间）                  │
│  ├─ 官方源：12 家公司博客 + 公告                       │
│  ├─ 媒体源：TechCrunch / Verge / 36kr / 虎嗅         │
│  ├─ 制造业源：Siemens / GE / Schneider newsroom      │
│  ├─ 政策源：网信办 / 工信部 / 发改委                  │
│  └─ 飞书源：waytoagi 知识库                           │
│  输出：原始材料 → 缓存到 /tmp/ai-news-raw/           │
└─────────────────────┬─────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│  ③ 逐家梳理（按竞品清单）                            │
│  - Part 1 国内 9 家 → 国外 3 家 → 论文/融资补充      │
│  - Part 2 制造业 3 家 → 方法论 → 政策                 │
│  - Part 3 拉取 waytoagi，筛过去一周条目              │
│  每家产出 1 条 Markdown（用模板 A/B/C/D）            │
└─────────────────────┬─────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│  ④ 质量门禁（5 项硬性自查）                          │
│  - G1 ~ G5 逐项检查                                  │
│  - 未通过 → 回到 ③ 补齐                              │
│  - 通过 → 进入 ⑤                                     │
└─────────────────────┬─────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│  ⑤ 装订 Markdown 文档                                │
│  - 标题：yyyy/mm/dd-模型版本                         │
│  - 严格按 Part 1 → 2 → 3 编排                        │
│  - 末尾标注采集时间 + 模型版本                       │
└─────────────────────┬─────────────────────────────────┘
                      ▼
              ┌───────┴────────┐
              ▼                ▼
        ┌──────────┐    ┌──────────────┐
        │ dry-run  │    │ 正式写入     │
        │ 输出到   │    │ 飞书知识库   │
        │ 本地文件 │    │ （见下）     │
        └──────────┘    └──────────────┘
```

### 飞书写入（仅正式模式）

1. 调用 `lark-cli` 写入目标知识库
2. **回传文档链接给用户**
3. **保留本地 Markdown 备份**到 `~/Documents/ai-weekly-reports/YYYY-MM-DD.md`

> 具体 lark-cli 命令以本地 `lark-cli --help` 为准；若工具不可用 → 回退到手动复制。

---

## 失败与恢复

| 场景 | 处理 |
| --- | --- |
| 某个源抓不到 | 跳过该源，标注"本周 N 家源未访问"，不影响其他源 |
| waytoagi 链接失效 | 跳过 Part 3，**降低 G3 要求**为"标注 Part 3 暂时缺失" |
| 飞书写入失败 | **保留本地 Markdown**，提示用户手动复制 |
| 中途中断 | **检查点机制**：每个 Part 完成后写入 `.checkpoint-Part1.done` 文件，断点续跑时跳过已完成 Part |

---

## 样例输出片段

> 给执行者一个"长什么样"的预期。

```markdown
#### OpenAI · 模型发布 · 2026/07/02

**标题**：GPT-5 正式发布，推理能力较 GPT-4 提升 40%

**摘要**：OpenAI 官方宣布 GPT-5 即日起向 Plus 用户开放，采用原生多模态架构，
在 SWE-bench Verified 上达到 74.9%。

**来源**：[OpenAI 官方博客](https://openai.com/blog/gpt-5-launch)

**影响**：与 Anthropic Claude 4 Opus、Google Gemini 2.5 Pro 的差距进一步缩小。

---

#### 智谱 AI · 融资 · 2026/07/01

**标题**：智谱完成 D+ 轮融资，估值突破 200 亿

**摘要**：本轮由北京市人工智能产业投资基金领投，多家老股东跟投。

**来源**：[36kr](https://36kr.com/p/zhipu-funding-2026q3)

**影响**：国内"AI 六小虎"格局中，智谱在 B 端政企市场领先优势进一步扩大。
```

---

## 注意事项

- **避免幻觉**：找不到来源时，**宁可标"本周无重大更新"，也不要编内容**
- **链接必须可点**：直接写完整 URL，不用"链接见原文"等模糊表达
- **日期精确**：用 `YYYY/MM/DD` 格式，不写"上周""最近"
- **多语言**：国内源用中文标题，国外源保留英文原文标题
- **冲突处理**：同一事件多源报道时 → 优先级 `官方源 > 一线媒体 > 社区讨论`
- **赞助/广告内容**：明确标注，避免混入主报告

---

## 附录

### A. 竞品清单速查

```
国内：字节 / 阿里 / 腾讯 / 智谱 / 月暗 / MiniMax / 百川 / 零一万物 / 阶跃
国外：Google / Anthropic / OpenAI
制造业：Siemens / GE / Schneider
```

### B. 链接清单

| 用途 | 链接 |
| --- | --- |
| waytoagi 知识库 | https://waytoagi.feishu.cn/wiki/QPe5w5g7UisbEkkow8XcDmOpn8e |
| 飞书输出知识库 | https://my.feishu.cn/wiki/KRltwXjqQi7GtbkSneQcVAj6nj6 |
| arXiv cs.AI | https://arxiv.org/list/cs.AI/recent |
| arXiv cs.CL | https://arxiv.org/list/cs.CL/recent |
| OpenAI 博客 | https://openai.com/blog |
| Anthropic 新闻 | https://www.anthropic.com/news |
| Google DeepMind 博客 | https://deepmind.google/discover/blog/ |
| Meta AI 博客 | https://ai.meta.com/blog/ |
| 西门子新闻 | https://www.siemens.com/global/en/products/newsroom.html |
| GE 新闻 | https://www.ge.com/news/ |
| 施耐德新闻 | https://www.se.com/ww/en/about-us/newsroom/ |

### C. lark-cli 备查

```bash
# 查看版本
lark-cli --version

# 查看 docs 子命令
lark-cli docs --help

# 创建文档（实际语法，lark-cli ≥ 1.0）
lark-cli docs +create \
  --title "2026/07/03-MiniMax-M3" \
  --content @content.md \
  --doc-format markdown \
  --parent-token <wiki_node_token>

# 完整工作流指南（lark-cli 内置 skill）
lark-cli skills read lark-doc
```

### D. 本地备份目录

```
~/Documents/ai-weekly-reports/YYYY-MM-DD-模型版本.md
```

### E. 版本历史

> 详细变更记录见 [`../../CHANGELOG.md`](../../CHANGELOG.md)
> 用 Git 追踪（`git log -p SKILL.md` 查看行级 diff）

| 版本 | 日期 | 主要变更 |
| --- | --- | --- |
| 2.4.0 | 2026-07-03 | 补 3 大规则：① 必抓官方源清单（每家公司）② 行业大会追踪维度（FORCE 等）③ Part 3 精选评分标准（Top 5，含创新/操作/时效/传播 4 维） |
| 2.3.0 | 2026-07-03 | waytoagi 链接更新为 Xjxv...Un4p（每日更新 wiki）；新增 docs +update overwrite 用于更新旧周报 |
| 2.2.0 | 2026-07-03 | 补"飞书权限"附录（docx scope / 路径处理 / +member-add / +apply-permission） |
| 2.1.0 | 2026-07-03 | 补"前置依赖安装"附录（agent-reach / Exa / lark-cli） |
| 2.0.0 | 2026-07-03 | 重构：补 frontmatter / 数据源分层 / 输出模板 / 质量门禁 / 失败恢复 / 样例 / 附录 |
| 1.0.0 | 2026-07-03 | 初版 |

**修改后必做**：
1. 更新 `SKILL.md` 的 `version` 字段
2. 在 `../../CHANGELOG.md` 追加新版本段
3. Git 提交（建议打 tag）

### F. 前置依赖安装（首次跑前必读）

> 本 skill 依赖若干**用户级**工具。所有工具均装到用户目录，**不需 sudo**、**不修改系统文件**。

#### F.1 完整依赖清单

| 工具 | 必需 | 用途 | 装在哪里 | 安装命令 |
| --- | --- | --- | --- | --- |
| **Python 3** | ✅ | 跑 agent-reach | Homebrew | （系统已有） |
| **Node.js** | ✅ | 跑 mcporter | `~/.local/bin/node` | （系统已有） |
| **agent-reach** | ✅ | 调度所有网络工具 | venv: `~/.agent-reach/venv/` | 见 F.2 |
| **mcporter + Exa MCP** | ✅ | 全网语义搜索（替代 Jina search） | npm 全局: `~/.local/bin/mcporter` | 见 F.3 |
| **lark-cli** | ✅（写飞书） | 写飞书文档 | `~/.local/bin/lark-cli` | 见 F.4 |
| **yt-dlp** | ⚠️ 可选 | 视频字幕/元数据 | venv: `~/.agent-reach/venv/bin/yt-dlp` | `~/.agent-reach/venv/bin/pip install yt-dlp` |
| **gh CLI** | ⚠️ 可选 | GitHub 仓库信息 | Homebrew | `brew install gh` |
| **gh auth** | ⚠️ GitHub 才要 | 认证 gh | — | `gh auth login`（**需用户交互**） |

#### F.2 安装 agent-reach（核心）

> **必须用 venv 隔离**，因 Homebrew Python 启用 PEP 668 禁止系统级 pip install。

```bash
# 1. 创建 venv
python3 -m venv ~/.agent-reach/venv

# 2. 在 venv 里装 agent-reach
~/.agent-reach/venv/bin/pip install https://github.com/Panniantong/agent-reach/archive/main.zip

# 3. 验证
~/.agent-reach/venv/bin/agent-reach --version
# 应输出：Agent Reach v1.5.0

# 4. 检查渠道状态
~/.agent-reach/venv/bin/agent-reach doctor
# 关注：Exa / Jina / RSS / GitHub 状态
```

#### F.3 安装 Exa 语义搜索（必需）

```bash
# 1. 装 mcporter（npm 全局）
npm install -g mcporter

# 2. 注册 Exa MCP（免费，无需 API Key）
mcporter config add exa https://mcp.exa.ai/mcp

# 3. 验证
mcporter call exa.web_search_exa query="test" numResults=2
```

#### F.4 验证 lark-cli（写飞书）

```bash
# 版本检查
lark-cli --version
# 应输出 ≥ 1.0.x

# 飞书文档命令帮助
lark-cli docs +create --help
```

> lark-cli 真实写飞书的语法是 **`lark-cli docs +create --title "..." --content @file.md --doc-format markdown --parent-token <wiki_token>`**，**不是**之前文档里写的 `lark-cli docs create --folder`（那个语法已过时）。

#### F.5 完整安装脚本（一键）

```bash
#!/bin/bash
set -e
echo "==> 1/4 装 agent-reach (venv)"
python3 -m venv ~/.agent-reach/venv
~/.agent-reach/venv/bin/pip install --quiet https://github.com/Panniantong/agent-reach/archive/main.zip

echo "==> 2/4 装 yt-dlp"
~/.agent-reach/venv/bin/pip install --quiet yt-dlp

echo "==> 3/4 装 mcporter (npm 全局)"
npm install -g mcporter
mcporter config add exa https://mcp.exa.ai/mcp

echo "==> 4/4 验证"
~/.agent-reach/venv/bin/agent-reach --version
mcporter call exa.web_search_exa query="ping" numResults=1

echo "✅ 全部依赖装好"
```

#### F.6 故障排查

| 症状 | 原因 | 修法 |
| --- | --- | --- |
| `pip: command not found` | Homebrew Python 路径 | 用 `python3 -m pip` |
| `PEP 668 externally-managed-environment` | Homebrew 锁了系统 Python | **必须用 venv**（F.2） |
| `all providers returned errors`（Jina search） | Jina search 不可用 | 改用 Exa（`mcporter call exa.web_search_exa ...`） |
| `waytoagi` 飞书文档抓空 | 需要登录态 | 跳过 Part 3 或改用 RSS 备选源 |
| `lark-cli docs +create` 报"无权限" | 没登录飞书 / token 失效 | 跑 `lark-cli login`（需用户） |
