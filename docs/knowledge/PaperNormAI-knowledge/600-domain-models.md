# PaperNormAI 领域模型知识

## 1. 文档目的

本文件用于记录 PaperNormAI 核心领域模型的设计与约束，回答以下问题：

1. 核心领域实体有哪些，它们的职责是什么。
2. 领域服务如何设计，边界在哪里。
3. 领域模型与数据库模型的关系。
4. 当前领域模型是蓝图目标还是已实现事实。

## 2. 覆盖范围

- 核心领域实体（Document, Template, ValidationRule 等）
- 领域服务（RuleEngine, TemplateService 等）
- 值对象（ElementPath, StyleDefinition 等）
- 领域事件（如果采用事件驱动）
- 领域服务与基础设施的边界

## 3. 核心事实

截至当前版本，PaperNormAI 领域模型仍处于蓝图设计阶段，尚未在代码中系统落地。

当前可确认的领域模型设计方向：

- Document 是核心领域实体，代表用户上传的论文
- Template 是规则集的载体，为 RuleEngine 提供参数
- 中间文档模型（ParsedDocument）是领域与基础设施的桥梁
- RuleEngine 是核心领域服务，执行规则校验

## 4. 核心领域实体

### 4.1 Document（文档）

定位：核心领域实体，代表用户上传的论文文档。

职责：

- 承载文档的元数据
- 关联模板和校验任务
- 追踪文档状态变更

属性：

```python
@dataclass
class Document:
    id: UUID
    user_id: UUID
    original_filename: str
    file_path: Path
    file_hash: str
    template_id: Optional[UUID]
    status: DocumentStatus
    uploaded_at: datetime
    updated_at: datetime
```

状态机：

```python
class DocumentStatus(Enum):
    PENDING = "pending"       # 刚上传，未处理
    PROCESSING = "processing" # 正在校验或修正
    COMPLETED = "completed"   # 处理完成
    FAILED = "failed"         # 处理失败
```

### 4.2 Template（模板）

定位：核心领域资产，定义论文格式规范。

职责：

- 封装规则集
- 为 RuleEngine 提供校验参数
- 支撑高校差异化需求

属性：

```python
@dataclass
class Template:
    id: UUID
    university: str
    degree_type: DegreeType
    discipline: str
    version: str
    rules: List[ValidationRule]
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### 4.3 ValidationRule（校验规则）

定位：规则引擎的执行单元。

职责：

- 定义单一格式规范
- 提供校验逻辑
- 标记修正能力

属性：

```python
@dataclass
class ValidationRule:
    id: str
    name: str
    level: RuleLevel  # L1 / L2 / L3
    description: str
    severity: Severity  # error / warning / info
    auto_fixable: bool
    params: Dict[str, Any]  # 规则参数（从模板传入）
    check_fn: Callable[[ParsedDocument, Dict], ValidationResult]
```

### 4.4 ParsedDocument（中间文档模型）

定位：**领域与基础设施的桥梁**，让核心逻辑摆脱 python-docx 耦合。

职责：

- 提供统一的文档访问接口
- 包含所有元素的结构化信息
- 支持序列化和路径定位

属性：

```python
@dataclass
class ParsedDocument:
    metadata: DocumentMetadata
    elements: List[DocumentElement]
    styles: Dict[str, StyleDefinition]
    parsed_at: datetime
    parser_version: str

@dataclass
class DocumentMetadata:
    title: Optional[str]
    author: Optional[str]
    word_count: int
    page_count: int

@dataclass
class DocumentElement:
    path: ElementPath  # 定位违规位置
    type: ElementType  # paragraph / heading / table / etc.
    content: str
    style: Optional[str]
    properties: ElementProperties

@dataclass
class ElementPath:
    # 用于精确定位文档中的元素
    # 例如：paragraph[3]/run[0]
    path: str

@dataclass
class ElementProperties:
    font_name: Optional[str]
    font_size: Optional[int]
    line_spacing: Optional[float]
    paragraph_spacing_before: Optional[float]
    paragraph_spacing_after: Optional[float]
    # ... 其他格式属性
```

### 4.5 ValidationResult（校验结果）

定位：规则引擎的结构化输出。

职责：

- 记录单一违规事实
- 提供修正所需的信息
- 支持 AI 增强标注

属性：

```python
@dataclass
class ValidationResult:
    id: UUID
    rule_id: str
    element_path: ElementPath
    severity: Severity
    expected_value: str
    actual_value: str
    message: str  # 人类可读的错误消息
    auto_fixable: bool
    ai_enhanced: bool
    confidence: Optional[float]  # AI 增强时记录
    created_at: datetime

@dataclass
class ValidationReport:
    document_id: UUID
    template_id: UUID
    job_id: UUID
    results: List[ValidationResult]
    summary: ValidationSummary
    generated_at: datetime
```

### 4.6 CorrectionPlan（修正计划）

定位：自动修正的执行计划。

职责：

- 描述如何修正一个违规
- 记录原始值（用于回滚）
- 追踪修正状态

属性：

```python
@dataclass
class CorrectionPlan:
    id: UUID
    result_id: UUID
    action_type: CorrectionActionType
    target_path: ElementPath
    original_value: Any
    planned_value: Any
    status: CorrectionStatus
    created_at: datetime
    applied_at: Optional[datetime]

class CorrectionActionType(Enum):
    REPLACE_STYLE = "replace_style"
    ADJUST_SPACING = "adjust_spacing"
    NORMALIZE_CITATION = "normalize_citation"
    # ... 其他修正类型

