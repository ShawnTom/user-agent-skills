---
name: ai-news-collector
version: 2.6.0
description: AI 行业资讯周报生成。覆盖国内外大模型公司动态（头部公司 ≥ 3 条，每条多 query + 多源 + 完整 highlights）、制造业+AI 行业（头部 3 家 + 方法论/案例/政策各 7 条）、AI 新应用范式（waytoagi 主题聚类，每范式 5-10 支撑条目），每周以 overwrite 方式更新到唯一知识库。
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
| 飞书源 | waytoagi 知识库（Xjxv...Un4p 每日更新 wiki） | **`lark-cli docs +fetch` 走 user token**（不要用 web_fetch） |
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

**头部公司条目数规则**（**v2.4.1 新增**）：

> 解决"头部公司被简略带过"问题。

| 档位 | 公司 | 最少条目数 |
| --- | --- | --- |
| **头部（≥3 条）** | 字节 / 阿里 / MiniMax / 智谱 | **3 条**（含模型 + 商业化 + 行业地位） |
| **常规（≥1 条）** | 腾讯 / 月之暗面 / 百川 / 零一万物 / 阶跃 / 国外 3 家 | 1 条 |

如何找足 3 条？参考下面"3 条内容维度"模板：

| 维度 | 抓什么 |
| --- | --- |
| ① 模型 / 技术 | 新模型发布、版本更新、评测对比 |
| ② 商业 / 资本 | 融资、上市、定价、客户案例 |
| ③ 战略 / 行业 | 行业大会、收购、合作伙伴、市场份额 |

**如果只搜到 1 条但公司是大厂**：用 site:限定官方域名 + 多 query 组合（公司名 + 产品名 + 创始人 + 合作伙伴），不要轻易用"本周无重大更新"带过。

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

## 标题层级规则（v2.5.1 新增）

> 解决"国内大厂有 3 个 `#### 公司名 · 类型 · 日期` 标题显得割裂"的问题。

### 规则总览

| 公司档位 | 文档结构 | 标题层级 |
| --- | --- | --- |
| **头部公司（≥ 3 条动态）** | 一个 H3 公司段 + N 个编号 H4 子条目 | H3 + H4 |
| **常规公司（1 条动态）** | 一个独立 H4 | H4 |
| **本周无更新** | H4 + 一行 ⚠️ 说明 | H4 |
| **行业大会 / 国外公司 / 制造业公司** | H3 段 | H3 |

### 头部公司结构（3 条示例）

```markdown
### 字节跳动

#### ① [动态 1 简短标题] · 2026/MM/DD

**标题**：[完整事件名]

**摘要**：[2-3 句话]

**来源**：[媒体](URL)

**影响**：[一句话]

#### ② [动态 2 简短标题] · 2026/MM/DD
...

#### ③ [动态 3 简短标题] · 2026/MM/DD
...
```

### 编号规则

- ① ② ③ ④ ⑤（中文圆圈数字）
- 编号前 H4 标题要短（≤ 25 字）—— 长内容放正文，标题只是导航
- 编号后**必须**带日期

### 常规公司结构（1 条示例）

```markdown
#### 腾讯（混元） · 应用内测 · 2026/06/19

**标题**：[完整事件名]
...
```

> 单条 H4 直接用"公司名 · 类型 · 日期"格式，不加编号。

### 本周无更新（降噪处理）

```markdown
#### 月之暗面 · 本周无重大更新

> ⚠️ Kimi 系列产品未检索到本周动态。
```

> - **保留 H4**（保持目录结构一致）
> - 内容**只一行** ⚠️ 描述，**不**写"本周无重大更新"等冗余文字（避免视觉膨胀）
> - 不加任何正文模板字段

### 视觉对比

❌ **不推荐**（之前）：

```
#### 字节跳动 · 行业大会 / 模型矩阵 · 2026/06/23
...
#### 字节跳动 · 全模态理解模型 · 2026/05/07
...
#### 字节跳动 · 图像创作 · 2026/06/23
...
```

