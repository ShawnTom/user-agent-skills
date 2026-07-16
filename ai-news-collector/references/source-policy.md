# 来源与事实规范

## 目录

1. 来源层级
2. 独立来源
3. 数据结构
4. 事实判定
5. WaytoAGI
6. 时效与冲突

## 1. 来源层级

按事实类型选择来源，不使用统一的“两个 URL 即通过”规则。

| 事实类型 | 最低证据 |
| --- | --- |
| 产品发布、版本、价格、官方活动 | 对应事件的官方原文 1 个；公司首页不算 |
| 法规、政策、监管决定 | 发布机关原文 1 个；解读只能作为补充 |
| 融资、估值、市场份额、用户量 | 至少 2 个独立来源；优先公司/监管文件加独立媒体 |
| 基准测试、性能对比 | 原始评测方法和结果；厂商自测必须标“厂商口径” |
| 客户案例、节省比例、商业效果 | 客户或可核验案例原文；营销材料标明来源属性 |
| 社区热度和观点 | 明确标为观点，不写成行业事实 |
| 预测 | 引用已验证事实作为依据，并标期限与置信度 |

搜索结果摘要、AI 摘要、转载聚合页和通用首页不能作为事实证据。短链接应解析为最终 canonical URL。

## 2. 独立来源

满足以下条件才算独立：

- `independence_key` 不同；通常使用独立编辑机构、监管机构或公司的规范名称。
- 两篇文章不是同一通讯稿、同一采访的转载或同一数据供应商的二次引用。
- 同一集团下不同域名默认算一个来源，除非有独立采编证据。

官方声明与引用该声明的媒体报道可以构成“官方 + 媒体”，但不能证明媒体没有独立核实。涉及高风险数字时继续寻找原始文件或第二套独立证据。

## 3. 数据结构

`sources.jsonl` 每行至少包含：

```json
{"source_id":"S001","canonical_url":"https://example.org/item","title":"原文标题","publisher":"发布方","independence_key":"publisher-group","source_type":"official","source_role":"event_page","retrieval_method":"direct_fetch","published_at":"2026-07-15T10:00:00+08:00","retrieved_at":"2026-07-16T09:00:00+08:00","temporal_role":"current","evidence_text":"用于核对的原文片段","content_sha256":"64位十六进制哈希"}
```

`claims.jsonl` 每行至少包含：

```json
{"claim_id":"C001","event_id":"E001","text":"最小且可验证的事实","claim_type":"release","status":"verified","include_in_report":true,"evidence":[{"source_id":"S001","quote":"必须能在 evidence_text 中找到的原文"}]}
```

`events.jsonl` 每行至少包含：

```json
{"event_id":"E001","canonical_key":"openai-product-release-2026-07-15","title":"事件标题","entity":"OpenAI","published_at":"2026-07-15T10:00:00+08:00","source_ids":["S001"]}
```

允许的 `source_type`：`official`、`regulator`、`media`、`research`、`community`、`waytoagi`。

`source_role` 使用 `event_page`、`article`、`dataset` 或 `entry_page`；`entry_page` 只用于覆盖审计，不能作为 claim 证据。`retrieval_method` 使用 `direct_fetch`、`api`、`lark_cli` 或 `search_snippet`；`search_snippet` 只能用于发现候选链接，不能作为 claim 证据。

允许的 `claim_type`：`release`、`policy`、`funding`、`market_metric`、`benchmark`、`customer_result`、`document_fact`、`analysis`、`forecast`。

允许的 `status`：`verified`、`primary_only`、`conflicting`、`unverified`。只有 `verified` 和满足规则的 `primary_only` 可作为确定性事实进入正文。

`temporal_role` 使用 `current`、`continuation` 或 `historical`。延续来源增加 `latest_update_at`；历史来源必须设置 `headline_eligible=false`。`include_in_report=false` 可保留未核实事实供审计，但不得输出为正文结论。

## 4. 事实判定

- 将复合句拆成最小事实，避免一个引用同时承担多个未验证结论。
- `quote` 必须是原文证据文本的连续或归一化后连续片段。
- 标题相似、URL 存在或来源域名权威都不能替代原文引用。
- 影响判断必须与事实段分开。无法直接证实的因果关系使用“可能”“表明”并说明依据。
- 删除无法举证的精确数字，不使用近似数字填充版式。

## 5. WaytoAGI

WaytoAGI 主 Wiki 和 `<cite doc-id>` 子文档用于证明内容来源。每个入选主题至少保留一个真实子文档 URL，并下钻读取正文。

WaytoAGI 主知识库默认收录最新资讯，主文档日期标题是条目的收录日期。标题只有月、日时，将其直接映射到当前报告窗口内匹配的日期，不单独核验年份，也不使用子文档创建时间或外部事件年份推翻该收录日期。归一化时设置 `published_at` 为对应日期的 `00:00:00+08:00`，并增加 `time_precision="day"`、`date_basis="waytoagi_latest_heading"`。此规则只适用于 `source_type="waytoagi"` 的收录日期。

WaytoAGI 是策展和转述来源，不自动成为产品、融资、市场或政策事实的一手证据。遇到这类主张时，继续查找对应官方原文和独立来源；查不到则标 `unverified`，不得写成确定事实。

## 6. 时效与冲突

- 使用页面或 API 返回的发布时间，不使用 URL 日期作为主要判断。
- WaytoAGI 收录日期按第 5 节处理；外部事实仍使用对应官方、监管、媒体或研究来源的实际发布时间。
- 修改时间只能证明页面更新，不能自动证明事件在本周发生。
- 对延续事件记录原始事件日期和本次新进展日期；只有后者计入窗口。
- 来源数字冲突时标 `conflicting`，并列数值、口径和时间，不计算未经说明的平均值。
- 保存原始响应、canonical URL、抓取时间和 SHA-256，以便复核内容变化。
