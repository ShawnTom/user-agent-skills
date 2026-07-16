# 飞书授权与真实原文预检

## 目录

1. 目标
2. 身份与权限
3. 预检流程
4. 返回内容真实性
5. 失败处理
6. 2026-07-16 实测结论

## 1. 目标

证明以下事项，而不仅是“本地存在 token”：

- CLI 能访问凭证存储；
- 用户 token 能通过服务端验证和自动刷新；
- 当前身份具备 Wiki 与 Docx 只读权限；
- 目标 Wiki ACL 允许访问；
- 返回内容是目标飞书正文，不是登录页、空响应或搜索转述；
- 主文档中的 `<cite doc-id>` 可以下钻读取。

## 2. 身份与权限

默认显式使用 `--as user`，禁止依赖 `auto`。至少检查：

```text
wiki:node:read
wiki:node:retrieve
docs:document.content:read
docx:document:readonly
offline_access
```

`status=needs_refresh` 和 `tokenStatus=needs_refresh` 可以进入一次真实读取，但随后必须再次执行 `auth status --verify`，确认变为 `ready` 和 `valid`。

公开 Wiki 可能允许 bot 读取，但这不是稳定授权保证，也不能外推到私有文档。默认不静默回退 bot。

## 3. 预检流程

首选运行：

```bash
python3 scripts/preflight_lark.py \
  --doc "https://waytoagi.feishu.cn/wiki/XjxvwwCZ7ijJMxkJ3SucrVEUn4p" \
  --identity user \
  --sample-cites 3 \
  --output audit/lark-preflight.json
```

脚本依次执行：

1. `lark-cli auth status --json --verify`；
2. `lark-cli wiki +node-get --as user`；
3. `lark-cli docs +fetch --as user --doc-format markdown`；
4. 抽取并读取最多 3 个 `<cite doc-id>` 子文档；
5. 再次验证 token 状态；
6. 保存 revision、更新时间、字符数、cite 数量、正文 SHA-256 和抽样结果。

不要把 access token、refresh token、appSecret、open_id 或完整 scope 写入审计文件。

## 4. 返回内容真实性

至少满足：

- `ok=true`；
- 返回 `identity` 与请求身份一致；
- Wiki `obj_type=docx`；
- `document_id` 与节点 `obj_token` 一致；
- `revision_id > 0`；
- 正文字符数超过配置阈值；
- 标题与 Wiki 节点标题一致或合理对应；
- 正文不含登录、未授权、验证码或错误页特征；
- 子文档能返回独立 document ID、revision 和正文。

这只能证明内容真实来自指定飞书文档。文档里的新闻事实仍按 `source-policy.md` 交叉验证。

## 5. 失败处理

| 错误 | 处理 |
| --- | --- |
| `keychain not initialized` | 让调度进程获得 macOS Keychain 权限；不要自动降级凭证存储 |
| user token 过期 | 按 lark-shared 使用最小 scope 发起 split-flow 授权 |
| missing scope | 只申请错误中列出的缺失 scope；多次授权会累积 |
| Wiki 节点成功、正文失败 | 记录 Docx ACL 或 scope 失败，不把节点元数据当正文成功 |
| 主文档成功、子文档失败 | 丢弃无法下钻的候选条目并记录失败 doc-id |
| bot 成功、user 失败 | 仍视为用户授权门禁失败；仅在明确的公开源策略下单独使用 bot |

`keychain-downgrade` 会把凭证保护从 Keychain ACL 降为文件权限。只有用户明确接受安全权衡时才执行。

## 6. 2026-07-16 实测结论

在当前环境中完成了只读模拟：

- user token 从 `needs_refresh` 自动刷新为 `ready/valid`；
- WaytoAGI 主 Wiki 解析为 Docx，正文 revision 为 `5090`，约 `470867` 字符；
- 抽样子文档读取成功，返回独立 revision 和正文；
- bot 当时也能读取该公开 Wiki，证明“bot 必然 ACL 拒绝”的旧规则不成立；
- 沙箱内直接访问 Keychain 失败，获得沙箱外只读 Keychain 权限后成功。

这些数值只记录本次验证，不作为未来运行的固定阈值或期望 revision。
