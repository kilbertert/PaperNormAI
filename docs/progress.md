# Progress — PaperNormAI
*当前项目状态快照。开工前必读。ARCHITECT.md 的 Session Start 依赖此文件。*

---

## 当前阶段

**Active Step:** Step 6 已完成（KG-4 规则持久化）  
**Status:** Phase 1 ✅ | Phase 2 ✅ | KG-4 ✅  
**Started:** 2026-05-03  
**Last Updated:** 2026-05-06

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
  -> 返回 ValidationReport 统计

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

1. 启动 Step 7（待定义）：优先从前端接入或 ValidationReport 深度持久化二选一。  
2. 执行 200/300/400/600/800 知识文档刷新为代码事实态。  
3. 对接 Step COMPLETE 四件套对账机制到 BUILD-LOG 流程。
