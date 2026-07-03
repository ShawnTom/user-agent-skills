---
name: example-skill
description: 这是一个示例 skill，用来演示 skill 文件的基本结构
---

# Example Skill

这是一个**示例 skill**，放在这里只是为了：

1. 演示 skill 文件的标准结构
2. 让你知道 `~/.agents/skills/` 目录已经建好了
3. 验证 catui-agent 能正常加载这个位置的 skill

## 如何写一个 skill

每个 skill 是一个目录，目录里至少要有一个 `SKILL.md`：

```
~/.agents/skills/
└── my-skill/
    ├── SKILL.md          # 必须，YAML 头部 + 说明文档
    ├── scripts/          # 可选，辅助脚本
    └── references/       # 可选，参考资料
```

## SKILL.md 头部

```yaml
---
name: my-skill            # skill 名（必填）
description: 简短描述...  # 一句话说明（必填，Catui 用它判断何时加载）
---
```

## 建议

- 把**长期、稳定**的 skill 放在 `~/.agents/skills/`（用户级）
- 把**跟具体项目相关**的 skill 放在项目内的 `.catui/skills/`
- 修改完 skill 后用 `/skills` 命令刷新列表
