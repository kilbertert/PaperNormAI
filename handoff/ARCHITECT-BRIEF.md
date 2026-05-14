# Architecture Brief — PaperNormAI

## Step 7 — ValidationReport 深度持久化

---

## 1. 背景与目的

Step 6A 架构修复完成后，Step 7 验证后端核心链路的收敛性。选择 ValidationReport 深度持久化作为目标，原因：
- 刚修复的是后端架构边界，最应该接着验证的也是后端核心链路
- ValidationReport 深度持久化会直接检验：领域模型是否稳定、数据库模型是否足够承载、API/Domain/Persistence 边界是否真正收敛

---

## 2. 架构门禁结论

| 门禁 | 结果 | 说明 |
|------|------|------|
| feature-readiness | ✅ Green | 知识文档足够、接口变化极小、回归面清晰有限 |
| architecture-check | 🟡 Yellow | API 层继续承担编排，直接调用 repository —— **MVP 例外** |

**Yellow 原因：** 不会新增 `domain → infrastructure` 违规，但会继续沿用 `API → infrastructure repository` 的务实捷径。

**例外条件：** 本轮允许 `spec_validation.py` 继续直接调用持久化仓储，但必须：
1. 在 BUILD-LOG 和本文档中明确记录"这是 MVP 例外"
2. 后续（Step 8+）下沉到 `application/` 层
3. 不以"架构已经这样了"为由拒绝修复

---

## 3. Definition of Done

### 数据库模型

```
ValidationReportModel:
  - report_id (PK, UUID)
  - session_id (FK → SpecSession, NOT NULL)
  - created_at (timestamp)
  - document_name (VARCHAR, nullable)
  - template_name (VARCHAR, nullable)
  - total_count / error_count / warning_count / info_count (INT)

ViolationDetailModel:
  - id (PK, UUID)
  - report_id (FK → ValidationReportModel)
  - category (VARCHAR)
  - severity (VARCHAR)
  - description (TEXT)
  - paragraph_index (INT)
  - text (TEXT)
  - original_content (TEXT, nullable)
  - suggested_fix (TEXT, nullable)
  - context_before (TEXT, nullable)
  - context_after (TEXT, nullable)
  - user_modified_fix (TEXT, nullable)
```

### API 变更

- `SpecValidationResponse` 追加 `report_id` 字段
- `POST /spec/validate-with-spec` 返回中携带 `report_id`

### 持久化职责

- API 编排层（`spec_validation.py`）负责调用持久化仓储
- Domain Service（`SemanticValidationService`）仅负责产出 `ValidationReport`
- 这是 MVP 务实落点，后续需下沉到 `application/` 层

### 明确不做

- 查询/回放接口
- RuleHitModel
- 前端消费完整报告
- 双模型统一重构（ValidationResult vs ViolationDetail）
- 模板校验链路改造
- 异步任务

### 验收标准

- [ ] `POST /spec/validate-with-spec` 返回 `report_id`
- [ ] 每次 spec 校验成功后，同步写入一条 `ValidationReport` 主记录
- [ ] `ValidationReport.violations` 全量落库，不丢字段
- [ ] 主记录统计字段与违规明细一致
- [ ] 不破坏现有 spec 链路 API 行为
- [ ] 不引入新的 `domain → infrastructure` 违规

---

## 4. 数据库迁移路径

- **开发环境：** SQLite + `create_all()`（新增表自动创建）
- **生产环境：** Alembic migration（不在 Step 7 范围内，记录为已知边界）

---

## 5. 影响文件清单

| 文件 | 操作 |
|------|------|
| `backend/app/infrastructure/persistence/models.py` | 新增 `ValidationReportModel` + `ViolationDetailModel` |
| `backend/app/api/endpoints/spec_validation.py` | 响应追加 `report_id`，调用新持久化仓储 |
| `backend/app/domain/entities/validation_report.py` | 确认可序列化（参考） |
| `backend/app/infrastructure/persistence/validation_report_repository.py` | 新建（可选，API 层直接调用 ORM） |

---

