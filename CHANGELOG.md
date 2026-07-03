# Changelog

本目录所有 skill 的版本变更记录。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## 版本号规则

- **MAJOR**：不兼容的输出格式变更（飞书文档结构变了 / 输出模板改了）
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