✅ **推荐**（现在）：

```
### 字节跳动

#### ① FORCE 大会 + 全模态矩阵 · 2026/06/23
...

#### ② Doubao-Seed-2.0-lite 全模态 · 2026/05/07
...

#### ③ Seedream 5.0 Pro 图像 · 2026/06/23
...
```

### 配套调整

- 头部公司条目数仍是 **≥ 3 条**（G1.1 不变）
- 编号 H4 不影响总条目数计算（仍是 1 家公司 = 3 条）

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
- [ ] **G1.1**（**v2.4.1 新增**）：**头部公司**（字节 / 阿里 / 智谱 / MiniMax）**每家 ≥ 3 条**
- [ ] **G2**：Part 2 至少检查了**西门子、GE、施耐德 3 家**
- [ ] **G3**：Part 3 **Top 5 精选**（按创新+操作+时效+传播评分），含日期 + 原文位置
- [ ] **G4**：每条非空条目**都有日期 + 可点击的完整 URL**
- [ ] **G5**：所有推测/单一来源内容**已加「待核实」标签**
- [ ] **G6**（v2.4.0 新增）：**已扫过本周行业大会清单**，如有相关事件已独立列出

通过 → 进入"飞书写入"环节。
未通过 → 列出缺失项，回到对应步骤补齐。

### G1.1 失败时的补抓流程

如果头部公司（字节/阿里/智谱/MiniMax）只搜到 1 条，按以下顺序补救：

1. **官方源深扫**：`site:<公司域名>` 或 `site:volcengine.com`
2. **子产品/品牌**：字节不是只搜"字节跳动"，要搜"豆包 / 即梦 / Seed / 火山引擎"
3. **资本/商业线**：Exa search "公司名 + 融资 / 上市 / 定价 / 收购"
4. **第三方报道**：36kr / 虎嗅 / IT 桔子（用 `web_fetch` 直搜）
5. **创始人/CXO 演讲**：谭待 / 月之暗面 杨植麟 / 王慧文 等
6. **实在搜不到**：保留 1 条但加"⚠️ 本周公开动态较少，不代表公司无动作"

---

## 执行流程（v2.6.0 重写）

> **核心转变**：从"抓取 → 整理" → **"多 query 抓取 → 读完整 highlights → 主题聚类 → 多源交叉 → 完整 Markdown"**。

### 关键差异（vs v2.5.x）

| 维度 | v2.5.x | v2.6.0 |
| --- | --- | --- |
| **每家公司 query 数** | 1 | **5-8**（模型/定价/CXO/合作伙伴/收购/政策） |
| **读完抓取结果** | 只看标题 | **必读 highlights**，把数字/参数/客户名全提炼 |
| **每条来源数** | 1 | **2-3**（官方 + 媒体 + 第三方） |
| **每条时间标签** | 模糊日期 | **【YYYY/MM/DD 官方/媒体/官方+媒体/待核实】** |
| **"无更新"处理** | 简单一句话 | 加**回溯上下文**（"距上次 X 月余，本周无大动作"） |
| **Part 2 制造业** | 3 头条 + 1 方法论 | **3 头条 + 7 方法论/案例 + 7 政策** |
| **政策跟踪** | 偶发 | **必跑一轮**（工信部/网信办/发改委/八部门联合文件） |
| **Part 3 waytoagi** | 5 个单条 Top 5 | **7-8 主题聚类**，每主题 5-10 支撑条目 |
| **待核实机制** | 极少用 | **必加**（推测/单一来源/官方未确认 → ⚠️） |

### 流程图

