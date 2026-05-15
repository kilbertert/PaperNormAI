# Progress — PaperNormAI
*当前项目状态快照。开工前必读。ARCHITECT.md 的 Session Start 依赖此文件。*

---

## 当前阶段

**Active Step:** Step 9 — Correction Download Frontend Integration
**Status:** Phase 1 ✅ | Phase 2 ✅ | KG-4 ✅ | Step 6A ✅ | Step 7 ✅ | Step 8A ✅ | Step 8B-Pre ✅ | Step 8B ✅ | Step 9 🔄
**Started:** 2026-05-03（Step 1）/ 2026-05-14（Step 6A/7/8A）
**Last Updated:** 2026-05-14

---

## 已完成步骤

| 步骤 | 状态 | 日期 |
|------|------|------|
| Step 1 — Docling 集成 | ✅ 完成 | 2026-05-03 |
| Step 2 — AI 语义规则提取与校验 | ✅ 完成 | 2026-05-05 |
| Step 3 — AI-Word-Skill 文档修正合并 | ✅ 完成 | 2026-05-05 |
| Step 4 — KG-1/2/3 验证与 AI Provider 集成 | ✅ 完成 | 2026-05-05 |
| Step 5 — 表格/插图/公式解析（Phase 2） | ✅ 完成 | 2026-05-05 |
| Step 6 — KG-4 规则持久化（SpecSession） | ✅ 完成 | 2026-05-06 |
| Step 6A — Architecture Repair（domain→infrastructure 分层违规修复） | ✅ 完成 | 2026-05-14 |
| Step 7 — ValidationReport 深度持久化 | ✅ 完成 | 2026-05-14 |
| Step 8B-Pre — ValidationReport 查询 API | ✅ 完成 | 2026-05-14 |
| Step 8B — 前端接入（Next.js） | ✅ 完成 | 2026-05-14 |
| Step 9 — Correction Download 前端集成 | ✅ 完成 | 2026-05-15 |
| Step 10 — API → application 下沉重构 | ✅ 完成 | 2026-05-15 |
| Step 11 — Alembic 数据库迁移路径建立 | ✅ 完成 | 2026-05-15 |

## Alembic 迁移状态

| 项目 | 状态 |
|------|------|
| 迁移基线 | ✅ `001` — stamp 已建立 |
| autogenerate 可信度 | ⚠️ 需人工审阅（存在 schema drift） |
| `alembic upgrade head` | ✅ 通过 |

**使用纪律**：autogenerate 结果必须人工审阅后才能执行，见 `handoff/BUILD-LOG.md`。

---

## 当前可用链路（代码事实）

```text
API Layer (thin endpoints)
  -> Application Layer (orchestration + transaction)
    -> Domain Layer (business logic)
      -> Infrastructure Layer (persistence)

POST /api/v1/spec/parse-spec
  -> SpecApplicationService.parse_spec()
  -> RuleExtractionService
  -> SpecSessionRepository.save

POST /api/v1/spec/validate-with-spec
  -> SpecApplicationService.validate_with_spec()
  -> SemanticValidationService
  -> ValidationReportModel + ViolationDetailModel 同步落库
  -> DocumentModel 持久化（thesis）

GET /api/v1/spec/reports/{report_id}
  -> SpecApplicationService.get_validation_report()
  -> ValidationReportModel + ViolationDetailModel

DELETE /api/v1/spec/sessions/{session_id}
  -> SpecApplicationService.delete_spec_session()

POST /api/v1/corrections/
  -> CorrectionApplicationService.create_correction_job()
  -> CorrectionJobModel 持久化
  -> BackgroundTasks 执行修正

GET /api/v1/corrections/{job_id}
  -> CorrectionApplicationService.get_correction_job()
  -> 返回 job 状态 + plans

GET /api/v1/corrections/{job_id}/download
  -> CorrectionApplicationService.get_download_info()
  -> FileResponse 返回 corrected 文件
```

---

## KG 状态

| 编号 | 描述 | 状态 |
|------|------|------|
| KG-1 | Docling DOCX 解析保真度验证 | ✅ 已验证（390 段落） |
| KG-2 | 应用层接入 DoclingDocumentParser | ✅ 已完成 |
| KG-3 | 长文档处理（>200 段落） | ✅ 已通过 |
| KG-4 | 规则会话持久化（SpecSession） | ✅ 已完成 |
| KG-5 | AI-Word-Skill 虚假包识别纠正 | ✅ 已完成 |
| KG-6 | 表格/插图/公式解析 | ✅ 已完成 |
| KG-7 | Docling v2 API 解析修复 | ✅ 已完成 |

---

## 提交后自动对账（四件套）

每次 Step 标记 `COMPLETE` 后，必须在同一会话确认以下 4 个文件均已更新：

1. `docs/progress.md`（当前状态与下一步）
2. `docs/knowledge/PaperNormAI-knowledge/900-learning-log.md`（学习与认知刷新）
3. `docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md`（skill 调用记录）
4. `docs/memory/YYYY-MM-DD.md`（当日会话归档）

未通过四件套对账，不得进入下一 Step。

---

## 下一步

1. **Step 12（待定）**：P2 决策 — 前端继续扩展 或 治理重构

2. **技术债务跟踪**：
   - Alembic 数据库迁移路径建立 — ✅ 已完成（Step 11）
   - API → application 下沉重构 — ✅ 已完成（Step 10）
   - DeepSeek API Key 更新 — 高优先级
   - OMA 可观测性/重试机制借鉴 — 低优先级
