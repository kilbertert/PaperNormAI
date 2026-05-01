# PaperNormAI 跨层调用链知识

## 1. 文档目的

本文件用于记录 PaperNormAI 各层之间的调用链设计，回答以下问题：

1. 请求从 API 到数据库的完整调用链是如何组织的。
2. 各层之间的依赖关系与边界在哪里。
3. 调用链中的关键路径有哪些。
4. 当前调用链设计是蓝图目标还是已实现事实。

## 2. 覆盖范围

- 典型调用链路径
- 层间依赖约束
- 数据传递格式
- 异常处理与传播
- 跨层调用时序

## 3. 核心事实

截至当前版本，PaperNormAI 跨层调用链仍处于蓝图设计阶段，尚未在代码中系统落地。

当前可确认的调用链设计方向：

- API Layer -> Application Layer -> Domain Layer -> Infrastructure Layer
- 依赖反转原则：Domain Layer 定义接口，Infrastructure Layer 实现
- 数据在各层间以领域对象传递

## 4. 分层架构概述

### 4.1 四层架构

```text
┌─────────────────────────────────────────┐
│              API Layer                   │
│   (FastAPI endpoints, request/response)  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           Application Layer              │
│      (Use Cases, Service Orchestration)  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│             Domain Layer                 │
│  (Entities, Domain Services, Value Objs) │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Infrastructure Layer             │
│ (Persistence, FileStorage, AI Provider)  │
└─────────────────────────────────────────┘
```

### 4.2 各层职责回顾

- **API Layer**：接收 HTTP 请求，参数验证，调用 Application Service，返回 HTTP 响应
- **Application Layer**：编排业务用例，事务边界，不包含业务逻辑
- **Domain Layer**：承载业务逻辑，领域模型，领域服务
- **Infrastructure Layer**：技术实现（数据库、文件、AI 服务）

## 5. 核心调用链详解

### 5.1 文档上传与校验调用链

```
Client
  │
  │ POST /api/v1/documents/upload (multipart/form-data)
  ▼
API Layer: DocumentUploadEndpoint
  │ 1. 接收文件，保存到临时目录
  │ 2. 调用 application_service.upload_document(...)
  ▼
Application Layer: DocumentApplicationService
  │ 1. 验证文件类型（.docx）
  │ 2. 计算文件 hash
  │ 3. 创建 Document 领域实体
  │ 4. 调用 domain_service.parse_document(...)
  ▼
Domain Layer: DocumentParser
  │ 1. 调用 infrastructure 层解析文档
  ▼
Infrastructure Layer: DocxParser
  │ 1. 使用 python-docx 读取文件
  │ 2. 构建 ParsedDocument
  ▼
Domain Layer: DocumentParser (return ParsedDocument)
  │
  │ 3. 存储 Document（通过 Persistence）
  ▼
Infrastructure Layer: DocumentRepository
  │ 1. 插入 DocumentModel 到数据库
  ▼
Application Layer (return Document)
  │
  │ 5. 创建 ValidationJob
  │ 6. 返回 Document 信息
  ▼
API Layer (return JSON: Document)
  │
  ▼
Client
```

### 5.2 校验任务执行调用链

```
Client
  │
  │ POST /api/v1/validations (document_id, template_id)
  ▼
API Layer: ValidationCreateEndpoint
  │ 1. 验证请求参数
  │ 2. 调用 application_service.create_validation_job(...)
  ▼
Application Layer: ValidationApplicationService
  │ 1. 获取 Document（通过 Repository）
  │ 2. 获取 Template（通过 TemplateService）
  │ 3. 创建 ValidationJob 实体
  │ 4. 存储 Job
  │ 5. 触发异步执行（JobScheduler.enqueue）
  ▼
JobScheduler (async)
  │
  ▼
Application Layer: ValidationApplicationService.execute_job(job_id)
  │ 1. 获取 Document, ParsedDocument
  │ 2. 调用 rule_engine.validate(document, template)
  ▼
Domain Layer: RuleEngine
  │ 1. 加载模板规则集
  │ 2. 对每个元素执行 L1/L2/L3 规则
  │ 3. 收集 ValidationResult
  ▼
Domain Layer: RuleEngine.validate()
  │ 对于 L3 规则：
  │ 4. 调用 AIEnhancementService.analyze(...)
  ▼
Infrastructure Layer: AIProvider
  │ 调用外部 AI API
  ▼
Domain Layer: AIEnhancementService (return AIResult)
  │
  │ 5. 生成 ValidationReport
  ▼
Application Layer
  │ 6. 存储 ValidationResult（通过 Repository）
  │ 7. 更新 Job 状态为 completed
  ▼
API Layer (polling): GET /api/v1/validations/{job_id}
  │
  ▼
Client (receive ValidationReport)
```

