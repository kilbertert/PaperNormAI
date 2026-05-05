# PaperNormAI 知识文档总入口

## 1. 文档目的

本文件是 PaperNormAI 知识库的导航总线，回答三个问题：

1. 我要理解什么主题，应该先读哪份文档？
2. 我要处理什么任务，应该先进入哪些知识入口？
3. 当前哪些知识已经存在，哪些知识还只是计划中的骨架？

## 2. 覆盖范围

- 知识库文档导航
- 架构蓝图与知识文档的关系
- agent / skill 的推荐阅读顺序
- 模块、功能、流程与文档之间的映射关系

## 3. 核心事实（2026-05-06 更新）

截至当前版本，以下 AI 协作文档已确认存在：

- `.github/copilot-instructions.md`
- `.ai/agents/PaperNormAI-knowledge-builder.agent.md`
- `.ai/agents/PaperNormAI-feature-development.agent.md`
- `.ai/skills/issue-evaluator.md`
- `.ai/skills/feature-readiness.md`
- `.ai/skills/feature-development.md`
- `.ai/skills/fix-development.md`
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`
- `docs/architecture/adr-001-005-architecture-decisions.md`
- `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`

截至当前版本，**业务代码已系统落地**，主要模块包括：

| 模块 | 路径 | 状态 |
|------|------|------|
| 文档解析 | `backend/app/infrastructure/docling/` | ✅ 已实现 |
| AI 规则提取 | `backend/app/domain/services/rule_extraction_service.py` | ✅ 已实现 |
| AI 语义校验 | `backend/app/domain/services/semantic_validation_service.py` | ✅ 已实现 |
| 文档修正合并 | `backend/app/infrastructure/docx/document_merger.py` | ✅ 已实现 |
| 修正服务 | `backend/app/domain/services/correction_service.py` | ✅ 已实现 |
| Spec 校验 API | `backend/app/api/endpoints/spec_validation.py` | ✅ 已实现 |
| 规则持久化 | `backend/app/infrastructure/persistence/spec_session_repository.py` | ✅ 已实现 |
| AI Provider | `backend/app/infrastructure/ai/openai_provider.py` | ✅ 支持 DeepSeek/Ollama/OpenAI |

截至当前版本，Phase 1 核心链路已完成，Phase 2 表格/插图/公式解析已完成。

## 4. 文档导航

### 4.1 先读什么

#### 如果你要理解 PaperNormAI 的产品与工程架构

1. `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`
2. `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md`
3. `docs/architecture/adr-001-005-architecture-decisions.md`
4. `docs/progress.md`

#### 如果你要进行功能开发（Bob 角色）

1. `handoff/ARCHITECT-BRIEF.md` — 当前步骤任务
2. `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`
3. 对应专题文档（200-800）
4. 运行 `.ai/skills/feature-readiness.md`

#### 如果你是 Arch 开始新会话

1. `handoff/SESSION-CHECKPOINT.md`（如有）
2. `handoff/BUILD-LOG.md`
3. `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`（本文件）

#### 如果你要理解 AI 协作规则

1. `.github/copilot-instructions.md`
2. `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`
3. `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`

### 4.2 当前知识文档地图

| 文档 | 主题 | 状态 |
|------|------|------|
| `.github/copilot-instructions.md` | AI 工程治理规则 | ✅ 已存在 |
| `docs/architecture/2026-04-28-mvp-engineering-blueprint.md` | MVP 工程架构 | ✅ 已存在 |
| `docs/architecture/adr-001-005-architecture-decisions.md` | 关键架构决策 | ✅ 已存在 |
| `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md` | 知识导航总入口 | ✅ 已存在 |
| `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md` | 系统总览 | ✅ 已存在（需更新） |
| `docs/knowledge/PaperNormAI-knowledge/200-database-models.md` | 数据库模型 | ✅ 已存在（需更新） |
| `docs/knowledge/PaperNormAI-knowledge/300-backend-kernel-services.md` | 后端核心服务 | ✅ 已存在（需更新） |
| `docs/knowledge/PaperNormAI-knowledge/400-api-architecture.md` | API 架构 | ✅ 已存在（需更新） |
| `docs/knowledge/PaperNormAI-knowledge/600-domain-models.md` | 领域模型 | ✅ 已存在（需更新） |
| `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md` | 功能能力地图 | ✅ 已存在（需更新） |
| `docs/knowledge/PaperNormAI-knowledge/800-cross-layer-call-chains.md` | 跨层调用链 | ✅ 已存在（需更新） |
| `docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md` | Skill 运行日志 | ✅ 已有真实记录 |
| `docs/progress.md` | 当前实施状态快照 | ✅ 实时更新 |
| `handoff/BUILD-LOG.md` | 构建历史 | ✅ 实时更新 |

## 5. 任务类型到阅读顺序的映射

### 5.1 总览学习任务

1. `.github/copilot-instructions.md`
2. `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`
3. `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md`
4. `docs/progress.md`

### 5.2 功能开发前的就绪性判断

1. `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`
2. `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md`
3. `handoff/BUILD-LOG.md`
4. 对应专题文档（200-800）

### 5.3 缺陷修复

1. `handoff/BUILD-LOG.md` — 了解已知问题
2. `docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md` — 查看历史修复记录
3. 对应专题文档

## 6. 模块与文档映射（已落地）

| 代码模块 | 对应知识文档 | 状态 |
|----------|-------------|------|
| `backend/app/infrastructure/docling/` | `300-backend-kernel-services.md` | ✅ 代码已实现 |
| `backend/app/domain/services/` | `300-backend-kernel-services.md`、`600-domain-models.md` | ✅ 代码已实现 |
| `backend/app/api/endpoints/spec_validation.py` | `400-api-architecture.md` | ✅ 代码已实现 |
| `backend/app/infrastructure/persistence/` | `200-database-models.md` | ✅ 代码已实现 |
| `backend/app/infrastructure/ai/` | `300-backend-kernel-services.md` | ✅ 代码已实现 |

## 7. 当前已知边界

1. 前端（`clients/apps/web/`）尚未实现，仍为蓝图目标。
2. `template-library/` 尚未实现。
3. 知识文档（200-800 系列）部分内容仍为蓝图描述，未反映最新代码实现。

## 8. 待确认问题

1. 知识文档（200-800 系列）何时系统更新为代码事实态（通过 knowledge-sync skill 逐步完成）。
2. 前端开发何时启动。

## 9. 更新记录

```
三人协作框架 (handoff/)          外部工程系统 (.ai/)
─────────────────────────────────────────────────────
Arch Session Start
  → 读 BUILD-LOG.md              → 读 000-doc-map.md（本文件）
  → 写 ARCHITECT-BRIEF.md        ← 知识库提供系统状态

Bob 开发
  → 读 ARCHITECT-BRIEF.md        → 读对应专题文档（200-800）
                                  → 运行 feature-readiness skill
                                  → 运行 feature-development skill

Richard 审核
  → 读 REVIEW-REQUEST.md
  → 写 REVIEW-FEEDBACK.md

Arch Deploy Gate
  → 更新 BUILD-LOG.md            → 运行 knowledge-sync skill
                                  → 更新知识文档（200-800）
                                  → 写入 910-skill-run-log.md
```

**知识库自动更新触发点：** Arch 在 Deploy Gate 完成后，运行 `.ai/skills/knowledge-sync.md`。

## 9. 更新记录

**最近复核时间**：2026-05-06

**重要变更（2026-05-06）：**
- 业务代码已系统落地，更新核心事实
- 添加两套系统协作关系图
- knowledge-sync skill 作为自动更新触发点

**当前可信度**：高
