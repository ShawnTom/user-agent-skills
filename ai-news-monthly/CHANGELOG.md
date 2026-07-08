# Changelog

All notable changes to the `ai-news-monthly` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-08

### Added

- 首版（Initial release）:基于 `ai-news-collector` v2.7.0 周报 skill 扩展为月报。
- **30 天时间窗口**：覆盖 `today - 30` ~ `today`，含跨周事件追踪。
- **6 维度条目模板**：头部公司每家 ≥ 6 条，分布到「模型/技术、商业/资本、战略/行业、产品/形态、国际化、治理/合规」6 维度。
- **Part 4：月度趋势分析**（独家）：4 个固定维度（资本 / 技术 / 格局 / 政策），每维度必填。
- **Part 5：跨周事件时间线**（独家）：从最近 4 期周报提取延续事件，做完整时间线聚合。
- **Part 6：本月行业大会复盘**：按月轮换清单（CES / GTC / I/O / WWDC / FORCE / WAIC / HDC / DevDay / 百度世界 / 云栖 等）。
- **MG1-MG10 质量门禁**：继承周报 G1-G5，新增 MG6-MG10（趋势分析 / 跨周时间线 / 条目数 / 来源数 / 执行摘要）。
- **每条 ≥ 3 个独立来源**（必含官方源），相比周报的 2-3 个来源更严格。
- **执行摘要（Executive Summary）**：≤ 300 字，覆盖本月 3 大事件 + 1 个核心判断。
- **5 维评分规则**（Part 3）：在周报 4 维基础上新增「持久性」维度（15%）。
- **12-15 主题聚类**：相比周报的 7-8 主题翻倍。
- **本地备份目录**：`~/Documents/ai-monthly-reports/YYYY-MM-月度AI资讯.md`。
- **飞书写入机制**：与周报共用 wiki（`LCFAwX7NmiepiIkU52AcoYUAnoh`），**新建独立文档不覆盖**。

### Notes

- 本 skill 与 `ai-news-collector`（周报）共用相同的飞书 wiki，但**输出为独立文档**，绝不互相覆盖。
- 建议工作流：每周跑 `ai-news-collector` → 每月跑 `ai-news-monthly` → 季度跑自定义复盘。
- 飞书写入不在 skill 创建时执行，**每次跑月报时由执行者触发**（按 SKILL.md 中"飞书写入"章节操作）。
