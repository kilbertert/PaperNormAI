# PaperNormAI 知识文档总入口

## 1. 文档目的

本文件是 PaperNormAI 知识库的导航总线，用来回答三个问题：

1. 我要理解什么主题，应该先读哪份文档？
2. 我要处理什么任务，应该先进入哪些知识入口？
3. 当前哪些知识已经存在，哪些知识还只是计划中的骨架？

## 2. 覆盖范围

本文件覆盖：

- 知识库文档导航
- 架构蓝图与知识文档的关系
- agent / skill 的推荐阅读顺序
- 模块、功能、流程与文档之间的映射关系

## 3. 核心事实

截至当前版本，仓库中已确认存在的 AI 协作文档有：

- `.github/copilot-instructions.md`
- `.ai/agents/PaperNormAI-knowledge-builder.agent.md`
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`
- `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`

截至当前版本，以下知识库骨架文档将在本轮建立：

- `000-doc-map.md`
- `100-system-overview.md`
- `700-capability-map.md`
- `900-learning-log.md`

截至当前版本，业务代码骨架（如 `backend/`、`clients/`、`template-library/`）仍主要存在于蓝图中，当前仓库尚未确认这些目录已经落地。

## 4. 文档导航

### 4.1 先读什么

#### 如果你要理解 PaperNormAI 的产品与工程架构（2026-05-03 更新）

按顺序阅读：

1. `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md` — 系统总览（架构已更新）
2. `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md` — 功能能力地图（Phase 1 & 2）
3. `docs/architecture/adr-001-005-architecture-decisions.md` — 关键架构决策
4. `docs/design/validation-report-datamodel.md` — ValidationReport 数据结构设计

#### 如果你要理解 AI 协作规则

按顺序阅读：

1. `.github/copilot-instructions.md`
2. `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`
3. `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`

#### 如果你要进行功能开发

按顺序阅读：

1. `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`
2. `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md`
3. `docs/architecture/adr-001-005-architecture-decisions.md`
4. 对应的 design 文档（如 `validation-report-datamodel.md`）

### 4.2 当前知识文档地图

| 文档 | 主题 | 当前状态 | 适用对象 |
|---|---|---|---|
| `.github/copilot-instructions.md` | AI 工程治理规则 | 已存在 | 所有 agent / skill |
| `docs/architecture/2026-04-28-mvp-engineering-blueprint.md` | MVP 工程架构 | 已存在 | 架构阅读、开发前置 |
| `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md` | AI 协作体系蓝图 | 已存在 | agent / skill 设计 |
| `docs/architecture/adr-001-005-architecture-decisions.md` | 关键架构决策（2026-05-03） | 已存在 | 开发前置 |
| `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md` | 知识治理规范 | 已存在 | knowledge-builder、维护者 |
| `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md` | 知识导航总入口 | 已存在 | 所有 agent / skill |
| `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md` | 系统总览（2026-05-03 更新） | 已存在 | knowledge-builder、开发前置 |
| `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md` | 功能能力地图（2026-05-03 更新） | 已存在 | 产品理解、开发前置 |
| `docs/design/validation-report-datamodel.md` | ValidationReport 数据结构设计 | 已存在 | 开发前置 |
| `docs/knowledge/PaperNormAI-knowledge/200-database-models.md` | 数据库模型蓝图 | 已存在 | 开发前置 |
| `docs/knowledge/PaperNormAI-knowledge/300-backend-kernel-services.md` | 后端核心服务蓝图 | 已存在 | 开发前置 |
| `docs/knowledge/PaperNormAI-knowledge/400-api-architecture.md` | API 架构蓝图 | 已存在 | 开发前置 |
| `docs/knowledge/PaperNormAI-knowledge/500-frontend-architecture.md` | 前端架构蓝图 | 已存在 | 开发前置 |
| `docs/knowledge/PaperNormAI-knowledge/600-domain-models.md` | 领域模型蓝图 | 已存在 | 开发前置 |
| `docs/knowledge/PaperNormAI-knowledge/800-cross-layer-call-chains.md` | 跨层调用链蓝图 | 已存在 | 开发前置 |
| `docs/knowledge/PaperNormAI-knowledge/900-learning-log.md` | 学习日志 | 已存在 | knowledge-builder |

## 5. 任务类型到阅读顺序的映射

### 5.1 总览学习任务

推荐读取：

1. `.github/copilot-instructions.md`
2. `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`
3. `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
4. `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`
5. `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`
6. `README.md`