### 5.3 修正任务执行调用链

```
Client
  │
  │ POST /api/v1/corrections (document_id, plan_ids)
  ▼
API Layer: CorrectionCreateEndpoint
  │
  ▼
Application Layer: CorrectionApplicationService
  │ 1. 获取 Document
  │ 2. 获取 CorrectionPlan 列表
  │ 3. 创建 CorrectionJob
  │ 4. 触发异步执行
  ▼
JobScheduler (async)
  │
  ▼
Application Layer: execute_correction(job_id)
  │ 1. 获取 CorrectionPlan 列表
  │ 2. 调用 correction_executor.execute(document, plans)
  ▼
Domain Layer: CorrectionExecutor
  │ 1. 对每个 Plan 调用 apply_plan()
  │ 2. 生成修正后的 ParsedDocument
  │ 3. 调用 infrastructure 生成 corrected.docx
  ▼
Infrastructure Layer: DocxWriter
  │ 写入修正后的 Word 文件
  ▼
Domain Layer (return corrected ParsedDocument)
  │
  │ 4. 更新 Document 状态
  │ 5. 更新 Job 状态为 completed
  ▼
Client (GET /api/v1/corrections/{job_id})
```

## 6. 层间数据传递格式

### 6.1 请求到 API Layer

```python
# API Layer 接收原始请求
class DocumentUploadRequest(BaseModel):
    file: UploadFile
    template_id: Optional[UUID]

# 转换为 Application Layer DTO
class DocumentUploadDTO:
    file_path: Path
    template_id: Optional[UUID]
    user_id: UUID
```

### 6.2 Application Layer 到 Domain Layer

```python
# Application Layer 调用 Domain Service
class DocumentApplicationService:
    def upload_document(self, dto: DocumentUploadDTO) -> Document:
        # 构建领域对象
        document = Document(
            user_id=dto.user_id,
            original_filename=dto.file.filename,
            file_path=dto.file_path,
            # ...
        )
        # 调用领域服务
        parsed = self.document_parser.parse(dto.file_path)
        document.attach_parsed(parsed)
        return document
```

### 6.3 Domain Layer 到 Infrastructure Layer（依赖反转）

```python
# Domain Layer 定义接口
class IDocumentRepository(Protocol):
    def save(self, document: Document) -> None: ...
    def find_by_id(self, id: UUID) -> Optional[Document]: ...

# Infrastructure Layer 实现接口
class DocumentRepository(IDocumentRepository):
    def __init__(self, db: Database):
        self.db = db

    def save(self, document: Document) -> None:
        model = DocumentMapper.to_model(document)
        self.db.insert(model)

    def find_by_id(self, id: UUID) -> Optional[Document]:
        model = self.db.find(DocumentModel, id)
        return DocumentMapper.to_domain(model) if model else None
```

## 7. 异常处理与传播

### 7.1 异常层次

```python
# Domain Layer 异常（业务异常）
class DocumentNotFoundError(Exception): ...
class TemplateNotFoundError(Exception): ...
class ValidationError(Exception): ...

# Application Layer 异常（用例异常）
class UploadDocumentError(Exception): ...
class CreateValidationJobError(Exception): ...

# Infrastructure Layer 异常（技术异常）
class DatabaseError(Exception): ...
class FileStorageError(Exception): ...
class AIProviderError(Exception): ...
```

### 7.2 异常传播策略

```
Infrastructure Exception
    -> 转换为 Application Exception（隐藏技术细节）
    -> 转换为 API Exception（返回给客户端）
```

