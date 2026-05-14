# PaperNormAI 功能能力地图

## 1. 文档目的

本文件建立 PaperNormAI 的功能能力地图，回答：

1. 当前产品能力按什么维度划分
2. 每项能力落在哪些模块上
3. 当前哪些能力已落地，哪些还未开始

## 2. 核心事实（2026-05-06 更新）

- Phase 1 核心链路已完成（2026-05-05）
- Phase 2 表格/插图/公式解析已完成（2026-05-05）
- 所有 Known Gaps（KG-1 至 KG-7）已清零

## 3. Phase 1 能力地图（已完成）

| 能力 | 模块 | 状态 |
|------|------|------|
| DOCX 文档解析 | `backend/app/infrastructure/docling/parser.py` | ✅ 已实现 |
| AI 语义规则提取 | `backend/app/domain/services/rule_extraction_service.py` | ✅ 已实现 |
| 规则持久化 | `backend/app/infrastructure/persistence/spec_session_repository.py` | ✅ 已实现 |
| AI 语义校验 | `backend/app/domain/services/semantic_validation_service.py` | ✅ 已实现 |
| ValidationReport | `backend/app/domain/entities/validation_report.py` | ✅ 已实现 |
| AI-Word-Skill 合并 | `backend/app/infrastructure/docx/document_merger.py` | ✅ 已实现 |
| 修正服务 | `backend/app/domain/services/correction_service.py` | ✅ 已实现 |
| Spec 校验 API | `backend/app/api/endpoints/spec_validation.py` | ✅ 已实现 |
| AI Provider | `backend/app/infrastructure/ai/openai_provider.py` | ✅ 支持 DeepSeek/Ollama/OpenAI |

**Phase 1 覆盖的格式问题：** 字体、字号、行距、段前段后、标题层级、页边距

## 4. Phase 2 能力地图（已完成）

| 能力 | 模块 | 状态 |
|------|------|------|
| 表格解析（TableInfo） | `backend/app/infrastructure/docling/document_model.py` | ✅ 已实现 |
| 插图解析（FigureInfo） | `backend/app/infrastructure/docling/document_model.py` | ✅ 已实现 |
| 公式解析（FormulaInfo） | `backend/app/infrastructure/docling/document_model.py` | ✅ 已实现 |

**验证结果（temp.docx）：** Tables=6，Figures=13，Formulas=20

## 5. 待实现能力

| 能力 | 状态 | 说明 |
|------|------|------|
| 前端 Web 界面 | ✅ 已实现（Step 8B） | Next.js App Router，/spec → /spec/[sessionId] → /spec/[sessionId]/report/[reportId] |
| corrected.docx 下载 API | 未实现 | 需要前端配合 |
| ValidationReport 完整持久化 | ✅ 已实现（Step 7） | ValidationReportModel + ViolationDetailModel |
| ValidationReport 查询 API | ✅ 已实现（Step 8B-Pre） | GET /spec/reports/{report_id} |
| template-library | 未实现 | Fallback 机制 |

## 6. 明确后置的能力

| 能力 | 后置原因 |
|------|----------|
| 桌面客户端 | 先验证 Web 主链路 |
| Word 插件 | 先验证 Web 主链路 |
| PDF 自动修正 | 文档结构复杂度高 |
| LaTeX 支持 | 超出当前场景收敛范围 |
| 多租户组织空间 | 当前重点不是协作平台 |

## 7. AI 工程协作能力地图

| 能力 | 状态 | 落点 |
|------|------|------|
| AI 行为治理 | ✅ 已落地 | `.github/copilot-instructions.md` |
| 知识学习 agent | ✅ 已落地 | `.ai/agents/PaperNormAI-knowledge-builder.agent.md` |
| 功能开发 agent | ✅ 已落地 | `.ai/agents/PaperNormAI-feature-development.agent.md` |
| issue-evaluator skill | ✅ 已落地（可执行形态） | `.ai/skills/issue-evaluator.md` |
| feature-readiness skill | ✅ 已落地（可执行形态） | `.ai/skills/feature-readiness.md` |
| feature-development skill | ✅ 已落地（可执行形态） | `.ai/skills/feature-development.md` |
| fix-development skill | ✅ 已落地（可执行形态） | `.ai/skills/fix-development.md` |
| Skill 运行日志 | ✅ 有真实记录 | `docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md` |

## 8. 更新记录

**最近复核时间**：2026-05-14

**重要变更（2026-05-14）：**
- Step 8B 前端 Web 界面已完成（Next.js App Router）
- Step 7 ValidationReport 深度持久化已完成
- Step 8B-Pre ValidationReport 查询 API 已完成

**当前可信度**：高