## 6. 下一步

等待"可以开始"确认后执行。

---

# Architecture Repair — Remove domain -> infrastructure dependencies

## Step 6A — Architecture Repair

---

## 1. 背景

在 Step 6 完成后，grill-me 审查发现当前代码库存在**系统性架构违规**：domain 层直接依赖 infrastructure 层，违反了 `api → application → domain → infrastructure` 的分层约束。

这些违规在实现时未被 skill 机制拦截，导致架构腐化已扩散至 7 个 service 文件。

---

## 2. 违规清单

### 清单说明

| 列 | 说明 |
|---|------|
| 文件 | 违规文件路径（相对于 `backend/app/`) |
| 违规依赖 | 具体 import 语句 |
| 问题性质 | 违规类型分类 |
| 修复方向 | 建议采用的修复模式 |

### 完整清单

| # | 文件 | 违规依赖 | 问题性质 | 修复方向 |
|---|------|---------|---------|---------|
| 1 | `domain/services/semantic_validation_service.py` | `from app.infrastructure.docling.document_model import DocumentModel` | domain → infrastructure (docling) | 改为 domain 抽象接口，由 application 层注入 |
| 2 | `domain/services/semantic_validation_service.py` | `from app.infrastructure.ai.openai_provider import OpenAIProvider` | domain → infrastructure (ai) | 改为 domain 抽象接口，由 application 层注入 |
| 3 | `domain/services/rule_extraction_service.py` | `from app.infrastructure.docling.document_model import DocumentModel` | domain → infrastructure (docling) | 改为 domain 抽象接口，由 application 层注入 |
| 4 | `domain/services/rule_extraction_service.py` | `from app.infrastructure.ai.openai_provider import OpenAIProvider` | domain → infrastructure (ai) | 改为 domain 抽象接口，由 application 层注入 |
| 5 | `domain/services/correction_service.py` | `from app.infrastructure.docx.document_merger import DocumentMerger` | domain → infrastructure (docx) | 改为 domain 抽象接口，由 application 层注入 |
| 6 | `domain/services/rule_engine.py` | `from app.infrastructure.docx.document_parser import ParsedDocument, DocumentElement` | domain → infrastructure (docx) | 改为 domain 抽象接口，由 application 层注入 |
| 7 | `domain/services/correction_executor.py` | `from app.infrastructure.docx.document_parser import ParsedDocument, DocumentElement` | domain → infrastructure (docx) | 改为 domain 抽象接口，由 application 层注入 |
| 8 | `domain/services/correction_executor.py` | `from app.infrastructure.docx.document_writer import DocumentWriter` | domain → infrastructure (docx) | 改为 domain 抽象接口，由 application 层注入 |
| 9 | `domain/services/ai_enhancement_service.py` | `from app.infrastructure.ai.openai_provider import OpenAIProvider` | domain → infrastructure (ai) | 改为 domain 抽象接口，由 application 层注入 |

**违规文件数：9 处 / 7 个 service 文件**

---

## 3. 问题性质分类

| 分类 | 涉及文件 | 根因 |
|------|---------|------|
| **AI Provider 泄露** | semantic_validation_service, rule_extraction_service, ai_enhancement_service | domain 层直接实例化 `OpenAIProvider()` |
| **Docling 模型泄露** | semantic_validation_service, rule_extraction_service | domain 层直接 import `DocumentModel` from infrastructure |
| **Docx Parser 模型泄露** | rule_engine, correction_executor | domain 层直接 import `ParsedDocument`, `DocumentElement`, `DocumentWriter` from infrastructure |
| **Infrastructure 具体实现泄露** | correction_service | domain 层直接 import `DocumentMerger` 具体实现 |

---

## 4. 架构修复模式

### 4.1 修复原则

```
违规：domain 直接依赖 infrastructure 实现
正确：domain 定义抽象接口（Protocol），application 层负责注入具体实现
```

### 4.2 需要新增的 Domain 抽象接口

