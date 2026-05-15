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

---

## 当前可用链路（代码事实）

```text
POST /api/v1/spec/parse-spec
  -> DoclingDocumentParser
  -> RuleExtractionService
  -> SpecSessionRepository.save

POST /api/v1/spec/validate-with-spec
  -> DoclingDocumentParser
  -> SemanticValidationService
  -> ValidationReportModel + ViolationDetailModel 同步落库
  -> 返回统计 + report_id

GET /api/v1/spec/reports/{report_id}        # Step 8B-Pre 新增
  -> ValidationReportModel + ViolationDetailModel
  -> 返回完整报告 + 所有违规明细

POST /api/v1/corrections/                    # Step 9 前端集成
  -> 创建 CorrectionJobModel
  -> BackgroundTasks 执行修正
  -> 返回 job_id + status

GET /api/v1/corrections/{job_id}             # Step 9 前端集成
  -> 返回修正任务状态 + plans

GET /api/v1/corrections/{job_id}/download   # Step 9 前端集成
  -> 返回 corrected_*.docx 文件

POST /api/v1/documents/upload
POST /api/v1/validations
POST /api/v1/corrections
  -> DocumentRepository / TemplateRepository / ValidationJobModel / CorrectionJobModel
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

1. **Step 9 — Correction Download 前端集成**：在报告页增加"生成修正/下载修正文档"入口

2. **技术债务跟踪**：
   - API → application 下沉重构 — 中优先级（单独立项）
   - Alembic 数据库迁移路径建立 — 低优先级
   - OMA 可观测性/重试机制借鉴 — 低优先级
