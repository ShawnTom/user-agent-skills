# 质量门禁 v3.1

## 目录

1. A0 输入与授权
2. G0 事实正确性
3. G1 时效
4. G2 覆盖完整性
5. G3 去重与简洁
6. G4 报告结构
7. G5 PDF

任一硬门禁失败时停止发布 PDF。不要为通过门禁而放宽证据要求。

## A0 输入与授权

- `audit/network-preflight.json` 证明 `agent-reach` 可执行，且候选搜索和官方正文读取均返回真实内容；任一路径失败时不得继续运行。
- `window_start`、`cutoff` 和 `Asia/Shanghai` 已写入审计文件。
- WaytoAGI 预检返回 `ok=true`，默认 `identity=user`。
- 用户身份 `verified=true`，真实读取后 `tokenStatus=valid`。
- 必需 scope、Wiki 节点、docx 对象、revision、正文长度和正文哈希完整。
- 至少成功下钻 3 个候选子文档；不足 3 个时下钻全部。
- Keychain、ACL 或 scope 失败时记录真实错误，不静默切换身份。

## G0 事实正确性

- 每个确定性事实都有 `claim_id` 和至少一个原文引用。
- 引用文本能在对应 `source.evidence_text` 中找到。
- 发布/政策类事实引用对应事件的官方或监管原文。
- 融资、市场数字、评测和客户效果满足独立来源要求。
- 搜索摘要、聚合页、公司首页和 WaytoAGI 转述未被当作外部事实的一手证据。
- `unverified` 不进入确定性正文；`conflicting` 明确展示冲突口径。

## G1 时效

- 每个正文事件的 `published_at` 位于 `(window_start, cutoff]`，或具有窗口内的 `latest_update_at`。
- WaytoAGI 日期标题缺少年份不构成失败；月、日匹配当前窗口且记录 `time_precision=day`、`date_basis=waytoagi_latest_heading` 即通过收录时效检查。
- 延续事件的标题日期使用本次新进展日期，历史日期只作背景。
- 没有通过 URL 路径或搜索引擎排序推断发布时间。
- 抓取时间和来源更新时间均已保留。

## G2 覆盖完整性

- `coverage.yaml` 中每个主体都有 `checked`、`no_significant_update`、`included` 或 `source_failed` 状态。
- 每个目标至少检查官方入口和适用的检索维度。
- 政策源、制造业主体和本周大会均有检查记录。
- 没有用最低新闻条数替代覆盖审计。

## G3 去重与简洁

- `deduplicate_events.py` 无未解决的重复 canonical key。
- 同一事件只完整展开一次。
- 执行摘要最多 5 条，趋势最多 3 个，观察项最多 3 个。
- 普通事件和重点事件符合字数预算。
- 无动态公司只出现在覆盖表。
- 内部质量日志未进入读者版 PDF。

## G4 报告结构

- PDF 包含执行摘要、重点事件、制造业与 AI、应用范式、趋势、观察清单和覆盖状态。
- 允许没有内容的非核心章节降级，但必须说明真实原因。
- 每条来源链接可点击且链接文本可识别。
- 事实、分析、预测和证据状态视觉上可区分。

## G5 PDF

- 使用 `assets/pdf-editorial.html` 和 `scripts/render_pdf.py`。
- 输出文件为新的非空 PDF，禁止覆盖旧文件。
- 首页、中间页、末页背景一致，无白边或明显色差。
- 页码可见且不与正文重叠。
- 标题不孤立在页尾，表头能跨页重复，表格和引用块不溢出。
- 没有空白页、截断文字、不可见链接或缺字字体。

将结果写入 `audit/quality.json`，字段包含 `gate`、`passed`、`checked_at`、`details`。该文件只用于审计，不嵌入 PDF。
