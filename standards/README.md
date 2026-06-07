# standards · banksys_szai4 项目规范

> **用途**:本目录存放 AI 项目记忆与通用工程规范。任意 AI 工具进入项目后,先读本文件,即可按统一规则继续开发、提交、PR、CI/CD。

---

## 1. 文件分类

| 类型 | 文件 | 是否每个项目要改 | 谁维护 |
|---|---|---|---|
| **项目活记忆** | `00-project-context.md`、`01-requirements.md`、`PROGRESS.md` | ✅ 已按本项目填写 | AI 写,人审 |
| **通用规范** | `02`~`06`、`templates/` | ❌ 默认不改 | 团队维护 |

---

## 2. AI 每次会话读取顺序

1. `00-project-context.md` — 项目身份、技术栈、目录地图、部署取值。
2. `01-requirements.md` — 活 PRD,所有需求与验收标准。
3. `PROGRESS.md` — 当前状态、下一步、决策、踩坑。
4. `02`~`06` — 通用工程规范。
5. `templates/` — Issue / PR 模板。

---

## 3. 标准开发闭环 · 固定六步(每步确认)

AI 严格按 `06-ai-collab-protocol.md` 的「六步交付流程 + 确认门」推进:

```text
① 建仓 + 配 Secrets → ② 开 feature 分支 → ③ 本地模块化开发(逐模块汇报)
     → ④ 本地 CI 自检(AI 执行) → ⑤ 触发 PR → ⑥ 人工审核→合并→CD
```

---

## 4. 反臃肿纪律

1. 需求只写进 `01-requirements.md`。
2. 进度、决策、坑只写进 `PROGRESS.md`。
3. 一需求一分支一 PR,PR 尽量小于 400 行。
4. CI 红灯不合并。
5. 新增目录前先更新 `00-project-context.md` 的目录地图。
