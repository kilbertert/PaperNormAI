# Build Log
*Owned by Architect. Updated by Builder after each step.*

---

## Current Status

**Active step:** Step 9 — Correction Download Frontend Integration
**Last cleared:** Step 8B — 2026-05-14
**Pending deploy:** NO (local development only)

### Architecture Gate（Step 7 收口）

| 门禁 | 结果 | 说明 |
|------|------|------|
| feature-readiness | ✅ Green | 知识文档足够、接口变化极小、回归面清晰 |
| architecture-check | 🟡 Yellow | API 层直接调用 repository — **MVP 例外**，已记录 |

**MVP 例外条件**：允许 `spec_validation.py` 继续承担编排，直接调用持久化仓储；后续需下沉到 `application/` 层。

### Step COMPLETE 自动对账（强制）

每次将 Step 标记为 `COMPLETE` 后，必须在同一会话完成四件套对账：

1. `docs/progress.md`
2. `docs/knowledge/PaperNormAI-knowledge/900-learning-log.md`
3. `docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md`
4. `docs/memory/YYYY-MM-DD.md`

建议在每个 Step 末尾追加以下检查块：

```markdown
Checklist (Step COMPLETE):
- [ ] progress.md 已更新
- [ ] 900-learning-log.md 已追加
- [ ] 910-skill-run-log.md 已追加
- [ ] memory/YYYY-MM-DD.md 已追加
```

---

## Step History

### Step 6A — Architecture Repair: Remove domain -> infrastructure dependencies — COMPLETE
*Date: 2026-05-14*

Files changed:
- `backend/app/domain/services/interfaces.py` — 新建：IAIProvider, IDocumentParser, IDocumentMerger, IDocumentWriter, IParsedDocument, ElementLike
- `backend/app/domain/services/ai_enhancement_service.py` — OpenAIProvider → IAIProvider
- `backend/app/domain/services/semantic_validation_service.py` — DocumentModel + OpenAIProvider → IDocumentParser + IAIProvider
- `backend/app/domain/services/rule_extraction_service.py` — DocumentModel + OpenAIProvider → IDocumentParser + IAIProvider
- `backend/app/domain/services/rule_engine.py` — ParsedDocument + DocumentElement → IParsedDocument + ElementLike
- `backend/app/domain/services/correction_executor.py` — ParsedDocument + DocumentWriter → IParsedDocument + IDocumentWriter
- `backend/app/domain/services/correction_service.py` — DocumentMerger → IDocumentMerger
- `backend/app/api/endpoints/spec_validation.py` — application 层注入具体实现

Decisions made:
- domain 层不再直接 import infrastructure，所有依赖通过 constructor 注入
- 新增 `domain/services/interfaces.py` 作为抽象接口定义文件
- `template_service.py` ✅ 无违规，保持不变

Validation results:
- ✅ domain/services/ 下不再有 app.infrastructure 直接 import
- ✅ 所有 domain service 公开方法签名不变
- ✅ Python 语法检查通过
- ✅ 模块级 import 验证通过
- ✅ spec_validation.py wiring 验证通过
- ✅ RuleEngine.validate 接受真实 ParsedDocument 验证通过

Deploy: 不适用（架构修复）

---

### Step 7 — ValidationReport 深度持久化 — COMPLETE
*Date: 2026-05-14*

Files changed:
- `backend/app/infrastructure/persistence/models.py` — 新增 ValidationReportModel + ViolationDetailModel（full UUID，字段 String(36)）
- `backend/app/api/endpoints/spec_validation.py` — 响应追加 report_id + 同步落库逻辑

Decisions made:
- 使用领域对象已有 UUID（report.id / v.id），不生成新 ID
- API 编排层负责持久化，Domain Service 仅产出 ValidationReport
- Architecture gate: feature-readiness ✅ Green, architecture-check 🟡 Yellow（MVP 例外：API 层直接调用 repository）

Validation results:
- ✅ ValidationReportModel + ViolationDetailModel 导入正常
- ✅ SpecValidationResponse 包含 report_id 字段
- ✅ 实际数据库写入/读取验证通过（主记录统计与明细数量一致）
- ✅ 无新增 domain → infrastructure 违规

Deploy: 不适用（开发阶段）

---

### Step 8A — Governance Hardening — COMPLETE
*Date: 2026-05-14*

Files changed:
- `.ai/skills/architecture-check.md` — 新建 architecture-check skill
- `.ai/skills/feature-readiness.md` — 新增 Step 3 架构影响初筛（5项检查）

Decisions made:
- P0: architecture-check skill 新建，强制门禁防止架构腐化复发
- P0: feature-readiness 增加架构影响初筛，触发 architecture-check 双门禁
- P1: 前端接入（暂缓）
- P2: API → application 下沉重构（单独立项，不夹带）

Validation results:
- ✅ architecture-check skill 门禁逻辑完整
- ✅ feature-readiness 串联 architecture-check 双门禁
- ✅ MVP 例外机制已记录

Deploy: 不适用（开发阶段）

---

### Step 8B-Pre — ValidationReport 查询 API — COMPLETE
*Date: 2026-05-14*

Files changed:
- `backend/app/api/endpoints/spec_validation.py` — 新增 GET /reports/{report_id}

