# PaperNormAI 后端核心服务知识

## 1. 文档目的

记录后端核心服务当前已落地的职责、边界与关键实现，避免继续按蓝图态描述。

## 2. 覆盖范围

- `RuleExtractionService`、`SemanticValidationService`
- `RuleEngine`、`AIEnhancementService`
- `CorrectionService`、`CorrectionExecutor`
- `DoclingDocumentParser`、`DocumentParser`
- 持久化服务与后台任务入口

## 3. 核心事实（代码事实态）

1. 后端主框架已落地为 FastAPI。  
2. 规则校验链路存在两套：  
   - Spec 驱动语义校验链路（Docling + AI 服务）  
   - 模板驱动规则引擎链路（RuleEngine L1/L2/L3）  
3. 文档修正链路已落地：`CorrectionService`（文本替换合并）与 `CorrectionExecutor`（结构化修正计划）并存。  
4. 规则会话持久化已从内存切换为 `SpecSessionRepository` + `SpecSessionModel`。

## 4. 核心服务现状

### 4.1 文档解析服务

- `DoclingDocumentParser`：用于 spec/论文语义链路，产出 `DocumentModel`。  
- `DocumentParser`：用于规则引擎与修正链路，产出 `ParsedDocument`。  
- 当前实现支持段落、结构、表格、图片、公式提取（Docling 路径）。

### 4.2 规则与校验服务

- `RuleExtractionService`：从规范文档提取抽象规则文本。  
- `SemanticValidationService`：基于规则与段落信息做 AI 语义校验，产出 `ValidationReport`。  
- `RuleEngine`：面向模板规则执行 L1/L2/L3，输出 `ValidationResult` 列表。  
- `AIEnhancementService`：可启停，L3 规则增强入口。

### 4.3 修正服务

- `CorrectionService`：基于 `ValidationReport` 的建议修正做文本层合并。  
- `CorrectionExecutor`：处理 `CorrectionPlan`，结合 `DocumentWriter` 输出修正文档。  
- `DocumentMerger`：承载 AI-Word-Skill 风格的文档修正合并实现。

### 4.4 持久化与任务

- Repository：`Document/Template/User/SpecSession` 已有 SQLAlchemy 实现。  
- 后台任务：`validations.py` 与 `corrections.py` 通过 `BackgroundTasks` 触发异步执行。  
- 任务表：`validation_jobs`、`correction_jobs` 已落地状态字段和时间字段。

## 5. 服务边界

1. API 层负责鉴权、参数校验、响应组装，不承载核心业务规则。  
2. 领域服务层负责规则判定与修正策略。  
3. 基础设施层负责解析器、AI Provider、数据库与文件存储。  
4. 当前代码中仍存在少量跨层耦合（例如 endpoint 内直接拼装部分模型/流程），后续可逐步收敛。

## 6. 当前已知边界

1. 后台任务目前基于 FastAPI `BackgroundTasks`，未引入专用队列中间件。  
2. 语义校验结果以报告对象返回，深度持久化仍可继续增强。  
3. 规则引擎与语义校验存在并行链路，未来可进一步统一编排入口。

## 7. 与其他文档的关联

- 前置文档：`100-system-overview.md`  
- 相关文档：`200-database-models.md`、`400-api-architecture.md`、`600-domain-models.md`、`800-cross-layer-call-chains.md`

## 8. 待确认问题

1. 是否将后台任务升级到 Celery/RQ 等独立任务系统。  
2. 规则引擎链路与 spec 语义链路是否在应用层统一调度。  
3. `DocumentParser` 与 `DoclingDocumentParser` 的职责长期边界是否维持双轨。

## 9. 更新记录

**最近复核时间**：2026-05-06  
**复核依据**：
- `backend/app/domain/services/rule_extraction_service.py`
- `backend/app/domain/services/semantic_validation_service.py`
- `backend/app/domain/services/rule_engine.py`
- `backend/app/domain/services/correction_service.py`
- `backend/app/infrastructure/docling/parser.py`

**当前可信度**：高  
**待确认点**：后台任务机制与双轨校验链路收敛策略。