```
┌─────────────────────────────────────────────────────────┐
│  ① 准备                                               │
│  - 确认 today / today-7 时间窗口                      │
│  - 读取上次周报链接（用于延续追踪 + 跳过已写过）     │
│  - 确认本次是否 dry-run                               │
└─────────────────────┬─────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│  ② 多维并发抓取（每家公司 5-8 query）                │
│  详见下方「抓取策略」                                │
└─────────────────────┬─────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│  ③ 深度阅读 + 多源交叉                                │
│  - 必读 highlights，不只读标题                        │
│  - 提炼数字/参数/客户名/CXO 名字                     │
│  - 每条事件找 2-3 个独立来源                          │
│  - 加上信息源标签【官方/媒体/官方+媒体/待核实】    │
└─────────────────────┬─────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│  ④ 主题聚类 + 缺口补抓                               │
│  - Part 1: 按公司分（每家 3+ 条）                    │
│  - Part 2: 按"头部公司/方法论案例/政策"三类分       │
│  - Part 3: waytoagi 按"主题"聚（不按天）             │
│  - 任何一类 < 目标条数 → 补抓                        │
└─────────────────────┬─────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│  ⑤ 质量门禁（G1-G6 + 三个新门禁 G7-G9）              │
│  G7: 每条 ≥ 2 个独立来源                              │
│  G8: 必含具体数字/参数/客户名                        │
│  G9: waytoagi 主题聚类 ≥ 7 个                        │
│  未通过 → 回到 ④ 补齐                                 │
└─────────────────────┬─────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│  ⑥ 装订 Markdown + 末尾数据标注                      │
│  - 标题：yyyy/mm/dd-模型版本                         │
│  - Part 1 → 2 → 3 严格编排                           │
│  - 末尾：采集时间 + 模型 + 来源类型 + 自查结果      │
└─────────────────────┬─────────────────────────────────┘
                      ▼
              ┌───────┴────────┐
              ▼                ▼
        ┌──────────┐    ┌──────────────────────────┐
        │ dry-run  │    │ overwrite 唯一目标 wiki     │
        └──────────┘    └──────────────────────────┘
```

### 抓取策略（详细）

#### Part 1：大模型公司

**头部公司（5-8 个 query 组合）**：

| 公司 | 必查 query 模板 |
| --- | --- |
| **字节/火山引擎** | `字节跳动 豆包 模型 发布 6月` + `火山引擎 FORCE 大会` + `Seedance OR Seedream OR Seed-Audio 6月` + `即梦 6月 更新` + `豆包专业版 OR 豆包 2.1 OR 豆包 Pro` + `梁汝波 OR 谭待 6月` |
| **阿里/通义** | `阿里 通义 Qwen 模型 6月` + `阿里 万相 Wan 视频 6月` + `通义千问 商业化 OR 定价 OR 客户 6月` + `千问 App OR Qwen3-Max 6月` + `夸克 AI OR MaaS 6月` + `Qwen-AgentWorld OR 世界模型 6月` |
| **MiniMax** | `MiniMax 海螺 OR MiniMax OR Hailuo 6月` + `MiniMax 视频 OR MiniMax OR Talkie 6月` + `MiniMax 模型 升级 OR 发布` + `MiniMax 融资 OR 上市 6月` + `MiniMax 商业化 客户 6月` + `闫俊杰 演讲 6月` |
| **智谱** | `智谱 GLM 模型 6月` + `智谱 GLM-5 上市 科创板` + `智谱 港股 涨 OR 跌 6月` + `智谱 客户 案例 6月` + `智谱 商业模式 OR 涨价 6月` + `王智远 OR 张鹏 智谱 6月` |
| **腾讯** | `腾讯 混元 模型 发布 6月` + `腾讯 元宝 OR 微信AI 6月` + `腾讯 MaaS 6月` |
| **月之暗面** | `月之暗面 Kimi 模型 6月` + `Kimi K3 OR 2.5 OR 发布 6月` + `月暗 融资 OR 估值 6月` + `杨植麟 演讲 6月` |
| **百川** | `百川智能 模型 6月` + `王小川 6月` + `百小医 6月` |
| **零一万物** | `零一万物 Yi 模型 6月` + `李开复 零一万物 6月` + `万智 2.5 客户 6月` |
| **阶跃** | `阶跃星辰 Step 模型 6月` + `姜大昕 阶跃 6月` + `Step 3 Flash 6月` + `阶跃 上市 港股 6月` |