class CorrectionStatus(Enum):
    PLANNED = "planned"
    APPROVED = "approved"
    APPLIED = "applied"
    SKIPPED = "skipped"
```

## 5. 领域服务

### 5.1 RuleEngine（规则引擎服务）

定位：**核心领域服务**。

职责：

- 加载模板规则集
- 协调 L1/L2/L3 规则执行
- 调用 AI 增强服务
- 生成 ValidationReport

接口：

```python
class RuleEngine:
    def validate(
        self,
        document: ParsedDocument,
        template: Template
    ) -> ValidationReport:
        """对文档执行完整校验"""
        pass

    def validate_single(
        self,
        element: DocumentElement,
        rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """对单一元素执行单一规则"""
        pass
```

### 5.2 TemplateService（模板服务）

定位：**领域服务**，管理模板生命周期。

职责：

- 加载模板（支持缓存）
- 验证模板规则集
- 管理模板版本

接口：

```python
class TemplateService:
    def get_template(self, template_id: UUID) -> Template:
        """获取模板（带缓存）"""
        pass

    def list_templates(
        self,
        university: Optional[str] = None,
        degree_type: Optional[DegreeType] = None
    ) -> List[Template]:
        """筛选模板列表"""
        pass

    def validate_template(self, template: Template) -> bool:
        """验证模板规则集完整性"""
        pass
```

### 5.3 DocumentParser（文档解析服务）

定位：**基础设施服务**，但属于领域边界。

职责：

- 将 .docx 解析为 ParsedDocument
- 提取元素和样式信息

接口：

```python
class DocumentParser:
    def parse(self, file_path: Path) -> ParsedDocument:
        """解析 Word 文档"""
        pass

    def parse_element(self, element) -> DocumentElement:
        """解析单一元素"""
        pass
```

### 5.4 CorrectionExecutor（修正执行服务）

定位：**领域服务**，执行修正操作。

职责：

- 应用修正计划到 ParsedDocument
- 生成修正后的文档
- 验证修正结果

接口：

```python
class CorrectionExecutor:
    def execute(
        self,
        document: ParsedDocument,
        plans: List[CorrectionPlan]
    ) -> ParsedDocument:
        """应用修正计划"""
        pass

    def apply_plan(
        self,
        document: ParsedDocument,
        plan: CorrectionPlan
    ) -> ParsedDocument:
        """应用单一修正计划"""
        pass
```

## 6. 领域边界与依赖关系

### 6.1 领域边界

**领域层包含：**

- Document, Template, ValidationRule, ParsedDocument, ValidationResult, CorrectionPlan
- RuleEngine, TemplateService, CorrectionExecutor

**不属于领域层的（基础设施层）：**

- DocumentParser（依赖 python-docx）
- Persistence（数据库操作）
- FileStorage（文件存储）
- AIProvider（AI 服务调用）

### 6.2 领域层与基础设施层的边界

```
Domain Layer
    │
    │  ParsedDocument（领域对象，基础设施层实现解析）
    ▼
Infrastructure Layer
    ├── DocumentParser: .docx -> ParsedDocument
    ├── Persistence: 领域实体 -> 数据库
    ├── FileStorage: 存储/读取文件
    └── AIProvider: AI 服务调用
```

约束：

- 领域层不直接依赖基础设施实现
- 领域服务通过接口（依赖反转）与基础设施交互
- ParsedDocument 是领域概念，但由基础设施实现

## 7. 领域模型与数据库模型的关系

### 7.1 模型分离原则

领域模型和数据库模型是分离的：

1. **领域模型**：业务逻辑的语言，纯净无持久化逻辑
2. **数据库模型**：持久化语言，包含 ORM 映射逻辑

### 7.2 映射策略

```python
# 领域实体
class Document:
    pass

# 数据库实体（SQLAlchemy 模型）
class DocumentModel(Base):
    __tablename__ = "documents"
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    # ...

# Mapper
class DocumentMapper:
    @staticmethod
    def to_domain(model: DocumentModel) -> Document:
        return Document(...)

    @staticmethod
    def to_model(domain: Document) -> DocumentModel:
        return DocumentModel(...)
```

## 8. 当前已知边界

1. 领域模型当前处于蓝图设计阶段，尚未在代码中系统落地。
2. 具体使用 Python 什么方式定义领域模型（dataclass / Pydantic / attrs）尚未确定。
3. 是否采用事件驱动架构（Domain Events）尚未确定。
4. 领域服务是否采用策略模式设计尚未确定。

## 9. 与其他文档的关联

- 前置文档：
  - `100-system-overview.md`（系统级概述）
  - `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- 相关文档：
  - `200-database-models.md`（领域模型与数据库模型的关系）
  - `300-backend-kernel-services.md`（领域服务设计）
  - `800-cross-layer-call-chains.md`（领域服务间调用链）

## 10. 待确认问题

1. 领域模型的具体实现方式（dataclass / Pydantic / attrs）。
2. 是否需要 Domain Events（领域事件）支持。
3. RuleEngine 的 L1/L2/L3 规则如何配置化（JSON？YAML？代码内定义？）。
4. 修正操作是否需要支持批量回滚。

## 11. 更新记录

**最近复核时间**：2026-04-28

**复核依据**：
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`（领域模型设计部分）
- `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`

**当前可信度**：中（蓝图设计阶段，尚未代码验证）

**待确认点**：领域模型实现方式、事件驱动需求需要在实现阶段确认。