| 抽象接口 | 位置 | 用途 |
|---------|------|------|
| `IDocumentParser` | `domain/services/interfaces.py` (新建) | 抽象文档解析行为 |
| `IAIProvider` | `domain/services/interfaces.py` (新建) | 抽象 AI 调用行为 |
| `IDocumentMerger` | `domain/services/interfaces.py` (新建) | 抽象文档合并行为 |
| `IDocumentWriter` | `domain/services/interfaces.py` (新建) | 抽象文档写入行为 |

### 4.3 修复后目标结构

```text
domain/services/
├── interfaces.py          # 新增：domain 抽象接口定义
├── semantic_validation_service.py   # 依赖 IDocumentParser + IAIProvider（接口）
├── rule_extraction_service.py      # 依赖 IDocumentParser + IAIProvider（接口）
├── correction_service.py            # 依赖 IDocumentMerger（接口）
├── rule_engine.py                   # 依赖 IDocumentParser（接口）
├── correction_executor.py           # 依赖 IDocumentParser + IDocumentWriter（接口）
├── ai_enhancement_service.py       # 依赖 IAIProvider（接口）
└── template_service.py              # ✅ 无违规，保持不变

application/
├── document_use_cases.py    # 注入具体实现到 domain service
├── validation_use_cases.py  # 注入具体实现到 domain service
```

---

## 5. 优先级排序

| 批次 | 文件 | 理由 |
|------|------|------|
| **P0 — 立即修** | `semantic_validation_service.py` | 涉及 AI Provider + Docling，核心链路 |
| **P0 — 立即修** | `rule_extraction_service.py` | 涉及 AI Provider + Docling，核心链路 |
| **P0 — 立即修** | `ai_enhancement_service.py` | 涉及 AI Provider，RuleEngine 依赖 |
| **P1 — 第二批** | `rule_engine.py` | RuleEngine 是校验核心，被 L3 规则依赖 |
| **P1 — 第二批** | `correction_executor.py` | 依赖 ParsedDocument + DocumentWriter |
| **P2 — 第三批** | `correction_service.py` | 依赖 DocumentMerger，边界清晰 |

---

## 6. 修复验收标准

### 6.1 硬性验收

- [ ] `domain/services/` 下所有 .py 文件，import 语句不包含 `app.infrastructure`
- [ ] 所有 domain service 通过 constructor 注入依赖（不接受 `from app.infrastructure.xxx import` 在模块级）
- [ ] `domain/services/interfaces.py` 存在且定义了所有需要的抽象接口
- [ ] `application/` 层负责实例化 infrastructure 实现并注入到 domain service

### 6.2 回归验收

- [ ] 所有 domain service 的公开方法行为不变（参数/返回值相同）
- [ ] `POST /spec/parse-spec` → `POST /spec/validate-with-spec` 链路仍然正常工作
- [ ] `POST /validations/` 链路仍然正常工作
- [ ] `POST /corrections/` 链路仍然正常工作
- [ ] 单元测试仍然通过（不因架构重构引人新失败）

### 6.3 架构门禁验收

- [ ] 新增 `architecture-check` skill（或 feature-readiness 增加架构检查维度）
- [ ] 后续所有 feature/fix 开发必须通过架构门禁才允许合并

---

## 7. 修复步骤

```
Step 6A.1 — 新建 domain/services/interfaces.py
           定义 IDocumentParser, IAIProvider, IDocumentMerger, IDocumentWriter

Step 6A.2 — 重构 ai_enhancement_service.py
           将 OpenAIProvider 改为 IAIProvider 接口，constructor 注入

Step 6A.3 — 重构 semantic_validation_service.py
           将 DocumentModel + OpenAIProvider 改为 IDocumentParser + IAIProvider 接口

Step 6A.4 — 重构 rule_extraction_service.py
           将 DocumentModel + OpenAIProvider 改为 IDocumentParser + IAIProvider 接口

Step 6A.5 — 重构 rule_engine.py
           将 ParsedDocument 改为 IDocumentParser 接口

Step 6A.6 — 重构 correction_executor.py
           将 ParsedDocument + DocumentWriter 改为 IDocumentParser + IDocumentWriter 接口

Step 6A.7 — 重构 correction_service.py
           将 DocumentMerger 改为 IDocumentMerger 接口

Step 6A.8 — 更新 application 层注入逻辑
           在 document_use_cases.py / validation_use_cases.py 中实例化具体实现并注入

Step 6A.9 — 运行回归测试
           验证所有链路仍然正常工作

Step 6A.10 — 更新相关知识文档
           200/300/600/800 刷新为代码事实态
```

