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
- 用户上传自己的规范手册（spec_doc）和论文（thesis_doc），AI 从规范手册提取语义规则并对论文进行校验
- 使用 AI-Word-Skill 技术实现"只改文字，保留排版"的修正合并
- 模板系统作为 Fallback：当用户未上传规范手册时，使用系统内置规则

截至当前版本，MVP 分两个阶段：

- **Phase 1（当前实施）：** 字体、字号、段落、页边距等基础文本格式
- **Phase 2（后续）：** 公式、表格、插图格式检测与修正

截至当前版本，MVP 关键技术选型已确认：

| 组件 | 选型 | 理由 |
|------|------|------|
| 文档解析 | docling | 开源成熟，结构化输出能力强，作为 Python 库集成 |
| 规则提取 | AI 语义理解 | 规范文档无法结构化规则化提取 |
| 规则形态 | 抽象描述性规则 | 结构化规则无法覆盖全部规范内容 |
| 文档合并 | AI-Word-Skill | "只改文字，保留排版"完美契合需求 |
| 校验方式 | AI 语义校验 | 而非规则引擎比对 |

截至当前版本，MVP 蓝图已明确以下边界：

- 当前 MVP 只做 Web 端
- 当前 MVP 只支持 `.docx`
- 文档处理采用 docling 进行解析
- 后端采用模块化单体，而不是微服务
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

核心价值主张：**用户上传自己的规范手册，AI 理解规范并校验论文格式**

MVP Phase 1 聚焦的基础格式问题：

- 字体
- 字号
- 行距
- 段前段后
- 标题层级
- 页边距

MVP Phase 2 扩展到：

- 参考文献格式
- 引用一致性
- 公式格式
- 表格格式
- 插图格式

### 4.2 MVP 的单一核心闭环

```text
用户上传规范手册 (spec_doc) ──→ docling 解析 ──→ AI 提取语义规则
用户上传论文 (thesis_doc)   ──→ docling 解析
                                          ↓
                              AI 语义校验 ──→ ValidationReport
                                          ↓
                              Git-diff 风格展示差异
                                          ↓
                              用户手动编辑校正
                                          ↓
                              用户确认 ──→ AI-Word-Skill 合并输出 corrected.docx

Fallback：用户未上传 spec_doc → 使用系统内置规则（论文规范.md）
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
- 公式、表格、插图格式检测与修正（Phase 2）

## 5. 系统核心子系统

### 5.1 文档解析子系统

定位：第一核心基础设施。

职责：

- 使用 docling 作为 Python 库解析 `.docx` 文档
- 将 Word 文档转换为结构化中间表示
- 支持规范手册和论文文档两种输入的处理
- 暴露统一的文档结构供后续 AI 处理使用

### 5.2 AI 规则提取子系统

定位：第一核心。

职责：

- 接收规范手册的结构化解析结果
- 通过 AI 语义理解提取格式规则（抽象描述性规则，非结构化参数）
- 将规则持久化存储（用户级别），支持同一用户后续复用
- 为论文校验提供规则输入

### 5.3 AI 语义校验子系统

定位：第一核心。

职责：

- 接收论文文档的结构化解析结果
- 基于 AI 提取的语义规则进行校验
- 生成 ValidationReport，包含违规位置、原始内容、修正建议
- 提供 Git-diff 风格的差异展示数据

### 5.4 修正合并子系统

定位：第一核心。

职责：

- 接收用户确认的修正内容
- 使用 AI-Word-Skill 技术进行"只改文字，保留排版"合并
- 输出修正后的 `.docx` 文档
- 确保公式、表格、插图等元素样式原样保留（Phase 2）

### 5.5 模板系统子系统

定位：Fallback 机制。

职责：

- 当用户未上传规范手册时提供系统内置规则
- 系统内置规则来源：`论文规范.md`
- 与用户自定义规则同等处理流程

### 5.6 用户交互与编辑子系统

定位：用户体验层。

职责：

- 展示 Git-diff 风格校验报告
- 支持用户在最终保存前手动编辑修正内容
- 管理用户确认流程

### 5.7 AI 工程协作层

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

### 7.1 主流程（Phase 1）

```text
用户上传规范手册 (spec_doc)
  -> docling 解析为结构化文档
  -> AI 语义理解提取规则（抽象描述性规则）
  -> 规则持久化（用户级别）

用户上传论文 (thesis_doc)
  -> docling 解析为结构化文档
  -> AI 基于规则进行语义校验
  -> 生成 ValidationReport（含违规位置、原始内容、修正建议）
  -> Git-diff 风格展示差异

用户手动编辑校正
  -> 用户确认
  -> AI-Word-Skill 合并回 .docx（只改文字，保留排版）
  -> 输出 corrected.docx
```

**Fallback 流程：**
用户未上传 spec_doc → 使用系统内置规则（论文规范.md）→ 后续流程相同

### 7.2 关键技术说明

**Docling 集成：**
- 作为 Python 库集成到后端
- 统一解析 spec_doc 和 thesis_doc
- 输出结构化中间表示供 AI 处理

**AI-Word-Skill 集成：**
- 仅在用户确认后触发
- 实现”只改文字，保留排版”
- Phase 1 不处理公式/表格/插图节点

**规则存储：**
- 随用户 Session 存在
- 持久化以备同一用户后续复用
- 用户级别规则隔离

### 7.3 当前状态说明

截至当前版本，这条主流程主要存在于架构蓝图中，尚未在业务代码中系统落地。

因此当前知识库应将其记录为：

- **已确认的架构目标流程**
- 而不是”已实现流程”

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

1. docling 的具体 API 接口和使用方式需要实际集成验证
2. AI-Word-Skill 的集成方式和限制需要实际验证
3. 规则持久化的具体存储方案（数据库表结构）
4. 用户上传 spec_doc 和 thesis_doc 的 UI 流程细节
5. ValidationReport 的具体数据结构设计
6. 用户手动编辑的交互设计

## 11. 更新记录

**最近复核时间**：2026-05-03

**复核依据**：
- 代码范围：仓库根目录、`.github/`、`.ai/agents/`、`docs/architecture/`、`docs/knowledge/`、`论文规范.md`
- 与项目负责人确认的业务流程

**重要架构变更（2026-05-03）：**

1. **规则来源变更：** 从"系统预置模板"改为"用户上传规范手册 AI 提取"
2. **文档解析变更：** 从 `python-docx` 改为 `docling`
3. **修正合并方式：** 新增 AI-Word-Skill 集成
4. **模板系统重定位：** 从核心降级为 Fallback 机制

**当前可信度**：高

**待确认点**：业务实现尚未开始，当前系统总览主要基于蓝图事实与现存治理资产。