Decisions made:
- 前端展示 ValidationReport 统计 + 违规明细，需要先有查询 API
- 新增 ViolationDetailResponse + ValidationReportResponse Pydantic 模型
- 使用 joinedload 预加载 violations 避免 N+1 查询
- 权限验证：通过 spec session 关联验证用户所有权

Validation results:
- ✅ Python import 检查通过
- ✅ 返回字段与前端需求对齐（report_id, session_id, document_name, template_name, created_at, total/error/warning/info_count, violations[]）

Deploy: 不适用（开发阶段）

---

### Step 8B — 前端接入（Next.js App Router）— COMPLETE
*Date: 2026-05-14*

Files changed:
- `clients/apps/web/` — 替换 Vite 为 Next.js App Router（无 react-query）
- `clients/apps/web/.env.local` — 新增 NEXT_PUBLIC_API_BASE_URL
- `clients/apps/web/src/lib/api.ts` — API 调用函数
- `clients/apps/web/src/lib/auth.ts` — 客户端守卫 getAccessToken + useRequireAuth
- `clients/apps/web/src/lib/types.ts` — 类型定义（从 api-client/types 复制）
- `clients/apps/web/src/app/login/page.tsx` — 极简登录页
- `clients/apps/web/src/app/spec/page.tsx` — Step 1: 上传 spec
- `clients/apps/web/src/app/spec/[sessionId]/page.tsx` — Step 2: 上传 thesis
- `clients/apps/web/src/app/spec/[sessionId]/report/[reportId]/page.tsx` — Step 3: 展示报告

Decisions made:
- 纯 Client Components（所有页面 'use client'）
- Token key: access_token（与 client.ts 一致）
- NEXT_PUBLIC_API_BASE_URL 环境变量直接请求后端
- 去掉 react-query（useState + useEffect）
- 先清目录再创建 Next.js

Validation results:
- ✅ npm run build 成功
- ✅ 6 个页面全部正确生成（/, /login, /spec, /spec/[sessionId], /spec/[sessionId]/report/[reportId]）
- ✅ TypeScript 检查通过

Deploy: 不适用（开发阶段）

---

### Step 9 — Correction Download Frontend Integration — COMPLETE
*Date: 2026-05-14*

Files changed:
- `backend/app/api/endpoints/spec_validation.py` — `SpecValidationResponse` 追加 `document_name` 字段；`POST /validate-with-spec` 在验证后持久化 thesis 为 `DocumentModel`（`file_path` 存储到 `uploads/`）
- `backend/app/api/endpoints/corrections.py` — `CorrectionResponse` 追加 `error_message` 字段
- `clients/apps/web/src/lib/types.ts` — 新增 `CorrectionJobResponse`、`CorrectionStatus` 接口；`CorrectionStatus` 含 `id/document_id/status/output_path/error_message/created_at/completed_at`
- `clients/apps/web/src/lib/api.ts` — 新增 `createCorrectionJob`、`getCorrectionJob`、`getCorrectionDownloadUrl`
- `clients/apps/web/src/app/spec/[sessionId]/page.tsx` — 简化跳转（去掉 URL query doc 参数）
- `clients/apps/web/src/app/spec/[sessionId]/report/[reportId]/page.tsx` — 新增"Generate Corrected Document"按钮 + 2秒轮询 + Blob 下载逻辑

Decisions made:
- thesis 验证后立即以 `DocumentModel` 持久化到 `uploads/`（document_id = report_id），供 correction pipeline 使用
- 前端轮询 `GET /corrections/{job_id}` 最多 60 次（120 秒超时）
- 下载使用 `fetch` + `Authorization: Bearer` + `URL.createObjectURL`（避免 URL token 泄露）
- `CorrectionStatus.error_message` 来自后端 `job.error_message`（修正失败时显示）

Validation results:
- ✅ `npm run build` 通过（6 routes 全部正确生成）
- ✅ Python import 检查通过
- ✅ `document_name` 已追加到 `SpecValidationResponse`
- ✅ `error_message` 已追加到 `CorrectionResponse`
- ✅ thesis 持久化到 DocumentModel（correction pipeline 可用 document_id）

Deploy: 不适用（开发阶段）

---

### Step 8B — 前端接入（Next.js App Router）— COMPLETE
*Date: 2026-05-14*

---

### Step 9 Bugfix — DocumentRepository UUID Type Fix — COMPLETE
*Date: 2026-05-15*

Files changed:
- `backend/.env` — 新建（DEEPSEEK_API_KEY 等配置）
- `backend/app/infrastructure/persistence/document_repository.py` — find_by_id 将 `user_id=row.user_id` 改为 `user_id=UUID(row.user_id)`

Decisions made:
- Raw SQL 返回字符串类型 UUID，ORM 模型构建时需显式转换为 UUID 对象
- document.user_id (UUID) 与 current_user.id (UUID) 比较失败导致 403 Access Denied
- 根本原因：find_by_id 用 raw SQL 查询但未将 user_id 转换为 UUID

验证结果:
- 修复后 POST /corrections/ 返回 202（之前返回 404）
- GET /corrections/{job_id} 轮询返回 completed
- Correction job 输出文件正确生成

Deploy: 不适用（开发阶段）

---

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
