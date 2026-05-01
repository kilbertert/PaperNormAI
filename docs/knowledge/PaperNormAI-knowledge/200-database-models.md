# PaperNormAI 数据库模型知识

## 1. 文档目的

本文件用于记录 PaperNormAI 目标数据库模型的结构与约束，回答以下问题：

1. 核心业务实体有哪些，数据模型如何设计。
2. 各实体之间的关联关系与约束条件。
3. 当前数据库模型是蓝图目标还是已实现事实。

## 2. 覆盖范围

- 核心业务实体设计
- 实体关联关系
- 中间文档模型与数据库的关系
- job 模型与任务状态机

## 3. 核心事实

截至当前版本，PaperNormAI 数据库模型仍处于蓝图设计阶段，尚未在代码中系统落地。

当前可确认的蓝图设计方向包括：

- 文档实体与 job 模型是核心存储单元
- 模板实体与规则集是只读参考数据
- 校验结果与修正计划是结构化输出

## 4. 核心业务实体

### 4.1 Document（文档实体）

定位：核心业务实体，代表用户上传的论文文档。

属性设计：

- `id`：全局唯一标识（UUID）
- `user_id`：所属用户标识
- `original_filename`：原始文件名
- `file_path`：文件存储路径
- `file_hash`：文件 SHA256 哈希（用于去重）
- `uploaded_at`：上传时间
- `template_id`：关联的模板 ID（可空）
- `status`：文档状态（pending / processing / completed / failed）

约束：

- 每个用户可以上传多份文档
- 同一文件 hash 不应重复创建 Document 记录（去重检查）

### 4.2 Template（模板实体）

定位：第一核心资产，代表高校论文格式模板。

属性设计：

- `id`：全局唯一标识（UUID）
- `university`：高校名称
- `degree_type`：学历类型（本科/硕士/博士）
- `discipline`：学科分类
- `version`：模板版本号
- `rules`：规则集配置（JSON 或关联表）
- `file_path`：模板参考文件路径
- `is_active`：是否启用
- `created_at`：创建时间
- `updated_at`：更新时间

约束：

- 同一高校 + 学历类型 + 学科应有唯一模板
- 模板更新不应影响历史校验记录（版本追踪）

### 4.3 ValidationJob（校验任务实体）

定位：核心异步任务单元，对应一份文档的一次校验流程。

属性设计：

- `id`：全局唯一标识（UUID）
- `document_id`：关联文档 ID
- `template_id`：关联模板 ID
- `status`：任务状态（pending / running / completed / failed）
- `priority`：优先级（用于队列调度）
- `trigger_type`：触发类型（manual / auto）
- `started_at`：开始时间
- `completed_at`：完成时间
- `error_message`：错误信息（失败时记录）

约束：

- 一份文档可以创建多个校验任务（重跑场景）
- 同一时刻一个 document 只有一个 running 状态的 job

### 4.4 ValidationResult（校验结果实体）

定位：规则引擎的结构化输出。

属性设计：

- `id`：全局唯一标识（UUID）
- `job_id`：关联的任务 ID
- `rule_id`：命中的规则 ID
- `severity`：严重程度（error / warning / info）
- `element_path`：出错的文档元素路径
- `expected_value`：期望值
- `actual_value`：实际值
- `auto_fixable`：是否可自动修正
- `ai_enhanced`：是否经过 AI 增强判断
- `confidence`：置信度（AI 增强时记录）

约束：

- 一条结果对应一条具体的违规
- 结果必须关联到具体的 job 和 rule

### 4.5 CorrectionPlan（修正计划实体）

定位：自动修正的执行计划。

属性设计：

- `id`：全局唯一标识（UUID）
- `result_id`：关联的校验结果 ID
- `action_type`：修正动作类型（replace_style / adjust_spacing / normalize_citation 等）
- `target_path`：目标元素路径
- `original_value`：原始值
- `planned_value`：计划修正值
- `status`：修正状态（planned / approved / applied / skipped）
- `applied_at`：应用时间（成功时记录）
- `rollback_data`：回滚数据（JSON）

约束：

- 只有 `auto_fixable=true` 的 result 才会生成 correction plan
- 用户可以选择跳过部分修正

### 4.6 CorrectionJob（修正任务实体）

