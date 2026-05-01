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

- 当前已明确的是能力蓝图，而不是能力实现现状。
- 当前 MVP 核心能力围绕 `.docx` 检测与修正闭环展开。
- 当前多端能力（桌面端、Word 插件）已明确后置。
- 当前知识库自身也可以视为一种“AI 协作能力建设”，但它服务于产品开发，不属于终端用户产品能力。

## 4. 能力分类

### 4.1 用户侧产品能力

1. 文档接入能力
2. 模板选择能力
3. 格式检测能力
4. 报告呈现能力
5. 自动修正能力
6. 修正结果交付能力

### 4.2 系统侧基础能力

1. 中间文档模型能力
2. 规则引擎能力
3. 模板系统能力
4. AI 增强判断能力
5. 异步任务能力

### 4.3 工程协作能力

1. AI 治理能力
2. 知识学习能力
3. 知识沉淀能力
4. 技能化执行能力
5. 文档导航与日志审计能力

## 5. MVP 核心能力地图

| 能力 | 类型 | MVP 优先级 | 当前状态 | 目标落点模块 |
|---|---|---|---|---|
| `.docx` 上传 | 用户侧产品能力 | 高 | 蓝图已定义，未落代码 | `clients/apps/web/`、`backend/app/api/` |
| 文档解析为中间模型 | 系统侧基础能力 | 高 | 蓝图已定义，未落代码 | `backend/app/infrastructure/docx/`、`backend/app/domain/document/` |
| 模板选择 | 用户侧产品能力 | 高 | 蓝图已定义，未落代码 | `clients/apps/web/`、`backend/app/domain/template/` |
| 模板规则加载 | 系统侧基础能力 | 高 | 蓝图已定义，未落代码 | `backend/app/domain/template/`、`backend/app/domain/validation/` |
| 确定性格式检测 | 用户侧产品能力 | 高 | 蓝图已定义，未落代码 | `backend/app/domain/validation/` |
| 检测报告生成 | 用户侧产品能力 | 高 | 蓝图已定义，未落代码 | `backend/app/domain/validation/`、`backend/app/api/` |
| 自动修正可修正问题 | 用户侧产品能力 | 高 | 蓝图已定义，未落代码 | `backend/app/domain/correction/`、`backend/app/infrastructure/docx/` |
| 修正后文档下载 | 用户侧产品能力 | 高 | 蓝图已定义，未落代码 | `backend/app/api/`、`clients/apps/web/` |
| AI 参考文献增强检查 | 系统侧基础能力 | 中 | 蓝图已定义，未落代码 | `backend/app/infrastructure/ai/`、`backend/app/domain/validation/` |
| 异步 job 执行 | 系统侧基础能力 | 高 | 蓝图已定义，未落代码 | `backend/app/application/` |

## 6. 明确后置的能力地图

| 能力 | 当前状态 | 后置原因 |
|---|---|---|
| 桌面客户端 | 不进入当前 MVP | 先验证核心引擎闭环 |
| Word 插件 | 不进入当前 MVP | 先验证 Web 主链路 |
| PDF 自动修正 | 不进入当前 MVP | 文档结构复杂度高 |
| LaTeX 支持 | 不进入当前 MVP | 超出当前场景收敛范围 |
| 多租户组织空间 | 不进入当前 MVP | 当前重点不是协作平台 |
| 复杂后台管理 | 不进入当前 MVP | 当前重点不是运营后台 |
| 团队协作与审批流 | 不进入当前 MVP | 当前重点是单用户工具闭环 |

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

1. MVP 首批高校模板支持范围会如何收敛。
2. AI 增强能力是否会在 MVP 第一批就上线，还是后移到后续阶段。
3. 异步任务状态获取会优先采用轮询还是预留 WebSocket。
4. 后续是否需要单独拆出“模板系统能力地图”和“规则能力地图”。

## 11. 更新记录

**最近复核时间**：2026-04-28

**复核依据**：
- 代码范围：当前仓库结构与 AI 协作文档
- 参考文档：
  - `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
  - `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`
  - `README.md`

**当前可信度**：高

**待确认点**：多数产品能力仍处于蓝图态，尚未落入业务代码。
