# PROGRESS · banksys_szai4 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-06-07 · by AI)

- **阶段**:`开发完成` — 六步流程第⑥步(合并完成, CD 待服务器)
- **上一步完成**:PR #1 已人工合并 main → CD 自动触发 → CD 因无服务器 Secrets 预期失败
- **下一步 (TODO 第一条)**:有服务器后配置 `SSH_PRIVATE_KEY`/`SSH_HOST`/`SSH_USER`,重新跑 CD
- **阻塞项**:暂无服务器 (CD Secrets 未配)

---

## 待办清单 (TODO,按优先级)

### 第一批 TODO — 初始化阶段(本次会话) ✅ 已完成

- [x] 阅读 `standards/` 全部规范(README + 00~06)
- [x] 填写 `standards/00-project-context.md`(项目身份、技术栈、目录地图、质量门槛、部署取值)
- [x] 填写 `standards/01-requirements.md`(4 个用户故事,各含验收标准)
- [x] 初始化 `PROGRESS.md`(本文件)
- [x] **✋ 确认门:人类确认文档内容** ✓
- [x] 建仓:用 `gh` 创建 GitHub 仓库 `banksys_szai4`
- [x] 构建项目骨架:目录结构、`requirements.txt`、`requirements-dev.txt`、`.gitignore`、`Dockerfile`
- [x] 编写 CI workflow(`.github/workflows/ci.yml`)
- [x] 编写 CD workflow(`.github/workflows/cd.yml`)

### 第二批 TODO — US-1~US-4:全部功能实现 ✅ 已完成

- [x] 从 `main` 开 `feature/1-project-init` 分支
- [x] 实现 `app.py` —— Streamlit 主入口(含主页 + 页面导航)
- [x] 实现 `src/data_loader.py` —— 数据加载与预处理
- [x] 实现 `tests/test_data_loader.py` (18 tests)
- [x] 实现 `src/analysis.py` —— 分析计算函数
- [x] 实现 `pages/1_📊_data_analysis.py` —— 交互式分析页面(5个分析维度)
- [x] 实现 `tests/test_analysis.py` (11 tests)
- [x] 实现 `src/model_train.py` —— 离线训练(RandomForest AUC=0.8907)
- [x] 实现 `tests/test_model_train.py` (12 tests)
- [x] 实现 `src/predict.py` —— 模型推理
- [x] 实现 `pages/2_🔮_prediction.py` —— 在线预测页面(表单+结果+历史)
- [x] 实现 `tests/test_predict.py` (11 tests)
- [x] 本地自检:ruff format ✓ + ruff check ✓ + pytest 52 passed ✓ + cov 93% ✓
- [x] Push + 建 PR #1 → CI 全绿 ✓

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

- conda `UnicodeEncodeError`(� 字符):Windows 控制台 GBK 编码与 pytest 输出中的 Unicode 符号冲突。解决:用 `set PYTHONIOENCODING=utf-8` + 直接用 `python.exe` 而非 `conda run`。

---

## 里程碑 (DONE)

- [x] **2026-06-07** 项目文档完成 (`00/01/PROGRESS`) + 仓库创建 + 骨架搭建
- [x] **2026-06-07** US-1~US-4 全部代码实现: 4 个 src 模块 + 2 个页面 + app.py
- [x] **2026-06-07** 测试完成: 52 tests, 93% coverage, ruff 全绿
- [x] **2026-06-07** 模型训练: RandomForest AUC=0.8907, 模型已保存
- [x] **2026-06-07** CI 全绿 (lint-and-test 42s + docker-build 37s)
- [x] **2026-06-07** PR #1 merged → CD 触发 (预期失败: 无服务器 Secrets)
