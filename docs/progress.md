# Progress — PaperNormAI
*当前项目状态快照。开工前必读。ARCHITECT.md 的 Session Start 依赖此文件。*

---

## 当前阶段

**Active Step:** KG-6 Phase 2 完成 — 2026-05-05
**Status:** Phase 1 ✅ | Phase 2 表格/插图/公式解析 ✅
**Started:** 2026-05-03
**Last Updated:** 2026-05-05

---

## Phase 1 & 2 完成总结

### Phase 1 核心链路

| 步骤 | 状态 | 日期 |
|------|------|------|
| Step 1 — Docling 集成 | ✅ 完成 | 2026-05-03 |
| Step 2 — AI 语义规则提取与校验 | ✅ 完成 | 2026-05-05 |
| Step 3 — AI-Word-Skill 文档修正合并 | ✅ 完成 | 2026-05-05 |
| Step 4 — KG-1/2/3 验证 + DeepSeek 集成 | ✅ 完成 | 2026-05-05 |

### Phase 2 表格/插图/公式解析

| 步骤 | 状态 | 日期 |
|------|------|------|
| Step 5 — Table/Figure/Formula 解析 | ✅ 完成 | 2026-05-05 |

### 核心链路

```text
用户上传 spec_doc + thesis_doc
  → docling 解析 → DocumentModel
  → AI 提取规则（RuleExtractionService）
  → AI 语义校验（SemanticValidationService）→ ValidationReport
  → Git-diff 风格展示
  → 用户手动编辑/确认
  → AI-Word-Skill 合并（CorrectionService + DocumentMerger）
  → 输出 corrected.docx
```

---

## 重要发现（2026-05-05）

**AI-Word-Skill 不是 Python 包**，而是一套代码模式/最佳实践：
- 核心思想：复制原档 → 改 run 级别文字 → 保存
- Bob 之前代码中的 `_merge_with_basic_replacement` **已经在使用正确的 AI-Word-Skill 模式**

**Docling v2 API 错误（严重）：**
- Bob 的 `_convert_to_document_model` 假设 `docling_doc.elements` 存在
- 但 docling v2.x 实际 API 使用 `docling_doc.texts` 和 `docling_doc.groups`
- `hasattr(docling_doc, "elements")` 始终返回 False，导致静默失败
- Arch 直接重写了 `parser.py` 修复此问题
- 复盘存档：`docs/postmortem/2026-05-05-docling-fake-implementation.md`

**DeepSeek API 集成：**
- 配置 `AI_PROVIDER=deepseek`
- API Key: `sk-a2fb983c14e54ca68409923b6373fcb1`
- Base URL: `https://api.deepseek.com/v1`
- Model: `deepseek-chat`

---

## KG 状态（2026-05-05 更新）

| 编号 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| KG-1 | Docling DOCX 解析保真度验证 | 中 | ✅ 已验证（390段落正常） |
| KG-2 | DocumentUseCases 接入 DoclingDocumentParser | 高 | ✅ 已完成 |
| KG-3 | 长文档处理（>200段落）| 中 | ✅ 已通过（390段落正常） |
| KG-4 | 规则和 ValidationReport 持久化 | 高 | 待实施 |
| KG-5 | ~~AI-Word-Skill 包检测~~ | ~~高~~ | ✅ 已完成 |
| KG-6 | ~~Phase 2（公式/表格/插图）~~ | ~~低~~ | ✅ 已完成 |
| KG-7 | ~~Docling v2 API 解析修复~~ | ~~高~~ | ✅ 已修复 |

---

## 端到端验证结果

**测试文档:** `temp.docx`

```
Phase 1:
  Paragraphs: 390, Sections: 59
  Rules: 17, Violations: 30

Phase 2 (新增):
  Tables: 6
  Figures: 13
  Formulas: 20
```

**AI 服务状态:**
- DeepSeek API: ✅ 已连接
- RuleExtractionService: ✅ 正常工作
- SemanticValidationService: ✅ 正常工作

---

## 下一步

1. **KG-4**: 实现规则和 ValidationReport 持久化（数据库）

---

*最近更新: 2026-05-05 15:00 — KG-6 Phase 2 完成，表格/插图/公式解析已实现并通过 Review*