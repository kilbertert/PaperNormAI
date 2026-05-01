# Feature Development Skill

> 本 skill 定义 PaperNormAI 功能开发的标准步骤和最佳实践。为 `PaperNormAI-feature-development` agent 提供开发指导。

## 1. 定位

Feature Development 是 `PaperNormAI-feature-development` 的辅助 skill。

当功能就绪检查通过后，使用本 skill 指导开发执行。

## 2. 开发阶段

### 阶段 1：理解功能

```
1. 读取功能对应的知识文档
2. 读取相关的 API 契约（400-api-architecture.md）
3. 读取相关的领域模型（600-domain-models.md）
4. 确认功能边界和依赖
```

### 阶段 2：设计实现

```
1. 分解为可验证的步骤
2. 识别需要 mock 的依赖
3. 设计测试用例
4. 写入 ARCHITECT-BRIEF.md 的 Builder Plan 节
5. 等待确认（如需要）
```

### 阶段 3：实现代码

按以下顺序实现：

```
1. 先写测试（测试驱动）
2. 实现基础设施层（如果需要）
3. 实现领域层（核心逻辑）
4. 实现应用层（用例编排）
5. 实现 API 层（endpoint）
```

### 阶段 4：验证

```
1. 运行单元测试
2. 运行集成测试（如果实现了 API）
3. 检查代码覆盖率（核心逻辑 > 80%）
4. 检查 linting 和类型检查
```

### 阶段 5：同步知识

```
1. 如果有非显而易见的决策，记录到知识文档
2. 更新 900-learning-log.md
3. 清理临时文件和注释
```

## 3. 各层实现规范

### 3.1 基础设施层（Infrastructure）

实现技术细节（数据库、文件存储、外部 API）。

原则：

- 实现 Domain 层定义的接口
- 不包含业务逻辑
- 提供技术实现，不做业务决策

示例：

```python
# backend/app/infrastructure/persistence/document_repository.py
from app.domain.repositories import IDocumentRepository
from app.domain.entities import Document

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

### 3.2 领域层（Domain）

实现核心业务逻辑和领域服务。

原则：

- 纯业务逻辑，无技术依赖
- 通过接口访问外部依赖（依赖反转）
- 包含业务规则，不包含用例编排

示例：

```python
# backend/app/domain/services/rule_engine.py
from app.domain.entities import ParsedDocument, Template, ValidationReport

class RuleEngine:
    def __init__(self, template_service: ITemplateService, ai_service: IAIEnhancementService):
        self.template_service = template_service
        self.ai_service = ai_service

    def validate(self, document: ParsedDocument, template: Template) -> ValidationReport:
        rules = template.get_rules()
        results = []

        for rule in rules:
            if rule.level == RuleLevel.L3:
                result = self._validate_with_ai(document, rule)
            else:
                result = self._validate_rule(document, rule)
            results.append(result)

        return ValidationReport(results=results)
```

### 3.3 应用层（Application）

编排领域服务，实现用例。

原则：

- 包含用例编排逻辑
- 管理事务边界
- 不包含业务规则（委托给 Domain）

示例：

```python
# backend/app/application/document_validation.py
class DocumentValidationUseCase:
    def __init__(self, rule_engine: RuleEngine, document_repo: IDocumentRepository):
        self.rule_engine = rule_engine
        self.document_repo = document_repo

    def execute(self, document_id: UUID, template_id: UUID) -> ValidationReport:
        document = self.document_repo.find_by_id(document_id)
        template = self.template_service.get_template(template_id)

        parsed = self.document_parser.parse(document.file_path)

        report = self.rule_engine.validate(parsed, template)

        self._save_validation_result(report)

        return report
```

### 3.4 API 层（API）

接收请求，调用应用服务，返回响应。

原则：

- 参数验证
- 错误转换
- 调用应用服务
- 格式化响应

示例：

```python
# backend/app/api/endpoints/validation.py
@router.post("/validations", status_code=202)
async def create_validation(request: ValidationCreateRequest) -> ValidationResponse:
    try:
        job = use_case.execute(request.document_id, request.template_id)
        return ValidationResponse(job_id=job.id, status=job.status)
    except DocumentNotFoundError:
        raise HTTPException(404, detail="Document not found")
    except TemplateNotFoundError:
        raise HTTPException(404, detail="Template not found")
```

## 4. 测试策略

### 4.1 单元测试

覆盖核心业务逻辑（Domain 层）。

```python
def test_rule_engine_l1_detects_font_mismatch():
    # Given
    engine = RuleEngine(template_service=mock_ts, ai_service=mock_ai)
    document = create_document_with_font("Times New Roman")
    template = create_template(require_font="宋体")

    # When
    results = engine.validate(document, template)

    # Then
    assert len(results) == 1
    assert results[0].rule_id == "font_name"
    assert results[0].severity == Severity.ERROR
```

### 4.2 集成测试

覆盖 API endpoint 和数据库操作。

```python
def test_upload_document_endpoint(tmp_path):
    # Given
    client = TestClient(app)
    file_content = generate_test_docx()
    (tmp_path / "test.docx").write_bytes(file_content)

    # When
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": open(tmp_path / "test.docx", "rb")}
    )

    # Then
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
```

## 5. 代码质量标准

| 标准 | 要求 |
|------|------|
| 测试覆盖率 | 核心逻辑 > 80% |
| Linting | 通过 flake8 / eslint |
| 类型检查 | 通过 mypy / TypeScript strict |
| 文档 | 公共接口有 docstring |

## 6. 常见模式

### 6.1 依赖注入模式

```python
# 不在 __init__ 中实例化，而是接收注入
class DocumentService:
    def __init__(
        self,
        repository: IDocumentRepository,
        parser: IDocumentParser,
        storage: IFileStorage
    ):
        self.repository = repository
        self.parser = parser
        self.storage = storage
```

### 6.2 工厂模式

```python
# 复杂对象的创建使用工厂
class RuleEngineFactory:
    @staticmethod
    def create(config: RuleEngineConfig) -> RuleEngine:
        template_service = TemplateService(config.template_dir)
        ai_service = OpenAIProvider(config.api_key)
        return RuleEngine(template_service, ai_service)
```

### 6.3 策略模式

```python
# 可替换的算法使用策略
class ValidationStrategy(Protocol):
    def validate(self, element: DocumentElement, rule: ValidationRule) -> ValidationResult

class L1ValidationStrategy:
    def validate(self, element, rule):
        # 确定性检查
        pass

class L3ValidationStrategy:
    def validate(self, element, rule):
        # AI 增强检查
        pass
```

## 7. 更新记录

**创建时间**：2026-05-01

**依据**：PaperNormAI MVP Engineering Blueprint、Layered Architecture Principles