# Build Log
*Owned by Architect. Updated by Builder after each step.*

---

## Current Status

**Active step:** Step 6 KG-4 完成 — 规则持久化 — 2026-05-06
**Last cleared:** Step 6 — 2026-05-06
**Pending deploy:** NO (local development only)

---

## Step History

### Step 6 — KG-4 规则持久化 — COMPLETE
*Date: 2026-05-06*

Files changed:
- `backend/app/infrastructure/persistence/models.py` — 添加 SpecSessionModel
- `backend/app/infrastructure/persistence/spec_session_repository.py` — 新建 repository
- `backend/app/api/endpoints/spec_validation.py` — 替换 _spec_sessions dict 为 DB

Decisions made:
- SpecSessionModel 使用 String(36) 存储 user_id（SQLite 兼容，不用 PGUUID FK）
- rules_json + summary_json 存储为 Text（JSON 序列化）
- ValidationReport violations 不持久化（仅返回计数，MVP 够用）

验证结果:
- save/find/delete 全部通过
- 服务重启后 session 不丢失

Deploy: 不适用（开发阶段）

---

### Step 5 — Phase 2 表格/插图/公式解析 — COMPLETE
*Date: 2026-05-05*

Files changed:
- `backend/app/infrastructure/docling/document_model.py` — 添加 TableInfo, FigureInfo, FormulaInfo
- `backend/app/infrastructure/docling/parser.py` — 扩展 _convert_to_document_model()

Decisions made:
- TableInfo: rows, cols, caption, style
- FigureInfo: width, height, caption
- FormulaInfo: content, numbered, number
- 所有新字段使用 field(default_factory=list) 保证向后兼容

验证结果 (temp.docx):
- Tables: 6
- Figures: 13
- Formulas: 20

Reviewer findings: Richard Review 通过（no Must Fix issues）
Deploy: 不适用（开发阶段）

---

### Step 4 — KG-1/2/3 端到端验证与 DeepSeek 集成 — COMPLETE
*Date: 2026-05-05*

Files changed:
- `backend/app/api/endpoints/spec_validation.py` — 接入 DoclingDocumentParser + AI 服务
- `backend/app/infrastructure/ai/openai_provider.py` — 支持 DeepSeek/ollama 多 provider
- `backend/app/core/config.py` — 添加 DeepSeek/ollama 配置
- `backend/app/domain/entities/validation_report.py` — 修复 dataclass 字段顺序
- `backend/app/domain/services/semantic_validation_service.py` — 修复 AI 响应解析逻辑

Decisions made:
- DeepSeek 作为主要 AI provider（`AI_PROVIDER=deepseek`）
- API Key: `sk-a2fb983c14e54ca68409923b6373fcb1`
- Base URL: `https://api.deepseek.com/v1`
- Model: `deepseek-chat`

验证结果:
- temp.docx (390段落, 59章节): 提取 17 条规则，检测到 30 处违规
- 所有 AI 服务（RuleExtraction + SemanticValidation）正常工作

Reviewer findings: KG-1/2/3 全部通过
Deploy: 不适用（开发阶段）

---

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

- **KG-1** — ~~Docling DOCX 解析保真度未在实际文档上验证~~ — ✅ 已验证（390段落正常），2026-05-05
- **KG-2** — ~~DocumentUseCases 尚未接入 DoclingDocumentParser~~ — ✅ 已完成，2026-05-05
- **KG-3** — ~~长文档处理（>200段落）~~ — ✅ 已通过（390段落正常），2026-05-05
- **KG-4** — ~~规则和 ValidationReport 尚未持久化到数据库~~ — ✅ 已完成（Step 6），2026-05-06
- **KG-5** — ~~AI-Word-Skill 虚假包检测~~ — ✅ 已修正，2026-05-05
- **KG-6** — ~~Phase 2（公式/表格/插图）~~ — ✅ 已完成（Step 5），2026-05-05
- **KG-7** — ~~Docling v2 API 错误（elements 不存在）~~ — ✅ Arch 直接重写 parser.py，2026-05-05

---

## Architecture Decisions
*Locked decisions that cannot be changed without breaking the system.*

- **ADR-001** — 使用 docling 作为文档解析引擎 — 2026-05-03
- **ADR-002** — 使用 AI 语义理解提取规则（而非结构化规则）— 2026-05-03
- **ADR-003** — 使用 AI-Word-Skill 实现文档修正合并 — 2026-05-03
- **ADR-004** — MVP 分两阶段实施 — 2026-05-03
- **ADR-005** — 规则存储采用用户级别持久化 — 2026-05-03
- **ADR-006** — AI Provider 支持多后端（OpenAI/Ollama/DeepSeek）— 2026-05-05