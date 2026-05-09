# PaperNormAI 领域模型知识

## 1. 文档目的

记录当前代码中的领域实体、枚举与领域服务，明确“已实现事实”与“待演进边界”。

## 2. 覆盖范围

- 领域实体：`Document`、`Template`、`ValidationRule`、`ValidationResult`、`ValidationReport`、`CorrectionPlan`
- 语义报告实体：`ViolationDetail` 与相关枚举
- 领域服务：`RuleEngine`、`TemplateService`、`AIEnhancementService`、`CorrectionService`、`CorrectionExecutor`

## 3. 核心事实（代码事实态）

1. 领域实体已在 `backend/app/domain/entities/` 落地为 dataclass/enum。  
2. 存在两套“校验结果模型”：  
   - 规则引擎链路使用 `validation_result.py`  
   - 语义校验链路使用 `validation_report.py`  
3. `DocumentStatus`、`RuleLevel`、`Severity`、`CorrectionStatus` 等核心枚举已稳定使用。  
4. 领域模型与 ORM 模型通过 mapper/repository 分离，不直接耦合。

## 4. 已落地实体

### 4.1 Document

- 字段：`id/user_id/original_filename/file_path/file_hash/template_id/status/uploaded_at/updated_at`。  
- 行为：`attach_template`、`mark_processing`、`mark_completed`、`mark_failed`。

### 4.2 Template

- 字段：`university/degree_type/discipline/version/rules/is_active`。  
- 行为：`add_rule`、`get_active_rules`。

### 4.3 ValidationRule

- 关键字段：`id/name/description/level/severity/auto_fixable/params/check_fn`。  
- 分层：`RuleLevel.L1/L2/L3` 已在 RuleEngine 中实际使用。

### 4.4 ValidationResult/ValidationReport（规则引擎链路）

- `ValidationResult`：规则命中结果（含 `auto_fixable/ai_enhanced/confidence`）。  
- `ValidationReport`：`document_id/template_id/job_id/results` 聚合，并按属性实时计算 summary。

### 4.5 ViolationDetail/ValidationReport（语义校验链路）

- 语义链路报告定义在 `validation_report.py`。  
- 支持 `ViolationCategory`、`ViolationSeverity`、`TextLocation`、`user_modified_fix` 等字段，用于 AI 反馈与人工修订。

### 4.6 CorrectionPlan

- 字段：`result_id/action_type/target_path/original_value/planned_value/status/applied_at/rollback_data`。  
- 行为：`approve`、`apply`、`skip`。

## 5. 领域服务落地

1. `RuleEngine`：L1/L2/L3 规则编排与结果聚合。  
2. `TemplateService`：模板读取与规则转换。  
3. `AIEnhancementService`：L3 增强开关和分析结果封装。  
4. `CorrectionService`：基于语义报告执行文档级修正。  
5. `CorrectionExecutor`：基于 CorrectionPlan 执行结构化修正。

## 6. 领域边界（当前实践）

1. 领域层定义业务实体与规则语义。  
2. 持久化通过 repository + mapper 进入 `infrastructure/persistence`。  
3. 解析模型由 `infrastructure/docx`、`infrastructure/docling` 产生，再进入领域服务消费。  
4. 当前仍存在双模型并行（`ValidationResult` 与 `ViolationDetail`），属可接受的阶段性状态。

## 7. 当前已知边界

1. 校验报告模型尚未完全统一，跨链路字段语义需要进一步收敛。  
2. Domain Event 机制尚未引入。  
3. `CorrectionPlan` 与前端交互契约仍有细化空间。

## 8. 与其他文档的关联

- 前置文档：`100-system-overview.md`  
- 相关文档：`200-database-models.md`、`300-backend-kernel-services.md`、`800-cross-layer-call-chains.md`

## 9. 待确认问题

1. 两套报告模型是否在下一阶段合并为统一聚合。  
2. 是否引入领域事件以追踪状态流转。  
3. `CorrectionActionType` 是否需要与前端枚举进一步对齐。

## 10. 更新记录

**最近复核时间**：2026-05-06  
**复核依据**：
- `backend/app/domain/entities/document.py`
- `backend/app/domain/entities/template.py`
- `backend/app/domain/entities/validation_rule.py`
- `backend/app/domain/entities/validation_result.py`
- `backend/app/domain/entities/validation_report.py`
- `backend/app/domain/entities/correction_plan.py`

**当前可信度**：高  
**待确认点**：双报告模型收敛策略。
