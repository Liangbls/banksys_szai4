# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 课程项目：银行营销数据分析与预测系统 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI/CD · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构、测试、CI 与 CD,
以便 后续每次开发都能自动检查并自动部署。

验收标准:
- AC1: 从 `main` 开 feature 分支完成初始化,不直接 push main。
- AC2: 项目目录结构符合 `00-project-context.md` 第 3 节的地图。
- AC3: PR 触发 CI,至少包含 `ruff format --check .`、`ruff check .`、`pytest --cov=src --cov-fail-under=80`、`docker build`。
- AC4: CI 全绿后合并 main。
- AC5: 合并 main 自动触发 CD,部署后 Streamlit 健康检查(`/_stcore/health`)返回 200。
- AC6: 服务可通过 `http://<HOST>:8004` 访问。
- AC7: 完成后更新 `standards/PROGRESS.md`。

技术备注:
- 容器内 Streamlit 固定端口 8501,主机端口映射 8004(支持回退到 8014)。
- 数据文件通过 Docker volume 或构建时复制挂载;模型训练产出放 `models/` 不进 Git。

---

### US-2 数据分析交互页面 · 状态: Backlog

作为 **银行营销人员/数据分析师**,
我想要 在一个交互式 Web 页面中探索银行营销数据,
以便 直观了解数据全貌、特征分布和认购(subscribe)相关因素,辅助营销策略制定。

验收标准:
- AC1: Given 应用已启动,When 用户打开数据分析页面,Then 页面显示数据总览(总行数、总列数、各列数据类型、缺失值计数)。
- AC2: Given 数据总览区域,When 用户查看,Then 显示目标变量 `subscribe` 的分布(yes/no 计数与比例)。
- AC3: Given 用户选择某个数值型特征(如 age、duration、campaign),When 页面渲染,Then 显示该特征的描述性统计(均值、中位数、标准差、最小值、最大值)及直方图/箱线图。
- AC4: Given 用户选择某个类别型特征(如 job、marital、education),When 页面渲染,Then 显示该特征的频次分布柱状图及与 subscribe 的交叉分组比例。
- AC5: Given 用户选择两个数值特征,When 页面渲染,Then 显示散点图或相关性热力图。
- AC6: Given 页面加载中或数据为空,When 渲染,Then 显示友好的提示信息(非崩溃或白屏)。

技术备注:
- 使用 Streamlit + plotly/altair 实现交互式图表。
- 数据加载逻辑放 `src/data_loader.py`,分析计算逻辑放 `src/analysis.py`,页面仅做渲染与选择器。
- 数值型特征列表、类别型特征列表由代码自动识别,不硬编码列名。

---

### US-3 离线模型训练 · 状态: Backlog

作为 **数据科学家**,
我想要 基于历史营销数据离线训练一个认购预测分类模型,
以便 模型可保存并在在线预测系统中加载使用,达到可用水平的预测准确率。

验收标准:
- AC1: Given `train.csv` 数据存在,When 运行训练脚本,Then 完成数据预处理(缺失值处理、类别编码、特征标准化/归一化)。
- AC2: Given 预处理后的数据,When 训练模型,Then 输出模型在验证集上的 AUC ≥ 0.70。
- AC3: Given 训练完成,When 模型保存,Then 产出文件 `models/model.pkl`(或 joblib 格式),可被预测模块重新加载。
- AC4: Given 训练脚本,When 运行,Then 同时输出特征重要性排名(至少前 10 个重要特征)。
- AC5: Given 模型产物,When 通过 `src/predict.py` 加载,Then 可用单条样本数据完成推理并返回预测类别与概率。
- AC6: Given 数据路径可通过命令行参数或环境变量指定,When 在不同机器运行,Then 无需修改代码即可切换数据源。

技术备注:
- 训练脚本:`src/model_train.py`,可作为独立脚本运行(`python src/model_train.py --data-path <path>`).
- 模型推荐:先基线 LogisticRegression,再对比 RandomForest/XGBoost,选 AUC 最优者。
- 类别编码用 OrdinalEncoder 或 OneHotEncoder;目标变量 yes/no → 1/0。
- 训练脚本不依赖 Streamlit,纯 Python 可独立执行和测试。

---

### US-4 在线预测系统 · 状态: Backlog

作为 **银行客户经理**,
我想要 通过一个 Web 表单点选输入客户特征信息,点击预测按钮后立即获得该客户是否会认购定期存款的预测结果,
以便 在日常工作中快速筛选高意向客户,提升营销效率。

验收标准:
- AC1: Given 应用已启动且模型已加载,When 用户打开预测页面,Then 显示输入表单,各特征字段以合适控件呈现(数值用输入框/滑块,类别用下拉框/单选)。
- AC2: Given 用户填写完所有必填字段,When 点击「预测」按钮,Then 显示预测结果:「会认购」(绿色标记)或「不会认购」(灰色标记),并附带预测概率百分比。
- AC3: Given 用户未填写必填字段或填入非法值,When 点击预测,Then 表单显示具体字段的校验错误提示,不崩溃。
- AC4: Given 模型未加载或预测失败,When 用户点击预测,Then 显示友好错误提示(如"模型服务暂不可用,请联系管理员"),不暴露技术栈报错细节。
- AC5: Given 用户多次预测不同客户,When 每次预测完成,Then 历史预测记录以表格形式展示在页面下方(含输入特征摘要 + 结果 + 时间戳)。
- AC6: Given 预测页面,When 用户首次打开,Then 各字段有合理的默认值,允许用户直接点预测看到示例结果。

技术备注:
- 模型由 `src/predict.py` 加载,页面通过 Streamlit session_state 缓存模型实例,避免重复加载。
- 特征字段控件:数值型用 `st.slider` 或 `st.number_input`,类别型用 `st.selectbox`。
- 历史记录仅在当前 session 保留(不持久化),用 `st.dataframe` 展示。

---

## 5. 非功能需求

- **安全**:密钥只进 GitHub Secrets,不进 Git;预测服务不记录用户 IP 或敏感身份信息。
- **可维护**:一需求一小 PR,核心逻辑与 UI 分离(`src/` 放纯逻辑,`pages/` 放 Streamlit 渲染)。
- **可测试**:`src/` 中每个模块必须有对应 `tests/test_*.py`,核心函数覆盖率 ≥ 80%。
- **可部署**:CD 自动部署到服务器,部署后自动健康检查;容器内固定 8501,主机端口 8004(支持回退)。
- **性能**:单次预测响应 < 2 秒(不含首次模型加载)。
- **兼容性**:支持 Chrome/Edge 最近 2 个大版本。