示例：

```python
# Infrastructure Layer
class DocumentRepository:
    def save(self, document: Document) -> None:
        try:
            self.db.insert(model)
        except DatabaseError as e:
            raise PersistenceError(f"Failed to save document: {e}") from e

# Application Layer
class DocumentApplicationService:
    def upload_document(self, dto) -> Document:
        try:
            return self._do_upload(dto)
        except PersistenceError as e:
            raise UploadDocumentError(f"Upload failed: {e}") from e

# API Layer
class DocumentEndpoint:
    def upload(self, request):
        try:
            return self.service.upload_document(dto)
        except UploadDocumentError as e:
            raise HTTPException(422, detail=str(e))
```

## 8. 依赖注入配置

### 8.1 依赖反转原则

Domain Layer 定义接口，Infrastructure Layer 实现接口。

Application Layer 通过依赖注入获取实现。

### 8.2 容器配置（示例）

```python
# infrastructure/containers.py
container = Container()

# Infrastructure
container.register(Database, lambda: PostgreSQLConnection())
container.register(FileStorage, lambda: LocalFileStorage())
container.register(AIProvider, lambda: OpenAIProvider())

# Repositories (Infrastructure implementations)
container.register(
    IDocumentRepository,
    lambda: DocumentRepository(container.resolve(Database))
)

# Domain Services
container.register(
    RuleEngine,
    lambda: RuleEngine(
        template_service=container.resolve(ITemplateService),
        ai_enhancement=container.resolve(AIEnhancementService)
    )
)

# Application Services
container.register(
    DocumentApplicationService,
    lambda: DocumentApplicationService(
        repository=container.resolve(IDocumentRepository),
        parser=container.resolve(IDocumentParser)
    )
)
```

## 9. 时序图：完整校验流程

```text
Client          API           App            Domain         Infra
  │              │             │               │               │
  │─POST upload──>│             │               │               │
  │              │─upload_doc->│               │               │
  │              │             │─parse_doc------------------->│
  │              │             │<────────parsed_doc───────────│
  │              │             │─save_doc-------------------->│
  │              │<──doc───────│               │               │
  │<─201 doc─────│             │               │               │
  │              │             │               │               │
  │─POST validat->│             │               │               │
  │              │─create_job->│               │               │
  │              │<──job_id───│               │               │
  │<─202 job_id──│             │               │               │
  │              │             │               │               │
  │ (polling)    │             │               │               │
  │─GET validat─>│             │               │               │
  │              │─get_job──>│               │               │
  │              │             │─validate_doc->│               │
  │              │             │               │─check L1/L2──>│
  │              │             │               │─check L3----->│
  │              │             │               │<──AI result───│
  │              │             │<──report──────│               │
  │              │<──report───│               │               │
  │<─200 report──│             │               │               │
```

## 10. 当前已知边界

1. 跨层调用链当前处于蓝图设计阶段，尚未在代码中系统落地。
2. 依赖注入容器的具体实现尚未选择（python-di？手动？）。
3. 异步任务的具体实现尚未选择（Celery？RQ？）。
4. 是否需要跨过程调用（如微服务拆分）尚未确定。

## 11. 与其他文档的关联

- 前置文档：
  - `100-system-overview.md`（系统级概述）
  - `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- 相关文档：
  - `200-database-models.md`（数据层的调用）
  - `300-backend-kernel-services.md`（Domain Service 设计）
  - `400-api-architecture.md`（API 层设计）
  - `600-domain-models.md`（领域模型设计）

## 12. 待确认问题

1. 依赖注入容器的选型（python-di / 手动 DI / 函数参数传递）。
2. 异步任务的选型（Celery / RQ / 数据库轮询）。
3. 是否需要引入 CQRS（命令查询分离）。
4. 是否需要引入事件总线（Event Bus）。

## 13. 更新记录

**最近复核时间**：2026-04-28

**复核依据**：
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`（调用链设计部分）
- `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`

**当前可信度**：中（蓝图设计阶段，尚未代码验证）

**待确认点**：依赖注入容器、异步任务选型需要在实现阶段确认。