**国外 3 家**（每家 3-4 query）：

| 公司 | query 模板 |
| --- | --- |
| **OpenAI** | `OpenAI announcement 6月` + `GPT-5 评测 OR 价格 OR 客户` + `ChatGPT Enterprise 6月` + `Sam Altman 演讲 6月` |
| **Google** | `Google AI announcement 6月` + `Gemini 3 Flash 发布` + `Google Cloud AI 客户 6月` + `I/O 2026 recap` |
| **Anthropic** | `Anthropic Claude announcement 6月` + `Claude 4.5 评测` + `Claude Code 客户 6月` + `Dario 演讲 6月` |

#### Part 2：制造业

| 类别 | query 模板 |
| --- | --- |
| **头部公司** | `Siemens Intelligence Center X` + `Siemens Industrial AI 6月` + `Siemens Xcelerator AI` + `GE Vernova AI 6月` + `GE Aerospace Palantir 6月` + `Schneider Electric 收购 OR Automate OR AI` + `施耐德 工业 AI 中国 6月` |
| **AI+制造方法论/案例**（至少 7 条） | `工业 AI 灯塔工厂 6月` + `具身智能 工业 6月` + `AI 工业 互联网 6月` + `工业 大模型 案例 6月` + `人形机器人 工业 6月` + `AI 5G 工厂 6月` + `中国制造 AI 案例 6月` |
| **政策**（至少 7 条） | `工信部 工业 AI 6月` + `八部门 印发 工业 6月` + `网信办 AI 6月` + `发改委 制造业 6月` + `十五五 制造 6月` + `工业互联网 实施意见 6月` + `中国 工业 大模型 政策 6月` |

#### Part 3：waytoagi 主题聚类

**抓取后必做的聚类**（不再按天切分）：

```
按"主题"把 30-60 条聚成 7-8 类，常见主题：
- Agent Skill 工程化
- Agentic Engineering / Loop Engineering
- OPC（One Person Company）+ Claude Cowork
- Vibe Coding / Vibe Motion
- AI Engineer 新职业
- 工具链生态（Codex/Claude Code 实战）
- 研究/产品/方法论融合
- （每周都可能新增主题，AI 自己提炼）
```

每个主题配 **5-10 个支撑条目**（带原文链接）。

### 飞书写入（默认 mode：overwrite 唯一目标 wiki）

**v2.5.0 起**固定为 overwrite 模式。目标：

```
node_token:  Czj0w4LIHiJNsykRhhWcYvvQnVh
obj_token:   RlHHdgzOsoYVc5xuzSdcWa8Pn5f   ← overwrite 用
url:         https://my.feishu.cn/wiki/Czj0w4LIHiJNsykRhhWcYvvQnVh
```

```bash
lark-cli docs +update \
  --command overwrite \
  --doc "RlHHdgzOsoYVc5xuzSdcWa8Pn5f" \
  --doc-format markdown \
  --content @./2026-07-03-MiniMax-M3.md
```

**注意**：
- 用 obj_token（`RlHH...Pn5f`），不是 node_token
- 必须用相对路径（`@./file.md`）
- 必须在文件所在目录跑（`cd /Users/st/Documents/ai-weekly-reports`）

### 自查（末尾必含）

