# PaperNormAI 数据库模型知识

## 1. 文档目的

记录当前代码中已经落地的数据库模型、关系和存储边界，作为后端实现与知识库对齐的事实源。

## 2. 覆盖范围

- SQLAlchemy 模型（`backend/app/infrastructure/persistence/models.py`）
- 主要 Repository 实现
- 任务状态字段与持久化边界

## 3. 核心事实（代码事实态）

1. 数据层已采用 SQLAlchemy，并已落地核心表结构。  
2. `users / documents / templates / validation_jobs / validation_results / correction_plans / correction_jobs / spec_sessions / audit_logs` 均已在模型层定义。  
3. `SpecSessionModel` 已替换内存字典，支持规则会话持久化。  
4. 当前实现同时考虑 PostgreSQL 类型与 SQLite 兼容场景（如 `spec_sessions.user_id` 使用 `String(36)`）。

## 4. 已落地模型

### 4.1 用户与文档

- `UserModel`：邮箱唯一索引、密码哈希、角色、登录时间。  
- `DocumentModel`：文档元数据、文件 hash、关联用户与模板、状态字段。  
- 关系：`UserModel.documents`、`DocumentModel.user/template/validation_jobs`。

### 4.2 模板与规则存储

- `TemplateModel`：`university/degree_type/discipline/version/is_active`。  
- 规则集使用 `rules_json`（`Text`）存储。  
- `TemplateRepository` 支持 `find_active/find_by_university/find_by_discipline`。

### 4.3 校验链路

- `ValidationJobModel`：`pending/running/completed/failed` 状态与时间字段。  
- `ValidationResultModel`：违规明细、严重级别、AI 增强标记与置信度。  
- 关系：`ValidationJobModel.results`。

### 4.4 修正链路

- `CorrectionPlanModel`：修正动作、目标路径、原值与计划值、状态。  
- `CorrectionJobModel`：修正任务状态、输出路径、`plan_ids_json`。

### 4.5 规则会话与审计

- `SpecSessionModel`：`session_id` 主键，持久化 `rules_json` 与 `summary_json`。  
- `AuditLogModel`：审计动作、实体类型、细节 JSON、时间索引。

## 5. 关系概览

```text
users (1) -> documents (N)
templates (1) -> documents (N)
documents (1) -> validation_jobs (N)
templates (1) -> validation_jobs (N)
validation_jobs (1) -> validation_results (N)
validation_results (1) -> correction_plans (N)
documents (1) -> correction_jobs (N)
```

## 6. Repository 落地状态

- 已实现：`DocumentRepository`、`TemplateRepository`、`UserRepository`、`SpecSessionRepository`。  
- 已支持：保存、查询、更新、删除（或软删除）、统计等核心操作。  
- `SpecSessionRepository` 已用于 `spec_validation` 端点读写。

## 7. 当前已知边界

1. `ValidationReport` 的完整违规明细未以独立聚合对象长期存储，目前以 `ValidationResultModel` 明细 + 统计返回为主。  
2. `plan_ids_json/rules_json/summary_json` 仍为 JSON 文本列，后续可评估结构化拆表。  
3. 部分模型使用 PostgreSQL UUID 方言，跨 SQLite/PG 的一致性仍需持续验证。

## 8. 与其他文档的关联

- 前置文档：`100-system-overview.md`  
- 相关文档：`300-backend-kernel-services.md`、`400-api-architecture.md`、`600-domain-models.md`

## 9. 待确认问题

1. 是否将 `ValidationReport` 升级为独立持久化聚合。  
2. 是否将 `rules_json`、`summary_json` 拆分为结构化表。  
3. 后续生产环境数据库是否固定 PostgreSQL 并统一 UUID 策略。

## 10. 更新记录

**最近复核时间**：2026-05-06  
**复核依据**：
- `backend/app/infrastructure/persistence/models.py`
- `backend/app/infrastructure/persistence/document_repository.py`
- `backend/app/infrastructure/persistence/template_repository.py`
- `backend/app/infrastructure/persistence/spec_session_repository.py`

**当前可信度**：高  
**待确认点**：JSON 字段结构化与跨数据库兼容策略。
