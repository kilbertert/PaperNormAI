# PaperNormAI Skill 运行日志

## 1. 文档目的

记录 skill 调用的真实执行历史，形成可追溯记录。

## 2. 日志格式

```markdown
## YYYY-MM-DD HH:MM - {skill_name}
**场景**：{为什么调用}
**输入**：{关键参数}
**结论**：{关键输出}
**关联**：{涉及的文件/功能}
```

---

## 2026-05-05 - feature-readiness

**场景**：评估 KG-1 端到端验证是否就绪
**输入**：feature=KG-1 Docling 解析保真度验证
**结论**：Green — DoclingDocumentParser 已实现，temp.docx 可用于测试
**关联**：`backend/app/infrastructure/docling/parser.py`

---

## 2026-05-05 - feature-development

**场景**：KG-1 端到端验证 — 验证 DoclingDocumentParser 在真实文档上的解析效果
**输入**：feature=KG-1，文档=temp.docx（390段落）
**结论**：验证通过 — 390段落、59章节正确解析；sections 分层结构（1/2/3级）正确
**关联**：`backend/app/infrastructure/docling/parser.py`

---

## 2026-05-05 - fix-development

**场景**：修复 parser.py 中 sections 提取逻辑错误（KG-7 遗留问题）
**输入**：bug=sections count=0，groups 为空
**结论**：根因 — 代码遍历 `docling_doc.groups` 但 DOCX 的 groups 始终为空；section_header 实际在 `docling_doc.texts` 中。修复：改为遍历 texts 检查 `label.value == 'section_header'`
**关联**：`backend/app/infrastructure/docling/parser.py:84-116`

---

## 2026-05-05 - feature-readiness

**场景**：评估 KG-2 接入应用层是否就绪
**输入**：feature=KG-2 DoclingDocumentParser 接入 spec_validation.py
**结论**：Yellow — DoclingDocumentParser 已就绪，但 spec_validation.py 仍使用旧 DocumentParser；需替换
**关联**：`backend/app/api/endpoints/spec_validation.py`

---

## 2026-05-05 - feature-development

**场景**：KG-2 接入应用层 — 替换 spec_validation.py 旧链路为 AI 服务
**输入**：feature=KG-2
**结论**：完成 — `/parse-spec` 改用 DoclingDocumentParser + RuleExtractionService；`/validate-with-spec` 改用 SemanticValidationService
**关联**：`backend/app/api/endpoints/spec_validation.py`

---

## 2026-05-05 - fix-development

**场景**：修复 ViolationDetail/ValidationReport dataclass 字段顺序错误
**输入**：bug=TypeError: non-default argument follows default argument
**结论**：根因 — `id: UUID = field(default_factory=uuid4)` 在 `category: ViolationCategory` 前面，违反 Python dataclass 规则。修复：将有默认值的字段移到末尾
**关联**：`backend/app/domain/entities/validation_report.py`

---

## 2026-05-05 - fix-development

**场景**：修复 _parse_violations 解析逻辑错误（AI 返回 0 violations）
**输入**：bug=SemanticValidationService 返回 0 violations，AI 实际有输出
**结论**：根因 — `[违规]` 被 `if line.startswith('[') and line.endswith(']')` 误判为 section marker，导致 pending_violation_data 被清空。修复：调整判断顺序，先检查 `[违规]` 再检查 `[校验结果]`
**关联**：`backend/app/domain/services/semantic_validation_service.py:202-226`

---

## 2026-05-05 - feature-development

**场景**：DeepSeek API 集成 — 替换 Ollama 为 DeepSeek
**输入**：feature=DeepSeek 集成，api_key=sk-a2fb983c14e54ca68409923b6373fcb1
**结论**：完成 — OpenAIProvider 支持 deepseek/ollama/openai 三种 provider；.env 配置 AI_PROVIDER=deepseek
**关联**：`backend/app/infrastructure/ai/openai_provider.py`，`backend/app/core/config.py`

---

## 2026-05-05 - feature-readiness

**场景**：评估 KG-6 Phase 2 表格/插图/公式解析是否就绪
**输入**：feature=KG-6 Phase 2
**结论**：Green — docling 提供 `doc.tables`、`doc.pictures`、`iterate_items()` API；DocumentModel 可扩展
**关联**：`backend/app/infrastructure/docling/document_model.py`

---

## 2026-05-05 - feature-development

**场景**：KG-6 Phase 2 — 扩展 DocumentModel 支持表格/插图/公式
**输入**：feature=KG-6
**结论**：完成 — 新增 TableInfo/FigureInfo/FormulaInfo；temp.docx 验证：Tables=6，Figures=13，Formulas=20
**关联**：`backend/app/infrastructure/docling/document_model.py`，`backend/app/infrastructure/docling/parser.py`

---

## 2026-05-06 - feature-readiness

**场景**：评估 KG-4 规则持久化是否就绪
**输入**：feature=KG-4 SpecSession 持久化
**结论**：Yellow — SQLAlchemy 已配置，但 SpecSessionModel 不存在；_spec_sessions 为内存 dict
**关联**：`backend/app/infrastructure/persistence/models.py`

---

## 2026-05-06 - feature-development

**场景**：KG-4 规则持久化 — 替换内存 dict 为数据库
**输入**：feature=KG-4
**结论**：完成 — 新增 SpecSessionModel（String user_id 兼容 SQLite）；新建 SpecSessionRepository；spec_validation.py 全部端点改用 DB
**关联**：`backend/app/infrastructure/persistence/models.py`，`backend/app/infrastructure/persistence/spec_session_repository.py`，`backend/app/api/endpoints/spec_validation.py`

---

## 6. 更新记录

**创建时间**：2026-05-01
**最近更新**：2026-05-06 — 补充 2026-05-05/06 真实运行记录（KG-1/2/3/4/6 全周期）
