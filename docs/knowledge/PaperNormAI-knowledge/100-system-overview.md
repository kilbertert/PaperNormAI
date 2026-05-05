# PaperNormAI 系统总览

## 1. 文档目的

本文件建立 PaperNormAI 的系统级公共认知，回答：

1. PaperNormAI 当前要做的产品是什么
2. 当前 MVP 的真实边界在哪里
3. 系统的核心子系统是什么
4. 当前已实现了哪些能力

## 2. 核心事实（2026-05-06 更新）

**产品定位：**
- 面向学生的 AI 论文格式校准工具
- 用户上传规范手册（spec_doc）和论文（thesis_doc），AI 从规范手册提取语义规则并对论文进行校验
- 使用 AI-Word-Skill 技术实现"只改文字，保留排版"的修正合并

**技术选型（已确认并实现）：**

| 组件 | 选型 | 状态 |
|------|------|------|
| 文档解析 | docling v2.x | ✅ 已实现 |
| 规则提取 | AI 语义理解（DeepSeek） | ✅ 已实现 |
| 文档校验 | AI 语义校验 | ✅ 已实现 |
| 文档合并 | AI-Word-Skill 模式 | ✅ 已实现 |
| AI Provider | DeepSeek（兼容 OpenAI SDK） | ✅ 已配置 |
| 规则持久化 | SQLite（SpecSessionModel） | ✅ 已实现 |

**Phase 1 核心链路（已完成）：**
```text
用户上传 spec_doc + thesis_doc
  → docling 解析 → DocumentModel（段落/章节）
  → RuleExtractionService → 规则列表（List[Dict]）
  → SemanticValidationService → ValidationReport（violations）
  → CorrectionService + DocumentMerger → corrected.docx
```

**Phase 2 扩展（已完成）：**
- DocumentModel 扩展支持 TableInfo、FigureInfo、FormulaInfo
- temp.docx 验证：Tables=6，Figures=13，Formulas=20

## 3. 已实现模块清单

| 模块 | 路径 | 说明 |
|------|------|------|
| DoclingDocumentParser | `backend/app/infrastructure/docling/parser.py` | 解析 DOCX → DocumentModel |
| DocumentModel | `backend/app/infrastructure/docling/document_model.py` | 中间表示（段落/章节/表格/插图/公式） |
| RuleExtractionService | `backend/app/domain/services/rule_extraction_service.py` | AI 从 spec_doc 提取规则 |
| SemanticValidationService | `backend/app/domain/services/semantic_validation_service.py` | AI 校验 thesis_doc |
| ValidationReport | `backend/app/domain/entities/validation_report.py` | 违规报告实体 |
| DocumentMerger | `backend/app/infrastructure/docx/document_merger.py` | AI-Word-Skill 模式合并 |
| CorrectionService | `backend/app/domain/services/correction_service.py` | 修正服务 |
| OpenAIProvider | `backend/app/infrastructure/ai/openai_provider.py` | 支持 DeepSeek/Ollama/OpenAI |
| SpecSessionRepository | `backend/app/infrastructure/persistence/spec_session_repository.py` | 规则持久化 |
| spec_validation API | `backend/app/api/endpoints/spec_validation.py` | /parse-spec, /validate-with-spec |

## 4. 核心业务流程（已实现）

```text
POST /spec/parse-spec
  → DoclingDocumentParser.parse(spec_doc) → DocumentModel
  → RuleExtractionService.extract_rules(spec_doc) → rules_dicts
  → SpecSessionRepository.save(session_id, rules_dicts)
  → 返回 session_id + rules_count

POST /spec/validate-with-spec?session_id=xxx
  → SpecSessionRepository.find(session_id) → rules_dicts
  → DoclingDocumentParser.parse(thesis_doc) → DocumentModel
  → SemanticValidationService.validate(thesis_doc, rules_dicts) → ValidationReport
  → 返回 violations 统计
```

## 5. 当前未实现

| 功能 | 状态 |
|------|------|
| 前端 Web 界面 | 未实现 |
| template-library | 未实现 |
| ValidationReport 完整持久化 | 未实现（仅返回计数） |
| 用户手动编辑修正 UI | 未实现 |
| corrected.docx 下载 API | 未实现 |

## 6. 关键技术说明

**Docling v2.x API：**
- `docling_doc.texts` — TextItem 和 SectionHeaderItem 列表
- `docling_doc.groups` — DOCX 中为空（PDF 有嵌套结构）
- `docling_doc.tables` — 表格列表
- `docling_doc.pictures` — 图片列表
- `docling_doc.iterate_items()` — 遍历所有元素（含 FormulaItem）

**AI-Word-Skill 模式：**
- 不是 Python 包，是代码模式
- 核心：`shutil.copy2()` 复制原档 → 修改 `run.text` → `doc.save()`
- 保留格式，只改文字内容

**DeepSeek 配置：**
- `AI_PROVIDER=deepseek`
- `DEEPSEEK_BASE_URL=https://api.deepseek.com/v1`
- `DEEPSEEK_MODEL=deepseek-chat`

## 7. 与其他文档的关联

- `docs/progress.md` — 当前实施状态（实时更新）
- `handoff/BUILD-LOG.md` — 构建历史（实时更新）
- `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md` — 功能能力地图
- `docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md` — Skill 运行日志

## 8. 更新记录

**最近复核时间**：2026-05-06

**重要变更（2026-05-06）：**
- 全面更新为代码事实态（Phase 1 + Phase 2 已完成）
- 添加已实现模块清单
- 添加已实现业务流程
- 更新技术说明（Docling v2.x API、DeepSeek 配置）
- 删除"尚未落地"的描述，改为准确的当前状态

**当前可信度**：高