定位：修正执行的任务单元。

属性设计：

- `id`：全局唯一标识（UUID）
- `document_id`：关联文档 ID
- `plan_ids`：要应用的修正计划 ID 列表
- `status`：任务状态（pending / running / completed / failed）
- `output_path`：修正后的文档路径
- `started_at`：开始时间
- `completed_at`：完成时间

### 4.7 User（用户实体）

定位：系统用户。

属性设计：

- `id`：全局唯一标识（UUID）
- `email`：邮箱（登录账号）
- `password_hash`：密码哈希
- `nickname`：昵称
- `role`：角色（student / admin）
- `created_at`：注册时间
- `last_login_at`：最后登录时间

约束：

- email 全局唯一

### 4.8 AuditLog（审计日志实体）

定位：可审计性记录。

属性设计：

- `id`：全局唯一标识（UUID）
- `user_id`：操作用户 ID
- `action`：操作类型
- `entity_type`：操作对象类型
- `entity_id`：操作对象 ID
- `detail`：操作详情（JSON）
- `ip_address`：IP 地址
- `created_at`：操作时间

## 5. 关联关系图

```text
User (1) ─────< Document (N)
                    │
                    │
Document (1) ─────< ValidationJob (N)
                    │
                    │
ValidationJob (1) ─────< ValidationResult (N)
                    │
                    │
ValidationResult (1) ─────< CorrectionPlan (N)
                    │
                    │
CorrectionPlan (N) ─────> CorrectionJob (1)
                    │
                    │
Template (1) ─────< Document (N, optional)
Template (1) ─────< ValidationJob (N, optional)
```

## 6. 中间文档模型的数据库映射策略

### 6.1 当前设计约束

中间文档模型（ParsedDocument）是运行时对象，不直接持久化到数据库。

当前蓝图的映射策略：

- Document 实体存储原始文件路径和元数据
- ValidationResult 存储结构化的校验输出，但不存储完整解析树
- 完整的解析结果通过文件路径+版本管理

### 6.2 为什么这样设计

1. 中间文档模型是易变的（解析逻辑迭代）
2. 完整的解析树数据量大，不适合关系数据库存储
3. 审计需求只需要违规结果，不需要完整文档内容

## 7. job 模型与状态机

### 7.1 ValidationJob 状态机

```
pending ──> running ──> completed
              │
              └──────> failed
```

状态转换约束：

- `pending -> running`：任务被 worker 抢占时
- `running -> completed`：所有规则执行完毕且无异常
- `running -> failed`：执行中遇到不可恢复错误
- `failed` 状态可重试（重新创建 job）

### 7.2 CorrectionJob 状态机

```
planned ──> approved ──> running ──> completed
              │
              └────────────> skipped
```

## 8. 当前已知边界

1. 数据库模型当前处于蓝图设计阶段，尚未在代码中系统落地。
2. 具体使用哪种数据库（PostgreSQL / SQLite）尚未确定。
3. ORM 框架尚未选择（Pydantic + raw SQL？SQLAlchemy？）。
4. 迁移工具尚未选择（Alembic 已在目录蓝图中提及，但未确认）。

## 9. 与其他文档的关联

- 前置文档：
  - `100-system-overview.md`（系统级概述）
  - `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- 相关文档：
  - `300-backend-kernel-services.md`（后端核心服务依赖数据模型）
  - `400-api-architecture.md`（API 层依赖数据模型设计）
  - `600-domain-models.md`（领域模型与数据库模型的关系）

## 10. 待确认问题

1. PostgreSQL vs SQLite 的选型决策。
2. ORM 框架的选型决策（Pydantic + raw SQL vs SQLAlchemy vs Tortoise ORM）。
3. 模板规则集的具体存储格式（JSON 列？关联表？文件？）
4. AI 增强结果的存储策略（是否需要单独存储 AI 推断上下文）。
5. Document.file_hash 的去重检查是在数据库层还是应用层实现。

## 11. 更新记录

**最近复核时间**：2026-04-28

**复核依据**：
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`（数据库设计部分）
- `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`

**当前可信度**：中（蓝图设计阶段，尚未代码验证）

**待确认点**：具体 ORM 选型、数据库选型、存储格式需要进入实现阶段后确认。