---

## 8. 影响的专题知识文档

| 文档 | 需要更新的内容 |
|------|--------------|
| `200-database-models.md` | 不涉及（Persistence 层未违规） |
| `300-backend-kernel-services.md` | domain service 依赖注入模式变更 |
| `400-api-architecture.md` | 不涉及（API 层未违规） |
| `600-domain-models.md` | 新增 interfaces.py 及抽象接口定义 |
| `800-cross-layer-call-chains.md` | 调用链从直接依赖改为依赖注入 |
| `910-skill-run-log.md` | 新增 architecture repair step 记录 |

---

## 9. 当前状态

- **Step 7 立项：** ❌ 冻结，等待 Step 6A 完成
- **Step 6A：** 待执行
- **目标完成时间：** 待定（取决于修复过程中是否发现新的技术债务）

---

## 10. 下一步行动

在收到"可以开始"确认后，执行 `Step 6A.1 — Step 6A.10`。

完成后执行四件套对账：
1. `docs/progress.md` — 更新 Active Step 为 Step 6A，标记 Step 7 为 pending
2. `docs/knowledge/PaperNormAI-knowledge/900-learning-log.md` — 追加架构修复学习记录
3. `docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md` — 追加修复执行记录
4. `docs/memory/YYYY-MM-DD.md` — 追加当日工作存档

---

## Appendix: 违规文件内容摘要

### semantic_validation_service.py
```python
# Line 6-7 — 当前违规 import
from app.infrastructure.docling.document_model import DocumentModel
from app.infrastructure.ai.openai_provider import OpenAIProvider

# Line 82-83 — 构造函数直接实例化
def __init__(self, openai_provider: Optional[OpenAIProvider] = None):
    self._provider = openai_provider or OpenAIProvider()
```

### rule_extraction_service.py
```python
# Line 4-5 — 当前违规 import
from app.infrastructure.docling.document_model import DocumentModel
from app.infrastructure.ai.openai_provider import OpenAIProvider

# Line 62-63 — 构造函数直接实例化
def __init__(self, openai_provider: Optional[OpenAIProvider] = None):
    self._provider = openai_provider or OpenAIProvider()
```

### correction_service.py
```python
# Line 11 — 当前违规 import
from app.infrastructure.docx.document_merger import DocumentMerger

# Line 21 — 构造函数直接实例化
def __init__(self, merger: Optional[DocumentMerger] = None, output_dir: Optional[Path] = None):
    self._merger = merger or DocumentMerger(output_dir=output_dir)
```

### rule_engine.py
```python
# Line 16 — 当前违规 import
from app.infrastructure.docx.document_parser import ParsedDocument, DocumentElement
```

### correction_executor.py
```python
# Line 14-15 — 当前违规 import
from app.infrastructure.docx.document_parser import ParsedDocument, DocumentElement
from app.infrastructure.docx.document_writer import DocumentWriter

# Line 21 — 构造函数直接实例化
def __init__(self, document_writer: Optional[DocumentWriter] = None):
    self._writer = document_writer or DocumentWriter()
```

### ai_enhancement_service.py
```python
# Line 4 — 当前违规 import
from app.infrastructure.ai.openai_provider import OpenAIProvider

# Line 12-13 — 构造函数直接实例化
def __init__(self, openai_provider: Optional[OpenAIProvider] = None):
    self._provider = openai_provider or OpenAIProvider()
```

### template_service.py
```python
# Line 5-6 — ✅ 无违规
from app.domain.entities.template import Template
from app.domain.repositories import ITemplateRepository
```