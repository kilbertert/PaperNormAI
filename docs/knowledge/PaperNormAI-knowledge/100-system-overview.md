# PaperNormAI 系统总览

## 1. 文档目的

本文件用于建立 PaperNormAI 的系统级公共认知，回答以下问题：

1. PaperNormAI 当前要做的产品是什么。
2. 当前 MVP 的真实边界在哪里。
3. 系统的核心子系统是什么。
4. 当前仓库已经具备哪些 AI 工程基础设施。
5. 当前哪些内容是已存在事实，哪些仍是蓝图目标。

## 2. 覆盖范围

本文件覆盖：

- 产品目标
- MVP 范围
- 架构原则
- 目标工程结构
- 当前仓库状态
- 高层业务流程

## 3. 核心事实

截至当前版本，PaperNormAI 的产品定位已明确为：

- 面向学生的 AI 论文格式校准工具
- 重点解决 `.docx` 论文格式检测与自动修正问题
- 基于高校模板与规则引擎进行确定性校验
- 使用 AI 对复杂格式问题进行增强判断

截至当前版本，MVP 蓝图已明确以下边界：

- 当前 MVP 只做 Web 端
- 当前 MVP 只支持 `.docx`
- 规则引擎与模板系统是第一核心
- 后端采用模块化单体，而不是微服务
- 文档处理必须围绕中间文档模型
- 检测与修正采用 job 模型

截至当前版本，仓库中已存在的主要资产仍然是：

- AI 工程治理文档
- MVP 工程架构蓝图
- AI 工程协作体系蓝图
- knowledge-builder agent
- 知识治理规范

截至当前版本，业务代码骨架尚未系统落地，因此当前系统认知以蓝图和治理规则为主，而不是以业务代码事实为主。

## 4. 产品与范围总览

### 4.1 产品目标

PaperNormAI 的目标是帮助学生在提交论文前，快速识别并修正格式规范问题，减少手工排版成本。

当前聚焦的问题包括：

- 字体
- 字号
- 行距
- 段前段后
- 标题层级
- 页边距
- 参考文献格式
- 引用一致性

### 4.2 MVP 的单一核心闭环

当前 MVP 的目标不是覆盖多端，而是打通以下单一闭环：

```text
上传 `.docx`
  -> 选择模板
  -> 检测格式问题
  -> 生成报告
  -> 自动修正可修正问题
  -> 下载修正后文档
```

### 4.3 当前不进入 MVP 的范围

以下内容在当前蓝图中明确不进入首发范围：

- Word 插件
- 桌面客户端
- PDF 自动修正
- LaTeX 支持
- 多租户组织空间
- 复杂后台管理
- 团队协作流程

## 5. 系统核心子系统

### 5.1 规则引擎子系统

定位：第一核心。

职责：

- 处理确定性格式规范
- 基于模板动态加载规则
- 输出结构化违规结果
- 驱动自动修正链路

### 5.2 模板系统子系统

定位：第一核心资产。

职责：

- 定义高校论文格式规范
- 为规则引擎提供参数化规则集
- 支撑未来高校模板扩展

### 5.3 文档处理中间层

定位：业务基础层。

职责：

- 将 `.docx` 映射为稳定的中间文档模型
- 让规则引擎和修正引擎摆脱对 `python-docx` 原始对象的直接耦合

### 5.4 AI 增强层

定位：辅助增强层，而不是主引擎。

职责：

- 处理参考文献格式等高歧义任务
- 生成结构化建议
- 不直接承担底层文档结构修改

### 5.5 AI 工程协作层

定位：当前阶段已经在落地的外部工程系统。

职责：

- 管理 AI 行为边界
- 建立知识学习与知识沉淀机制
- 为后续功能开发提供前置认知系统

## 6. 目标工程结构与当前状态

### 6.1 蓝图目标结构

根据 MVP 工程架构蓝图，目标工程结构包括：

- `backend/`
- `clients/`
- `template-library/`
- `docs/architecture/`
- `docs/knowledge/`
- `.ai/`
- `.github/`

### 6.2 当前已落地结构

当前已确认存在：

- `.github/copilot-instructions.md`
- `.ai/agents/PaperNormAI-knowledge-builder.agent.md`
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`
- `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`
- 本轮建立的知识库骨架文档

### 6.3 当前未落地但已定义目标结构

当前尚未从代码层面系统确认的目标结构包括：

- `backend/app/core/`
- `backend/app/domain/`
- `backend/app/application/`
- `backend/app/infrastructure/`
- `backend/app/api/`
- `clients/apps/web/`
- `clients/packages/`
- `template-library/`

这意味着：

- 当前可以确定的是架构意图
- 当前尚不能把这些结构写成“代码已实现事实”

## 7. 高层业务流程

### 7.1 蓝图定义的主流程

当前蓝图定义的 PaperNormAI MVP 主流程为：

```text
用户上传 .docx
  -> 创建 document 记录
  -> 创建 validation job
  -> 解析 Word 文档为中间文档模型
  -> 选择模板（用户手选或系统推荐）
  -> 加载模板规则
  -> 执行规则引擎
  -> 对需要 AI 的规则发起增强检查
  -> 生成统一 ValidationReport
  -> 对可自动修正的问题生成 CorrectionPlan
  -> 应用修正并输出 corrected.docx
  -> 前端展示报告并提供下载
```

### 7.2 当前状态说明

截至当前版本，这条主流程主要存在于架构蓝图中，尚未在业务代码中系统落地。

因此当前知识库应将其记录为：

- **已确认的架构目标流程**
- 而不是“已实现流程”

## 8. 与其他文档的关联

- 前置文档：
  - `.github/copilot-instructions.md`
  - `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- 相关文档：
  - `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`
  - `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`
  - `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md`

## 9. 当前已知边界

1. 当前系统总览以蓝图和治理文档为主，不以业务代码为主。
2. 当前可以明确 AI 工程协作系统已经开始落地。
3. 当前还不能对后端、前端、模板库的具体代码结构做事实性描述。
4. 当前系统总览的首要任务是建立统一认知，不是穷尽实现细节。

## 10. 待确认问题

1. 业务代码骨架将以什么顺序正式落地。
2. `clients/` 目录会在何时替代旧的 `frontend/` 设想。
3. 模板库初版会先以何种文件格式落地（YAML、JSON 或混合）。
4. job 模型的首版实现会采用应用内后台任务还是独立队列。

## 11. 更新记录

**最近复核时间**：2026-04-28

**复核依据**：
- 代码范围：仓库根目录、`.github/`、`.ai/agents/`、`docs/architecture/`、`docs/knowledge/`
- 参考文档：
  - `README.md`
  - `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
  - `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`

**当前可信度**：高

**待确认点**：业务实现尚未开始，当前系统总览主要基于蓝图事实与现存治理资产。
