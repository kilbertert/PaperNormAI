# Build Log
*Owned by Architect. Updated by Builder after each step.*

---

## Current Status

**Active step:** Phase 1 完成 — MVP 核心链路已就绪
**Last cleared:** Step 3 — 2026-05-05
**Pending deploy:** NO (local development only)

---

## Step History

### Step 3 — AI-Word-Skill 文档修正合并 — COMPLETE
*Date: 2026-05-05*

Files changed:
- `backend/app/infrastructure/docx/document_merger.py` — DocumentMerger 实现
- `backend/app/domain/services/correction_service.py` — CorrectionService 实现
- `backend/tests/unit/test_document_merger.py` — 单元测试
- `backend/tests/unit/test_correction_service.py` — 单元测试

Decisions made:
- AI-Word-Skill 优先，不可用的 fallback 到 python-docx
- 部分成功时保留已应用的修正
- 临时文件 + 原子性操作

Reviewer findings: 4 Must Fix 全部修复，Richard 确认通过
Deploy: 不适用（开发阶段）

---

### Step 2 — AI 语义规则提取与校验 — COMPLETE
*Date: 2026-05-05*

Files changed:
- `backend/app/domain/entities/validation_report.py` — ValidationReport, ViolationDetail 等实体
- `backend/app/domain/services/rule_extraction_service.py` — AI 规则提取服务
- `backend/app/domain/services/semantic_validation_service.py` — AI 语义校验服务
- `backend/tests/unit/test_validation_report.py` — 单元测试
- `backend/tests/unit/test_rule_extraction_service.py` — 单元测试
- `backend/tests/unit/test_semantic_validation_service.py` — 单元测试

Decisions made:
- 规则提取使用 Prompt 1，语义校验使用 Prompt 2
- ValidationReport 包含统计字段和 _recalc_stats()
- 段落索引使用 1-based，与 AI 输出对齐
- 长文档限制前 200 个段落

Reviewer findings: 6 Must Fix 全部修复，Richard 确认通过
Deploy: 不适用（开发阶段）

---

### Step 1 — Docling 集成 — COMPLETE
*Date: 2026-05-03*

Files changed:
- `backend/app/infrastructure/docling/__init__.py` — 模块导出
- `backend/app/infrastructure/docling/document_model.py` — DocumentModel 数据类
- `backend/app/infrastructure/docling/parser.py` — DoclingDocumentParser 实现
- `backend/tests/unit/test_docling_parser.py` — 单元测试
- `backend/requirements.txt` — 添加 docling>=1.0.0

Decisions made:
- DoclingDocumentParser 与现有 DocumentParser (python-docx) 共存，职责分离
- DocumentModel 作为 AI 处理的中间表示

Reviewer findings: 3 Must Fix 全部修复，Richard 确认通过
Deploy: 不适用（开发阶段）

---

## Known Gaps
*Logged here instead of fixed. Addressed in a future step.*

- **KG-1** — Docling DOCX 解析保真度未在实际文档上验证 — logged 2026-05-03
- **KG-2** — DocumentUseCases 尚未接入 DoclingDocumentParser — logged 2026-05-03
- **KG-3** — 长文档处理（>200段落）— logged 2026-05-05
- **KG-4** — 规则和 ValidationReport 尚未持久化到数据库 — logged 2026-05-05
- **KG-5** — AI-Word-Skill API 实际可用性待验证（repo 不可访问）— logged 2026-05-05
- **KG-6** — Phase 2（公式/表格/插图）尚未实现 — logged 2026-05-05

---

## Architecture Decisions
*Locked decisions that cannot be changed without breaking the system.*

- **ADR-001** — 使用 docling 作为文档解析引擎 — 2026-05-03
- **ADR-002** — 使用 AI 语义理解提取规则（而非结构化规则）— 2026-05-03
- **ADR-003** — 使用 AI-Word-Skill 实现文档修正合并 — 2026-05-03
- **ADR-004** — MVP 分两阶段实施 — 2026-05-03
- **ADR-005** — 规则存储采用用户级别持久化 — 2026-05-03