```
数据采集时间：2026/MM/DD HH:MM
使用模型：MiniMax-M3
覆盖周期：YYYY/MM/DD - YYYY/MM/DD

自查：
- ☐ G1: 国内 9 家 + 国外 3 家全覆盖
- ☐ G1.1: 头部 4 家 ≥ 3 条
- ☐ G2: 制造业 3 头条 + 7 方法论 + 7 政策
- ☐ G3: Part 3 ≥ 7 个主题聚类
- ☐ G4: 每条都有日期 + URL
- ☐ G5: 推测/单一来源已加 ⚠️ 待核实
- ☐ G6: 重要行业大会已扫
- ☐ G7: 每条 ≥ 2 个独立来源（新）
- ☐ G8: 含具体数字/参数/客户名（新）
- ☐ G9: waytoagi 主题聚类 ≥ 7（新）
```

---

## 失败与恢复

| 场景 | 处理 |
| --- | --- |
| 某个源抓不到 | 跳过该源，标注"本周 N 家源未访问"，不影响其他源 |
| waytoagi 链接失效 | 跳过 Part 3，**降低 G3/G9 要求**为"标注 Part 3 暂时缺失" |
| 抓取后某公司信息不足 | **回溯搜索**（"距上次发布 X 月"），如确实无就标"无重大更新"+回溯上下文 |
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

| 用途 | 链接 / Token |
| --- | --- |
| waytoagi（每日知识库更新 wiki） | https://waytoagi.feishu.cn/wiki/XjxvwwCZ7ijJMxkJ3SucrVEUn4p |
| waytoagi（旧框架入口） | https://waytoagi.feishu.cn/wiki/QPe5w5g7UisbEkkow8XcDmOpn8e |
| **飞书输出（**唯一目标 wiki**）** | https://my.feishu.cn/wiki/Czj0w4LIHiJNsykRhhWcYvvQnVh |
| 目标 wiki node_token | `Czj0w4LIHiJNsykRhhWcYvvQnVh` |
| 目标 docx obj_token（overwrite 用） | `RlHHdgzOsoYVc5xuzSdcWa8Pn5f` |
| 目标 space_id | `7651908426297002965` |
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

> v2.5.0 起，**默认使用 update overwrite**，不再创建新文档。

```bash
# 查看版本
lark-cli --version

# 查看 docs 子命令
lark-cli docs --help

# ★ 默认操作：overwrite 唯一目标 wiki 里的 docx
lark-cli docs +update \
  --command overwrite \
  --doc "RlHHdgzOsoYVc5xuzSdcWa8Pn5f" \
  --doc-format markdown \
  --content @./2026-07-03-MiniMax-M3.md

# 完整工作流指南（lark-cli 内置 skill）
lark-cli skills read lark-doc
```

### D. 本地备份目录

```
~/Documents/ai-weekly-reports/YYYY-MM-DD-模型版本.md
```

> **重要**：因飞书上 overwrite 会丢失历史，建议永远在本地保留 Markdown 备份（至少最近 4 周可对比）。

### E. 版本历史

> 详细变更记录见 [`../../CHANGELOG.md`](../../CHANGELOG.md)
> 用 Git 追踪（`git log -p SKILL.md` 查看行级 diff）

| 版本 | 日期 | 主要变更 |
| --- | --- | --- |
| 2.6.0 | 2026-07-03 | **流程重写**：多 query（5-8/家）、读完整 highlights、每条 2-3 来源、信息源标签【官方/媒体】、Part 2 扩到 3 头条+7 方法论+7 政策、waytoagi 主题聚类 7+ 主题、必加 ⚠️ 待核实、新门禁 G7/G8/G9 |
| 2.5.1 | 2026-07-03 | **标题层级规则**：头部公司（≥3 条）合并为 H3 段 + 编号 H4 子条目（① ② ③）；常规公司 1 条 H4；无更新用 ⚠️ 降噪 |
| 2.5.0 | 2026-07-03 | **唯一目标知识库**（`Czj0w4...QnVh`）；默认 overwrite 模式；删除"复制到新空间"流程；保留本地 Markdown 备份防历史丢失 |
| 2.4.1 | 2026-07-03 | 头部公司（字节/阿里/智谱/MiniMax）≥ 3 条规则；G1.1 门禁 + 补抓流程；3 条内容维度模板 |
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
