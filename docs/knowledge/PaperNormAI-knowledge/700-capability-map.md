# PaperNormAI 功能能力地图

## 1. 文档目的

本文件用于建立 PaperNormAI 的功能能力地图，回答以下问题：

1. 当前产品能力按什么维度划分。
2. 每项能力落在哪些目标模块或子系统上。
3. 当前哪些能力已经进入蓝图，哪些能力已经落地，哪些还未开始。
4. 哪些能力属于 MVP 核心，哪些能力明确后置。

## 2. 覆盖范围

本文件覆盖：

- 产品能力分类
- MVP 核心能力
- 后置能力
- 能力到目标模块的映射
- 能力当前状态标记

## 3. 核心事实

截至当前版本：

- 架构已发生重大变更（2026-05-03）：规则来源从”系统预置模板”改为”用户上传规范手册 AI 提取”
- 当前 MVP 分两个阶段：Phase 1（基础文本格式）、Phase 2（公式/表格/插图）
- 关键技改：docling 替代 python-docx，AI-Word-Skill 实现只改文字保留排版
- 当前多端能力（桌面端、Word 插件）已明确后置
- 模板系统从核心降级为 Fallback 机制

## 4. 能力分类

### 4.1 用户侧产品能力

1. **规范手册上传能力** — 用户上传自己的格式规范手册（spec_doc）
2. **论文文档上传能力** — 用户上传毕业设计论文（thesis_doc）
3. **模板选择能力** — 用户未上传规范手册时，选择系统预置模板（Fallback）
4. **规则提取能力** — AI 从规范手册中语义理解提取规则
5. **格式检测能力** — AI 基于提取的规则对论文进行语义校验
6. **报告呈现能力** — Git-diff 风格展示检测结果（原始内容 vs 修正后内容）
7. **用户编辑能力** — 用户在确认前可手动编辑修正内容
8. **修正合并能力** — AI-Word-Skill 实现只改文字保留排版
9. **修正结果交付能力** — 用户确认后生成并下载 corrected.docx

### 4.2 系统侧基础能力

1. **Docling 文档解析能力** — 使用 docling 统一解析 spec_doc 和 thesis_doc
2. **AI 语义规则提取能力** — AI 将规范手册内容提取为抽象描述性规则
3. **AI 语义校验能力** — AI 基于语义规则对论文进行校验
4. **规则持久化能力** — 用户级别规则存储，支持后续复用
5. **AI-Word-Skill 合并能力** — 只改文字，保留原始 Word 排版
6. **异步任务能力** — 文档处理和 AI 调用的异步执行

### 4.3 工程协作能力

1. AI 治理能力
2. 知识学习能力
3. 知识沉淀能力
4. 技能化执行能力
5. 文档导航与日志审计能力

## 5. MVP 能力地图（Phase 1 & Phase 2）

### 5.1 Phase 1（当前实施）

| 能力 | 类型 | 当前状态 | 目标落点模块 |
|---|---|---|---|
| 规范手册上传 | 用户侧产品能力 | 蓝图已定义，未落代码 | `backend/app/api/`、`clients/apps/web/` |
| 论文文档上传 | 用户侧产品能力 | 蓝图已定义，未落代码 | `backend/app/api/`、`clients/apps/web/` |
| 模板选择（Fallback） | 用户侧产品能力 | 蓝图已定义，未落代码 | `clients/apps/web/`、`backend/app/domain/template/` |
| docling 文档解析 | 系统侧基础能力 | 蓝图已定义，未落代码 | `backend/app/infrastructure/docling/` |
| AI 语义规则提取 | 系统侧基础能力 | 蓝图已定义，未落代码 | `backend/app/domain/rules/`、`backend/app/infrastructure/ai/` |
| 规则持久化 | 系统侧基础能力 | 蓝图已定义，未落代码 | `backend/app/infrastructure/persistence/` |
| AI 语义校验（文本格式） | 系统侧基础能力 | 蓝图已定义，未落代码 | `backend/app/domain/validation/`、`backend/app/infrastructure/ai/` |
| Git-diff 报告展示 | 用户侧产品能力 | 蓝图已定义，未落代码 | `backend/app/api/`、`clients/apps/web/` |
| 用户手动编辑 | 用户侧产品能力 | 蓝图已定义，未落代码 | `clients/apps/web/` |
| AI-Word-Skill 合并 | 系统侧基础能力 | 蓝图已定义，未落代码 | `backend/app/infrastructure/docx/` |
| 修正后文档下载 | 用户侧产品能力 | 蓝图已定义，未落代码 | `backend/app/api/`、`clients/apps/web/` |
| 异步 job 执行 | 系统侧基础能力 | 蓝图已定义，未落代码 | `backend/app/application/` |

