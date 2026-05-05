# Architect Brief
*Written by Architect. Read by Builder and Reviewer.*
*Overwrite this file each step — it is not a log, it is the current active brief.*

---

## Step 5 — Phase 2: 公式/表格/插图 解析支持

### 背景

Phase 1 已完成核心链路：
- DoclingDocumentParser 解析 DOCX → DocumentModel
- RuleExtractionService + SemanticValidationService 进行 AI 校验
- 390段落文档验证通过

Phase 2 需要扩展解析能力，支持：
- **表格 (Table)** — 检测表格标题、格式
- **插图 (Figure)** — 检测图标题、图注位置
- **公式 (Formula)** — 检测公式编号、公式格式

### 当前状态

**已支持：**
- 段落解析（text）
- 章节标题解析（section_header）
- 字体信息提取（bold, italic）

**待支持：**
- 表格解析（doc.tables）
- 插图/图片解析（doc.inline_shapes）
- 公式解析（OMML/MathML）

### 文档模型扩展

`DocumentModel` 需要添加：

```python
@dataclass
class TableInfo:
    """Table metadata and content."""
    rows: int
    cols: int
    caption: Optional[str] = None
    style: Optional[str] = None

@dataclass
class FigureInfo:
    """Figure/image metadata."""
    width: float
    height: float
    caption: Optional[str] = None

@dataclass
class FormulaInfo:
    """Formula/m equation metadata."""
    content: str  # OMML or text representation
    numbered: bool = False
    number: Optional[str] = None  # e.g., "(1)"

@dataclass
class DocumentModel:
    paragraphs: list[Paragraph]
    tables: list[TableInfo] = field(default_factory=list)
    figures: list[FigureInfo] = field(default_factory=list)
    formulas: list[FormulaInfo] = field(default_factory=list)
    # ... existing fields
```

### Docling 扩展

检查 `docling_core.types.doc.document` 是否有：
- `tables` 属性
- `pictures` 或 `images` 属性
- `formulas` 或 `equations` 属性

### 实现顺序

1. **Tables** — 最常用，先实现
   - 提取行数、列数、表格内容
   - 提取表格标题（caption）
   - AI 校验表格格式规范

2. **Figures** — 图注检测
   - 提取图片尺寸、位置
   - 提取图标题
   - 检测图注与正文引用的一致性

3. **Formulas** — 公式编号
   - 提取公式内容
   - 提取公式编号
   - 检测编号格式（如 "(1)" vs "1."）

### Definition of Done

- [ ] `DocumentModel` 扩展 `tables`、`figures`、`formulas` 字段
- [ ] `DoclingDocumentParser` 提取表格数据
- [ ] 表格校验规则可配置
- [ ] AI 可基于表格信息给出格式建议
- [ ] 单元测试覆盖

### 约束

1. **不破坏现有链路** — 新字段为可选，现有功能不受影响
2. **与 ViolationCategory 对齐** — TABLE, FIGURE, FORMULA 已定义
3. **可渐进增强** — 先解析基本字段，后续可扩展 caption/style 检测

---

## Builder Plan
*[Builder fills this in]*

Architect approval: [ ] Approved / [ ] Redirect — see notes below