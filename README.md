# User Skills

`~/.agents/skills/` 下的所有自定义 skill。

> 用户级 skill 目录 — catui-agent 启动时会自动扫描加载，所有项目共享。

## 目录约定

```
skills/
├── README.md                # 本文件
├── CHANGELOG.md             # 规范化版本变更日志
├── .gitignore               # 排除系统/编辑器临时文件
└── <skill-name>/            # 每个 skill 一个目录
    ├── SKILL.md             # 必须：YAML 头部 + 说明文档
    ├── scripts/             # 可选：辅助脚本
    ├── references/          # 可选：参考资料
    └── runs/                # 可选：运行日志
```

## 当前 skill 列表

| Skill | 版本 | 描述 |
| --- | --- | --- |
| [ai-news-collector](./ai-news-collector/SKILL.md) | 2.0.0 | AI 行业资讯周报（输出飞书） |
| [example-skill](./example-skill/SKILL.md) | 1.0.0 | 示例，可删除 |

## 使用方式

1. **触发**：在 catui-agent 对话中说对应 trigger 关键词
2. **新建 skill**：在 `skills/` 下建子目录，参照 `example-skill/` 模板
3. **修改 skill**：编辑后更新 `SKILL.md` 的 `version` 字段 + 在 `CHANGELOG.md` 追加记录 + git 提交

## 版本管理

采用 **Git + SemVer + Keep a Changelog**：

```bash
# 拉取/查看历史
git log --oneline
git diff v1.0.0..v2.0.0 -- ai-news-collector/SKILL.md

# 修改后提交
git add .
git commit -m "release(ai-news-collector): v2.1.0 xxx"
git tag v2.1.0    # 重要版本打 tag
```

详细规则见 [CHANGELOG.md](./CHANGELOG.md)。

## 删除示例 skill

```bash
rm -rf example-skill
git add -A
git commit -m "chore: 移除示例 skill"
```
