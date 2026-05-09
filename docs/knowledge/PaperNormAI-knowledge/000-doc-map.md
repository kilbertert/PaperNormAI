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

1. 前端（`clients/apps/web/`）目前仅有基础骨架，业务页面与交互尚未落地。
2. `template-library/` 仍以示例模板为主，尚未形成完整高校模板库。
3. 历史知识文档存在阶段性漂移风险，需在每个 Step 完成后执行四件套对账。

## 8. 待确认问题

1. Step 7 的优先方向：先做前端接入，还是先做 ValidationReport 深度持久化。
2. 是否将 `.ai/skills/*.md` 进一步落地为 IDE 原生可调度技能目录。

## 10. 三套基础设施闭环

```
Session 开始
  → 读 docs/progress.md（当前状态）
  → 读 handoff/BUILD-LOG.md（执行历史）
  → 读 docs/knowledge/PaperNormAI-knowledge/000-doc-map.md（知识状态）

开发执行
  → handoff/ 追踪（Arch→Bob→Richard）
  → .ai/ 知识库指导（专题文档 + skills）

Step 完成（Deploy Gate）
  → knowledge-sync skill
      ├─ 更新 docs/knowledge/PaperNormAI-knowledge/ 专题文档（200-800）
      ├─ 更新 docs/progress.md
      ├─ 写入 docs/knowledge/PaperNormAI-knowledge/900-learning-log.md
      ├─ 写入 docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md
      └─ 写入 docs/memory/YYYY-MM-DD.md

Bug 发现
  → docs/postmortem/ 写入
  → 教训回写 .ai/skills/ 或 copilot-instructions.md

下次 Session
  → 读 docs/progress.md（循环）
```

## 12. Step COMPLETE 对账清单

每次 `BUILD-LOG` 将 Step 标记为 `COMPLETE` 后，必须同步完成并人工勾选以下四件套：

| 对账项 | 必须动作 | 验收标准 |
|------|------|------|
| `progress.md` | 更新 Active Step/Status/Next Step | 与 BUILD-LOG 最新 Step 一致 |
| `900-learning-log.md` | 追加本次增量学习记录 | 包含触发原因、阅读范围、新事实、更新文档 |
| `910-skill-run-log.md` | 追加 skill 运行摘要 | 至少包含场景、输入、结论、关联文件 |
| `memory/YYYY-MM-DD.md` | 追加当日存档 | 记录今日完成、决策、卡点与下一步 |

未完成四件套，不进入下一 Step。

## 11. 更新记录

**最近复核时间**：2026-05-06

**重要变更（2026-05-06）：**
- 添加三套基础设施闭环图
- knowledge-sync skill 同时更新 progress.md 和 memory/
- postmortem 教训回写 .ai/skills/

**当前可信度**：高
