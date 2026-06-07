# PROGRESS · banksys_szai4 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-06-07 · by AI)

- **阶段**:`初始化` — 对应六步流程**第①步(建仓前准备)**
- **上一步完成**:项目文档已填写 — `00-project-context.md`、`01-requirements.md`、`PROGRESS.md` 初版完成。
- **下一步 (TODO 第一条)**:人工确认文档内容后,进入六步流程第①步:建仓 + 配 Secrets。
- **阻塞项**:等待人类确认以下内容:
  1. 项目目标与技术栈是否准确?
  2. 四个用户故事(US-1~US-4)和验收标准是否覆盖完整?
  3. 目录结构是否合理?
  4. 端口 8004 是否确认?

---

## 待办清单 (TODO,按优先级)

### 第一批 TODO — 初始化阶段(本次会话)

- [x] 阅读 `standards/` 全部规范(README + 00~06)
- [x] 填写 `standards/00-project-context.md`(项目身份、技术栈、目录地图、质量门槛、部署取值)
- [x] 填写 `standards/01-requirements.md`(4 个用户故事,各含验收标准)
- [x] 初始化 `PROGRESS.md`(本文件)
- [ ] **✋ 确认门:等待人类确认上述文档内容**
- [ ] 建仓:用 `gh` 创建 GitHub 仓库 `banksys_szai4`
- [ ] 提示人类配置 GitHub Secrets:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`
- [ ] 构建项目骨架:目录结构、`requirements.txt`、`requirements-dev.txt`、`.gitignore`、`Dockerfile`
- [ ] 编写 CI workflow(`.github/workflows/ci.yml`)
- [ ] 编写 CD workflow(`.github/workflows/cd.yml`)

### 第二批 TODO — US-1:工程化落地与 CI/CD 跑通

- [ ] 从 `main` 开 `feature/1-project-init` 分支
- [ ] 实现 `app.py` —— Streamlit 主入口(含主页 + 页面导航)
- [ ] 实现 `src/data_loader.py` —— 数据加载与预处理
- [ ] 实现 `tests/test_data_loader.py`
- [ ] 本地自检:ruff + pytest + 覆盖率
- [ ] Push + 建 PR → CI 全绿 → 人工合并 main → CD 部署验证

### 第三批 TODO — US-2:数据分析交互页面

- [ ] 开 `feature/2-data-analysis` 分支
- [ ] 实现 `src/analysis.py` —— 分析计算函数
- [ ] 实现 `pages/1_📊_data_analysis.py` —— 交互式分析页面
- [ ] 实现 `tests/test_analysis.py`
- [ ] 本地自检 → PR → CI → 合并 → CD

### 第四批 TODO — US-3 & US-4:模型训练与在线预测

- [ ] 开 `feature/3-model-training` 分支
- [ ] 实现 `src/model_train.py` —— 离线训练脚本
- [ ] 实现 `tests/test_model_train.py`
- [ ] 开 `feature/4-prediction` 分支
- [ ] 实现 `src/predict.py` —— 模型推理
- [ ] 实现 `pages/2_🔮_prediction.py` —— 在线预测页面
- [ ] 实现 `tests/test_predict.py`
- [ ] 分别自检 → PR → CI → 合并 → CD

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-06-07 | Web 框架选 Streamlit | 适合数据应用快速搭建,内置交互组件,支持多页面,与 Python 数据生态无缝集成 |
| 2026-06-07 | 核心逻辑与 UI 分离(`src/` + `pages/`) | 便于测试(纯逻辑在 `src/`,可单测),遵循关注点分离原则 |
| 2026-06-07 | 数据与模型不进 Git | 数据集 ~30K 行 CSV;模型 `.pkl` 文件较大且由训练脚本可复现;通过 `.gitignore` 排除 |
| 2026-06-07 | 模型 AUC 门槛设为 ≥ 0.70 | 银行营销场景基线;后续可根据实际模型表现调高 |
| 2026-06-07 | 主机端口 8004,容器内 8501 | Streamlit 默认端口 8501;映射到 8004 满足课程端口要求,支持 8004-8014 回退 |

---

## 已知坑 (GOTCHAS)

- _暂无(项目刚初始化,尚未踩坑)_

---

## 里程碑 (DONE)

- _暂无_