### 5.2 功能开发前的就绪性判断

推荐读取：

1. `.github/copilot-instructions.md`
2. `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`
3. `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`
4. `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md`
5. `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`

### 5.3 后续专题学习任务

按主题增加的专题知识文档：

- 数据库专题 → `200-database-models.md` ✅
- 后端核心服务专题 → `300-backend-kernel-services.md` ✅
- API 专题 → `400-api-architecture.md` ✅
- 前端专题 → `500-frontend-architecture.md` ✅
- 领域模型专题 → `600-domain-models.md` ✅
- 跨层调用链专题 → `800-cross-layer-call-chains.md` ✅

## 6. 模块与文档映射

### 6.1 当前已存在模块映射

当前仓库中，已确认存在的非业务模块主要是：

- AI 治理模块 → `.github/copilot-instructions.md`
- AI 学习 agent 模块 → `.ai/agents/PaperNormAI-knowledge-builder.agent.md`
- 架构蓝图模块 → `docs/architecture/*`
- 知识治理模块 → `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`

### 6.2 目标业务模块映射（来自蓝图，尚待代码落地）

> 以下映射描述的是蓝图目标结构，不代表当前代码已全部存在。

| 目标模块 | 对应知识文档 | 当前状态 |
|---|---|---|
| `backend/app/domain/document/` | `600-domain-models.md` | 待建立知识，待落代码 |
| `backend/app/domain/template/` | `600-domain-models.md`、`700-capability-map.md` | 待建立知识，待落代码 |
| `backend/app/domain/validation/` | `300-backend-kernel-services.md`、`600-domain-models.md` | 待建立知识，待落代码 |
| `backend/app/domain/correction/` | `300-backend-kernel-services.md`、`600-domain-models.md` | 待建立知识，待落代码 |
| `backend/app/api/` | `400-api-architecture.md` | 待建立知识，待落代码 |
| `clients/apps/web/` | `500-frontend-architecture.md` | 待建立知识，待落代码 |
| `template-library/` | `700-capability-map.md`、后续模板专题文档 | 待建立知识，待落代码 |

## 7. 当前已知边界

1. 当前知识库仍处于骨架建设阶段。
2. 当前能够确认的内容，主要来自蓝图文档、治理文档和已建立的 agent 文档。
3. 业务代码骨架尚未系统落地，因此大量业务知识暂时只能记录为“目标结构”而不是“已实现事实”。
4. 当前 `000-doc-map.md` 的重点是建立稳定的导航入口，而不是穷尽业务模块细节。

## 8. 待确认问题

1. `backend/`、`clients/`、`template-library/` 等蓝图目标目录何时正式落地。
2. 后续 `PaperNormAI-feature-development.agent.md` 与各类 skill 文件的实际落盘路径和命名是否保持蓝图一致。
3. 后续是否需要把知识文档再细分到“规则引擎专题”“模板系统专题”等更细粒度层级。

## 9. 更新记录

**最近复核时间**：2026-04-28

**复核依据**：
- 代码范围：仓库根目录、`.github/`、`.ai/agents/`、`docs/architecture/`、`docs/knowledge/`
- 参考文档：
  - `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
  - `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`
  - `.ai/agents/PaperNormAI-knowledge-builder.agent.md`

**当前可信度**：高

**待确认点**：业务代码骨架尚未落地，当前大量模块映射仍属于蓝图目标态而非代码事实。