**Phase 1 覆盖的格式问题：** 字体、字号、行距、段前段后、标题层级、页边距

### 5.2 Phase 2（后续实施）

| 能力 | 类型 | 当前状态 | 后置原因 |
|---|---|---|---|
| 公式格式检测与修正 | 用户侧产品能力 | 蓝图已定义 | Phase 1 完成后实施 |
| 表格格式检测与修正 | 用户侧产品能力 | 蓝图已定义 | Phase 1 完成后实施 |
| 插图格式检测与修正 | 用户侧产品能力 | 蓝图已定义 | Phase 1 完成后实施 |
| 参考文献格式检测 | 用户侧产品能力 | 蓝图已定义 | Phase 1 完成后实施 |
| 引用一致性检测 | 用户侧产品能力 | 蓝图已定义 | Phase 1 完成后实施 |

## 6. 明确后置的能力地图

| 能力 | 当前状态 | 后置原因 |
|---|---|---|
| 桌面客户端 | 不进入当前 MVP | 先验证 Web 主链路 |
| Word 插件 | 不进入当前 MVP | 先验证 Web 主链路 |
| PDF 自动修正 | 不进入当前 MVP | 文档结构复杂度高 |
| LaTeX 支持 | 不进入当前 MVP | 超出当前场景收敛范围 |
| 多租户组织空间 | 不进入当前 MVP | 当前重点不是协作平台 |
| 复杂后台管理 | 不进入当前 MVP | 当前重点不是运营后台 |
| 团队协作与审批流 | 不进入当前 MVP | 当前重点是单用户工具闭环 |
| 公式/表格/插图格式检测与修正 | Phase 2 | Phase 1 完成后实施 |
| 参考文献格式检测 | Phase 2 | Phase 1 完成后实施 |
| 引用一致性检测 | Phase 2 | Phase 1 完成后实施 |

## 7. AI 工程协作能力地图

> 以下能力不直接属于终端产品能力，但属于当前工程阶段的关键基础设施。

| 能力 | 当前状态 | 主要落点 |
|---|---|---|
| AI 行为治理 | 已落地第一版 | `.github/copilot-instructions.md` |
| 知识学习 agent | 已落地第一版 | `.ai/agents/PaperNormAI-knowledge-builder.agent.md` |
| 知识治理规范 | 已落地第一版 | `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md` |
| 知识导航入口 | 本次建立 | `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md` |
| 系统总览认知 | 本次建立 | `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md` |
| 学习日志机制 | 本次建立 | `docs/knowledge/PaperNormAI-knowledge/900-learning-log.md` |
| 功能开发 agent | 尚未建立 | `.ai/agents/` |
| skill 模块体系 | 尚未建立 | `.ai/skills/` |

## 8. 能力到知识文档的映射

| 能力主题 | 首选知识文档 |
|---|---|
| 系统级理解 | `100-system-overview.md` |
| MVP 范围与边界 | `100-system-overview.md` + MVP 蓝图 |
| 功能优先级与后置能力 | `700-capability-map.md` |
| AI 协作规则 | `.github/copilot-instructions.md` + AI 协作蓝图 |
| 知识导航入口 | `000-doc-map.md` |
| 知识维护规则 | `010-knowledge-governance.md` |

## 9. 当前已知边界

1. 当前能力地图以蓝图定义为主，不能误写成实现状态。
2. 当前能力地图的主要价值是帮助未来的 agent 和 skill 判断任务是否超出 MVP 范围。
3. 当前尚未进入数据库、API、前端等专题能力细化阶段。
4. AI 工程协作能力和产品终端能力必须区分记录，避免混淆。

## 10. 待确认问题

1. Phase 1 具体落地顺序（是先做 docling 集成还是先做 AI 校验流程）
2. AI 语义规则的具体 prompt 设计
3. ValidationReport 的具体数据结构
4. 用户手动编辑的交互设计
5. Phase 2 的优先级排序（公式 vs 表格 vs 插图）

## 11. 更新记录

**最近复核时间**：2026-05-03

**复核依据**：
- 与项目负责人确认的业务流程（2026-05-03）
- 参考文档：
  - `论文规范.md`
  - AI-Word-Skill 项目：https://github.com/sgsss998/AI-Word-Skill.git
  - docling 项目：https://github.com/docling-project/docling.git

**重要架构变更（2026-05-03）：**

1. 规则来源从”系统预置模板”改为”用户上传规范手册 AI 提取”
2. 文档解析从 `python-docx` 改为 `docling`
3. 新增 AI-Word-Skill 用于修正合并
4. 模板系统降级为 Fallback 机制
5. MVP 分为 Phase 1（文本格式）和 Phase 2（公式/表格/插图）

**当前可信度**：高
