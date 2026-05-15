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

## 2026-05-14 - feature-readiness (Step 7)

**场景**：评估 ValidationReport 深度持久化就绪条件
**输入**：feature=Step 7 ValidationReport 深度持久化
**结论**：Green — 知识文档足够、接口变化极小（仅增加 report_id 字段）、回归面清晰有限、持久化职责明确
**关联**：`backend/app/infrastructure/persistence/models.py`、`backend/app/api/endpoints/spec_validation.py`

---

## 2026-05-14 - architecture-check (Step 7)

**场景**：评估 ValidationReport 深度持久化架构合规性
**输入**：feature=Step 7，架构门禁检查
**结论**：Yellow — 不会新增 domain→infrastructure 违规，但会继续沿用 API→infrastructure repository 的务实捷径；记录为 MVP 例外
**关联**：`backend/app/api/endpoints/spec_validation.py`（API 层直接调用 repository）

---

## 2026-05-14 - governance-hardening (Step 8A)

**场景**：Step 8A — 新建 architecture-check skill + 修改 feature-readiness 架构初筛
**输入**：feature=Step 8A Governance Hardening
**结论**：完成 — 新建 `.ai/skills/architecture-check.md`（分层/边界/持久化合规检查 + 例外机制）；修改 `.ai/skills/feature-readiness.md`（新增 Step 3 架构影响初筛 5 项 + 双门禁串联）
**关联**：`.ai/skills/architecture-check.md`、`.ai/skills/feature-readiness.md`、`handoff/BUILD-LOG.md`、`docs/progress.md`

---

## 2026-05-14 - architecture-repair (Step 6A)

**场景**：清除 domain → infrastructure 直接依赖（系统架构违规修复）
**输入**：feature=Architecture Repair — 9处违规 / 7个service文件
**结论**：完成 — 6个service文件全部重构为依赖注入模式；新增 domain/services/interfaces.py；所有domain service不再直接import infrastructure
**关联**：`backend/app/domain/services/semantic_validation_service.py`、`backend/app/domain/services/rule_extraction_service.py`、`backend/app/domain/services/rule_engine.py`、`backend/app/domain/services/correction_service.py`、`backend/app/domain/services/correction_executor.py`、`backend/app/domain/services/ai_enhancement_service.py`、`backend/app/domain/services/interfaces.py`、`backend/app/api/endpoints/spec_validation.py`

---

## 2026-05-14 - feature-development (Step 8B)

**场景**：Step 8B 前端接入 — Next.js App Router 实现
**输入**：feature=Step 8B 前端接入
**结论**：完成 — 替换 Vite 为 Next.js，实现极简登录 + spec/thesis 上传 + 报告展示
**关联**：`clients/apps/web/`（Next.js 项目）、`clients/apps/web/src/app/login/page.tsx`、`clients/apps/web/src/app/spec/`、`clients/apps/web/src/lib/`

**场景**：Step 8B 前端接入阻塞解除 — 新增 ValidationReport 查询 API
**输入**：feature=GET /spec/reports/{report_id}
**结论**：完成 — 新增 GET /api/v1/spec/reports/{report_id}，返回完整 ValidationReport + ViolationDetail[]
**关联**：`backend/app/api/endpoints/spec_validation.py`

---

## 2026-05-06 - knowledge-sync

**场景**：建立 Step COMPLETE 自动对账清单并执行专题知识刷新
**输入**：step=Step 6 后治理收口；目标=强制检查 progress + 900 + 910 + memory 四件套并修复知识漂移
**结论**：完成 — BUILD-LOG 与 knowledge-sync skill 已加入四件套强制检查；`progress.md` 与 `000-doc-map.md` 冲突已修复；`200/300/400/600/800` 已刷新为代码事实态
**关联**：`handoff/BUILD-LOG.md`，`.ai/skills/knowledge-sync.md`，`docs/progress.md`，`docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`，`docs/knowledge/PaperNormAI-knowledge/{200,300,400,600,800}-*.md`

---

## 2026-05-14 - feature-development (Step 9)

**场景**：Step 9 — Correction Download 前端集成，在报告页增加"生成修正/下载修正文档"入口
**输入**：feature=Step 9 前端修正文档下载
**结论**：完成 — 新增 correction API 调用函数、报告页修正按钮与轮询下载逻辑；SpecValidationResponse 追加 document_name
**关联**：`clients/apps/web/src/lib/api.ts`、`clients/apps/web/src/lib/types.ts`、`clients/apps/web/src/app/spec/[sessionId]/page.tsx`、`clients/apps/web/src/app/spec/[sessionId]/report/[reportId]/page.tsx`、`backend/app/api/endpoints/spec_validation.py`

---

## 2026-05-15 - bugfix (DocumentRepository UUID type)

**场景**：Step 9 correction endpoint 持续 404 — DocumentRepository 类型 mismatch bug
**输入**：bug=corrections.py 返回 404 Document not found，但文档实际存在于 DB
**结论**：完成 — 发现 DocumentRepository.find_by_id 用 raw SQL 返回字符串而非 UUID 对象；修复为 `user_id=UUID(row.user_id)`；修正后 correction endpoint 返回 202
**关联**：`backend/app/infrastructure/persistence/document_repository.py`（find_by_id 修复）、`backend/app/api/endpoints/corrections.py`

---

## 6. 更新记录

**创建时间**：2026-05-01
**最近更新**：2026-05-15 — 新增 Step 9 bugfix (DocumentRepository UUID type)
