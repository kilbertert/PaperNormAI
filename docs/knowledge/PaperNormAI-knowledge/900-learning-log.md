# PaperNormAI 学习日志

## 1. 文档目的

本文件用于记录 `PaperNormAI-knowledge-builder` 及相关知识学习活动的摘要日志，形成对知识建立、刷新、冲突发现和文档回写的可回放轨迹。

## 2. 覆盖范围

本文件覆盖：

- 总览学习日志
- 专题学习日志
- 流程学习日志
- 增量学习日志
- 知识库骨架建立记录

## 3. 核心事实

截至当前版本，本文件是 PaperNormAI 知识学习体系的第一份集中式学习日志。

它的职责不是记录所有技术细节，而是沉淀：

- 为什么发起这次学习
- 读了哪些范围
- 确认了哪些事实
- 发现了哪些知识缺口或冲突
- 更新了哪些知识文档
- 下一步建议是什么

## 4. 日志记录模板

后续每次知识学习建议按以下格式追加：

```markdown
## YYYY-MM-DD HH:MM - {学习目标}

**学习类型**：总览学习 / 专题学习 / 流程学习 / 增量学习

**触发原因**：{为什么发起这次学习}

**阅读范围**：
- {文件或目录}

**新确认的事实**：
- {事实 1}
- {事实 2}

**发现的空白或冲突**：
- {空白或冲突}

**更新了哪些知识文档**：
- {文档路径}

**后续建议动作**：
- {建议}
```

## 5. 学习日志

## 2026-04-28 10:55 - 建立首批知识库骨架文档

**学习类型**：总览学习

**触发原因**：进入 Phase 2 的第二步，需要为 `PaperNormAI-knowledge-builder` 建立第一批可写入、可导航、可回放的知识库骨架文档。

**阅读范围**：
- 仓库根目录结构
- `.github/copilot-instructions.md`
- `.ai/agents/PaperNormAI-knowledge-builder.agent.md`
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`
- `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`

**新确认的事实**：
- 当前仓库已经落地了 AI 治理文档、两份架构蓝图、knowledge-builder agent 和知识治理规范。
- 当前业务代码骨架尚未系统落地，因此首批知识文档必须明确区分“当前事实”和“蓝图目标”。
- 当前最优先建立的知识入口是 `000-doc-map.md`、`100-system-overview.md`、`700-capability-map.md` 和 `900-learning-log.md`。

**发现的空白或冲突**：
- 当前尚无 `000-doc-map.md`，在本次任务前知识导航入口缺失。
- 当前尚无专题知识文档，后续数据库、API、前端、领域模型和调用链知识仍待建立。
- 当前蓝图中的 `backend/`、`clients/`、`template-library/` 仍未由业务代码确认落地。

**更新了哪些知识文档**：
- `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`
- `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`
- `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md`
- `docs/knowledge/PaperNormAI-knowledge/900-learning-log.md`

**后续建议动作**：
- 继续进入 Phase 2 的下一步，建立 `200-database-models.md`、`300-backend-kernel-services.md`、`400-api-architecture.md`、`500-frontend-architecture.md`、`600-domain-models.md` 的骨架文档。
- 在功能开发 agent 建立前，先把知识入口和总览层级补齐。

## 2026-05-01 20:00 - 建立专题知识骨架文档（200-800 系列）

**学习类型**：专题学习

**触发原因**：Phase 2 第二步的后续动作，在首批骨架文档（000/100/700/900）完成后，继续建立数据库模型、后端核心服务、API 架构、前端架构、领域模型和跨层调用链六大专题知识文档。

**阅读范围**：
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`
- `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`

**新确认的事实**：
- 后端核心服务以规则引擎（L1/L2/L3 分层设计）为第一核心，模板系统为第一核心资产。
- API 层采用 RESTful 设计，认证采用 JWT，文档校验采用异步 job 模型。
- 前端技术栈为 React + TypeScript，状态管理采用 React Query + Context。
- 领域模型与数据库模型分离，采用依赖反转原则（Domain 定义接口，Infrastructure 实现）。
- 跨层调用链遵循 API → Application → Domain → Infrastructure 的分层路径。

**发现的空白或冲突**：
- 多个技术选型尚未确认（Web 框架 FastAPI/Flask、AI 服务接入、job 队列选型、ORM 框架、依赖注入容器等）。
- 数据库选型（PostgreSQL vs SQLite）尚未确定。
- 样式方案（CSS Modules/Tailwind/styled-components）和 UI 组件库尚未选型。

**更新了哪些知识文档**：
- `docs/knowledge/PaperNormAI-knowledge/200-database-models.md` — 数据库模型蓝图
- `docs/knowledge/PaperNormAI-knowledge/300-backend-kernel-services.md` — 后端核心服务蓝图
- `docs/knowledge/PaperNormAI-knowledge/400-api-architecture.md` — API 架构蓝图
- `docs/knowledge/PaperNormAI-knowledge/500-frontend-architecture.md` — 前端架构蓝图
- `docs/knowledge/PaperNormAI-knowledge/600-domain-models.md` — 领域模型蓝图
- `docs/knowledge/PaperNormAI-knowledge/800-cross-layer-call-chains.md` — 跨层调用链蓝图

**后续建议动作**：
- 继续进入 Phase 2 的下一步：建立 `PaperNormAI-feature-development.agent.md`（Phase 4 的执行 agent）。
- 创建 4 个 skill 模块：`issue-evaluator`、`feature-readiness`、`feature-development`、`fix-development`。

---

## 2026-05-05 - Phase 1 核心链路完成 + 知识系统问题发现

**学习类型**：增量学习

**触发原因**：Phase 1 全部 KG 完成后，发现知识系统（skills/知识文档）未随开发进度更新，存在严重过期事实。

**阅读范围**：
- `backend/app/infrastructure/docling/parser.py`
- `backend/app/domain/services/rule_extraction_service.py`
- `backend/app/domain/services/semantic_validation_service.py`
- `backend/app/infrastructure/ai/openai_provider.py`
- `backend/app/infrastructure/persistence/spec_session_repository.py`
- `docs/progress.md`、`handoff/BUILD-LOG.md`

**新确认的事实**：
- Phase 1 核心链路已完成：DoclingDocumentParser → RuleExtractionService → SemanticValidationService → CorrectionService
- Phase 2 表格/插图/公式解析已完成：TableInfo/FigureInfo/FormulaInfo
- 规则持久化已完成：SpecSessionModel + SpecSessionRepository
- DeepSeek 已集成：AI_PROVIDER=deepseek，deepseek-chat 模型
- 端到端验证通过：temp.docx 390段落，提取 17 条规则，检测 30 处违规
- Docling v2.x 实际 API：`doc.texts`（非 `doc.elements`）、`doc.groups`（DOCX 为空）

**发现的空白或冲突**：
- `.ai/skills/*.md` 为说明文档形态，非可执行 skill 形态
- `910-skill-run-log.md` 停在模板层，无真实运行记录
- `000-doc-map.md` 仍描述"业务代码骨架尚未落地"（已过期）
- `100-system-overview.md` 仍描述"当前还不能对后端代码做事实性描述"（已过期）
- `700-capability-map.md` 仍描述"蓝图已定义，未落代码"（已过期）

**更新了哪些知识文档**：
- `.ai/skills/issue-evaluator.md` — 改为可执行 skill 形态
- `.ai/skills/feature-readiness.md` — 改为可执行 skill 形态
- `.ai/skills/feature-development.md` — 改为可执行 skill 形态
- `.ai/skills/fix-development.md` — 改为可执行 skill 形态
- `docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md` — 补充真实运行记录
- `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md` — 更新为代码事实态
- `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md` — 更新为代码事实态
- `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md` — 更新为代码事实态

**后续建议动作**：
- 200/300/400/600/800 系列知识文档仍为蓝图描述，需要系统更新为代码事实态
- 每次功能开发后，应立即更新对应知识文档（不要等到积累后再批量更新）
- 开始搭建业务代码骨架（`backend/`、`clients/`、`template-library/`）。

## 2026-05-01 20:10 - 建立 Feature Development Agent 与 Skill 体系

**学习类型**：总览学习

**触发原因**：Phase 2 第二步完成后的后续动作，需要建立 Phase 4 执行层的 agent 和 skill 体系。

**阅读范围**：
- `.ai/agents/PaperNormAI-knowledge-builder.agent.md`（agent 设计参考）
- `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`（skill 设计指引）
- `BUILDER.md`（Builder 角色参考）

**新确认的事实**：
- Feature Development Agent 的职责是在知识库和蓝图指引下执行功能开发，并同步实现发现回知识库。
- 四个 skill 分工明确：issue-evaluator（评估复杂度/风险/优先级）、feature-readiness（判断就绪条件）、feature-development（指导开发步骤）、fix-development（指导缺陷修复）。
- Skill 运行日志单独记录在 `910-skill-run-log.md` 中。

**发现的空白或冲突**：
- 当前业务代码骨架尚未落地，feature-development agent 需在真实代码建立后才能发挥全部作用。
- Skill 体系的实际效果需要通过实际的功能开发过程验证。

**更新了哪些知识文档**：
- `.ai/agents/PaperNormAI-feature-development.agent.md` — 功能开发 agent
- `.ai/skills/issue-evaluator.md` — 问题评估 skill
- `.ai/skills/feature-readiness.md` — 功能就绪 skill
- `.ai/skills/feature-development.md` — 功能开发 skill
- `.ai/skills/fix-development.md` — 缺陷修复 skill
- `docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md` — skill 运行日志

**后续建议动作**：
- 进入 Phase 3：业务代码骨架搭建（`backend/`、`clients/`、`template-library/` 目录结构）。
- 可选：开始 MVP 的核心功能实现（文档解析服务、规则引擎 L1 实现）。

## 2026-05-01 22:30 - 完成 Phase 3：业务代码骨架搭建

**学习类型**：流程学习

**触发原因**：用户指令进入 Phase 3，按 MVP 工程架构蓝图搭建 backend/、clients/、template-library/ 目录结构。

**阅读范围**：
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`（第 5 节：工程目录蓝图）

**新确认的事实**：
- Backend 目录结构完全按照蓝图建立：app/core（配置/数据库/依赖注入）、app/domain（entities/services/repositories）、app/application（use cases）、app/infrastructure（docx/storage/persistence/ai）、app/api（endpoints）。
- Frontend 目录结构采用 clients/apps/web + clients/packages 的双层结构，符合蓝图意图。
- Template library 包含 JSON Schema 和两个示例模板文件（清华硕士、北大本科）。

**发现的空白或冲突**：
- Repository 实现类中大多数方法仍是 TODO placeholder，需要后续实现。
- DocumentParser 只返回空结构，python-docx 集成尚未实现。
- Frontend 只有基础路由骨架，页面组件尚未实现。

**更新了哪些知识文档**：
- `backend/app/` — 完整四层架构骨架（43 个 Python 文件）
- `clients/apps/web/` — React + TypeScript + Vite 初始项目结构
- `clients/packages/` — API client 和 TypeScript 类型定义
- `template-library/` — 模板 Schema 和两个示例模板

**后续建议动作**：
- Phase 4：实现 MVP 核心功能（DocumentParser、RuleEngine L1 实现）。
- 或继续完善骨架：Repository 实现、数据库迁移、Alembic 配置。

## 2026-05-01 22:45 - 完成 Phase 4：MVP 核心功能实现

**学习类型**：专题学习

**触发原因**：用户指令进入 Phase 4，实现 DocumentParser 真实解析和 RuleEngine L1 规则。

**阅读范围**：
- `backend/app/infrastructure/docx/document_parser.py`（原有空壳结构）
- `backend/app/domain/services/rule_engine.py`（原有空壳结构）
- python-docx 官方文档

**新确认的事实**：
- DocumentParser 已实现真实的 python-docx 解析逻辑：
  - `_parse_paragraphs()` 遍历文档段落
  - `_parse_tables()` 处理表格
  - 提取 font_name、font_size、line_spacing、paragraph_spacing、alignment 等属性
  - 提取 document metadata（title、author、word_count）
  - `_check_generic_rule()` 提供通用的规则检查能力
- RuleEngine L1 规则已实现完整逻辑：
  - `font_name_body`：检测正文段落字体是否为预期字体（支持多个允许值）
  - `font_name_heading`：检测标题段落字体
  - `font_size_body`：检测正文字号（含 tolerance 支持）
  - `line_spacing`：检测行距（含 tolerance 支持）
  - `paragraph_spacing`：检测段前段后间距
  - L3 规则通过 AIEnhancementService 增强（需要手动 enable）
- L1 规则返回第一个匹配的错误结果，而不是列举所有错误（性能优先）

**发现的空白或冲突**：
- `page_margin` 检查暂未实现（python-docx 不直接暴露页面级属性）
- AI 增强功能需要手动调用 `ai_enhancement.enable()` 才能启用
- Repository 实现仍为 placeholder，数据库持久化尚未完成

**更新了哪些知识文档**：
- `backend/app/infrastructure/docx/document_parser.py` — 真实 python-docx 解析实现
- `backend/app/domain/services/rule_engine.py` — L1/L2/L3 规则实现
- `backend/requirements.txt` — 添加 python-docx 依赖
- `backend/tests/unit/test_document_parser.py` — DocumentParser 单元测试
- `backend/tests/unit/test_rule_engine.py` — RuleEngine 单元测试

**后续建议动作**：
- 实现 CorrectionExecutor 的修正逻辑
- 实现 Repository 的真实数据库操作（SQLAlchemy）
- 完善 page_margin 检查（需读取 section 属性）

## 2026-05-01 23:15 - 完成 CorrectionExecutor 修正逻辑实现

**学习类型**：专题学习

**触发原因**：用户指令继续实现 CorrectionExecutor 修正逻辑。

**阅读范围**：
- `backend/app/domain/services/correction_executor.py`（原有空壳）
- `backend/app/infrastructure/docx/document_parser.py`（ParsedDocument 结构）

**新确认的事实**：
- `CorrectionExecutor` 已实现完整的修正执行逻辑：
  - `execute()`：对 approved 状态的 plan 应用修正
  - `execute_and_save()`：执行修正并写入新的 .docx 文件
  - `generate_correction_plans()`：从 ValidationResult 生成 CorrectionPlan
  - `approve_plan()` / `skip_plan()`：plan 状态管理
- `DocumentWriter` 是新创建的基础设施组件：
  - `apply_corrections()`：将修正应用到 ParsedDocument（ immutable 操作）
  - `write_to_docx()`：将修正后的 ParsedDocument 写回 .docx 文件
  - 支持段落、标题、表格三种元素类型
  - 应用 font_name、font_size、line_spacing、paragraph_spacing 等属性
- 采用 immutable 模式：通过 `replace()` 创建新对象，不修改原始对象

**发现的空白或冲突**：
- 之前 `_determine_action_type` 返回字符串而非 `CorrectionActionType` enum
- 已修复：返回正确的 enum 类型
- `action_type` 枚举值需要与前端约定的值一致

**更新了哪些知识文档**：
- `backend/app/domain/services/correction_executor.py` — 完整修正逻辑实现
- `backend/app/infrastructure/docx/document_writer.py` — 新建，文档写入器
- `backend/app/infrastructure/docx/__init__.py` — 导出 DocumentWriter
- `backend/tests/unit/test_correction_executor.py` — 完整单元测试

**后续建议动作**：
- 实现完整的 API endpoint（upload -> validate -> correct -> download 流程）
- 添加 page_margin 检查（需要读取 document section 属性）
- 添加 Alembic 数据库迁移配置

## 2026-05-02 00:10 - 完成完整 API Endpoint 流程实现

**学习类型**：专题学习

**触发原因**：用户指令继续实现完整 API endpoint 流程。

**阅读范围**：
- `backend/app/api/endpoints/documents.py`（原有空壳）
- `backend/app/api/endpoints/validations.py`（原有空壳）
- `backend/app/api/dependencies.py`（新建）

**新确认的事实**：
- API 认证通过 JWT Bearer Token 实现：
  - `get_current_user` dependency 从 token 解析 user_id
  - `get_optional_current_user` 支持可选认证
- 文档上传 API 已完整实现：
  - 文件类型验证（.docx）
  - 文件大小验证（max_upload_size）
  - SHA256 哈希去重检查
  - 异步存储到 FileStorage
  - DocumentRepository 持久化
- 校验任务 API 已完整实现：
  - BackgroundTasks 异步执行校验
  - `_run_validation_job` 后台任务函数
  - ValidationJobModel 和 ValidationResultModel 持久化
  - 轮询获取结果（GET /validations/{job_id}）
- 修正任务 API 已完整实现：
  - 从 ValidationResult 生成 CorrectionPlan
  - CorrectionExecutor 执行修正
  - DocumentWriter 写回 .docx
  - 支持下载修正后的文档

**发现的空白或冲突**：
- 校验结果创建时只传了 id 而非完整 result 对象，可能导致某些字段丢失
- 修正任务的 plan_ids 需要确保在同一个 document 下

**更新了哪些知识文档**：
- `backend/app/api/dependencies.py` — 新建，JWT 认证依赖
- `backend/app/api/endpoints/documents.py` — 完整文档 CRUD API
- `backend/app/api/endpoints/validations.py` — 完整校验任务 API
- `backend/app/api/endpoints/corrections.py` — 新建，修正任务 API
- `backend/app/api/routes.py` — 添加 corrections router
- `backend/app/api/endpoints/__init__.py` — 导出 corrections

**后续建议动作**：
- 配置 Alembic 数据库迁移
- 添加模板管理 API（template CRUD）
- 完善 auth API（login/register 实现）

## 2026-05-02 00:20 - 完成 page_margin 检查实现

**学习类型**：专题学习

**触发原因**：用户指令继续实现 page_margin 检查。

**阅读范围**：
- `backend/app/infrastructure/docx/document_parser.py`（SectionProperties 部分）
- `backend/app/domain/services/rule_engine.py`（_check_page_margin 部分）

**新确认的事实**：
- DocumentParser 新增 `_extract_section_properties` 方法，从 python-docx 的 section 属性提取页面设置
- `SectionProperties` dataclass 包含：page_width、page_height、margin_top、margin_bottom、margin_left、margin_right、orientation
- pt_to_cm 转换：1pt = 2.54/72 cm
- `_check_page_margin` 使用 tolerance 参数判断是否超标，默认 0.1cm
- 模板中 page_margin 规则参数：`top`、`bottom`、`left`、`right`（单位 cm）

**发现的空白或冲突**：
- 之前 page_margin 检查是 placeholder，返回 None
- 已修复：现在读取 section 属性并与模板参数比较

**更新了哪些知识文档**：
- `backend/app/infrastructure/docx/document_parser.py` — 添加 SectionProperties 和 _extract_section_properties
- `backend/app/domain/services/rule_engine.py` — 完整实现 _check_page_margin 方法
- `backend/tests/unit/test_rule_engine.py` — 添加 page_margin 测试

**后续建议动作**：
- 配置 Alembic 数据库迁移
- 添加模板管理 API（template CRUD）
- 完善 auth API（login/register 实现）

## 2026-05-01 23:45 - 完成 SQLAlchemy 数据库模型与 Repository 实现

**学习类型**：专题学习

**触发原因**：用户指令继续实现 Repository 数据库操作。

**阅读范围**：
- `backend/app/infrastructure/persistence/models.py`（新建）
- `backend/app/infrastructure/persistence/mappers.py`（新建）
- `backend/app/domain/repositories.py`（原有接口定义）

**新确认的事实**：
- 数据库模型层已完整建立（7 张表）：
  - `UserModel`：用户表（email 唯一索引）
  - `DocumentModel`：文档表（user_id、file_hash 索引）
  - `TemplateModel`：模板表（university 索引，rules_json 存储规则）
  - `ValidationJobModel`：校验任务表（document_id、template_id 外键）
  - `ValidationResultModel`：校验结果表（job_id 外键）
  - `CorrectionPlanModel`：修正计划表（result_id 外键）
  - `CorrectionJobModel`：修正任务表
  - `AuditLogModel`：审计日志表
- Mapper 层实现实体 ↔ 模型双向转换：
  - `DocumentMapper`、`TemplateMapper`、`ValidationResultMapper`、`CorrectionPlanMapper`
  - Template 的 rules 以 JSON 格式存储在 rules_json 字段
- Repository 实现（真实数据库操作）：
  - `DocumentRepository`：save、find_by_id、find_by_user_id、find_by_hash、update、delete、find_by_status、count_by_user
  - `TemplateRepository`：save、find_by_id、find_by_university、find_active、update、deactivate、find_by_discipline、count_active
  - `UserRepository`：save、find_by_id、find_by_email、exists_by_email

**发现的空白或冲突**：
- 模板 rules_json 存储格式需要与前端协商一致
- PostgreSQL UUID 类型与 SQLite 的兼容性需要注意

**更新了哪些知识文档**：
- `backend/app/infrastructure/persistence/models.py` — 7 张 SQLAlchemy 模型
- `backend/app/infrastructure/persistence/mappers.py` — 4 个 Mapper 类
- `backend/app/infrastructure/persistence/document_repository.py` — 真实实现
- `backend/app/infrastructure/persistence/template_repository.py` — 真实实现
- `backend/app/infrastructure/persistence/user_repository.py` — 真实实现
- `backend/tests/unit/test_repositories.py` — Repository 和 Mapper 单元测试
- `backend/requirements.txt` — 添加 psycopg2-binary、alembic 依赖

**后续建议动作**：
- 实现完整的 API endpoint（upload -> validate -> correct -> download 流程）
- 添加 page_margin 检查（需要读取 document section 属性）
- 配置 Alembic 数据库迁移

## 2026-05-14 12:00 - Step 8B: 前端接入（Next.js App Router）

**学习类型**：流程学习

**触发原因**：Step 8B-Pre ValidationReport 查询 API 完成后，开始前端接入实现。

**阅读范围**：
- `clients/apps/web/package.json`（Next.js 16.2.6）
- `clients/packages/api-client/client.ts`（access_token key）
- `clients/packages/types/index.ts`（类型定义）

**新确认的事实**：
- Next.js 已通过 create-next-app 创建在 clients/apps/web/
- 纯 Client Components 模式（所有页面 'use client'）
- 去掉了 react-query，使用 useState + useEffect
- Token key: access_token（与 client.ts 一致）
- API_BASE: NEXT_PUBLIC_API_BASE_URL 环境变量
- 极简 /login 页面（POST /auth/login）
- 三个 spec 流程页面：/spec → /spec/[sessionId] → /spec/[sessionId]/report/[reportId]

**发现的空白或冲突**：
- Vite 项目已替换为 Next.js，clients/packages/api-client 未使用（类型复制到 src/lib/types.ts）

**更新了哪些知识文档**：
- `clients/apps/web/.env.local`（NEXT_PUBLIC_API_BASE_URL）
- `clients/apps/web/src/lib/api.ts`（API 调用）
- `clients/apps/web/src/lib/auth.ts`（getAccessToken + useRequireAuth）
- `clients/apps/web/src/lib/types.ts`（类型定义）
- `clients/apps/web/src/app/login/page.tsx`（登录页）
- `clients/apps/web/src/app/spec/page.tsx`（上传 spec）
- `clients/apps/web/src/app/spec/[sessionId]/page.tsx`（上传 thesis）
- `clients/apps/web/src/app/spec/[sessionId]/report/[reportId]/page.tsx`（报告展示）

**后续建议动作**：
- Step 8B 四件套对账
- 端到端联调验证

---

## 2026-05-14 13:00 - P1 知识文档刷新（400/500/700/800）

**学习类型**：增量学习

**触发原因**：Step 8B 完成后按外部工程系统要求执行 P1 知识文档刷新，将 400/500/700/800 系列文档更新为代码事实态。

**阅读范围**：
- `docs/knowledge/PaperNormAI-knowledge/400-api-architecture.md`
- `docs/knowledge/PaperNormAI-knowledge/500-frontend-architecture.md`
- `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md`
- `docs/knowledge/PaperNormAI-knowledge/800-cross-layer-call-chains.md`
- `clients/apps/web/src/app/spec/[sessionId]/report/[reportId]/page.tsx`

**新确认的事实**：
- 400-api-architecture.md：`GET /spec/reports/{report_id}` 已新增（Step 8B-Pre），返回字段完整对齐前端需求
- 500-frontend-architecture.md：Next.js App Router 已替换 Vite，纯 Client Components，无 react-query，access_token 存 localStorage
- 700-capability-map.md：前端 Web 界面 + ValidationReport 查询 API 均已实现
- 800-cross-layer-call-chains.md：新增 Step 4.5/4.6/4.7 三条调用链（validate → get-report → 前端渲染）

**发现的空白或冲突**：
- 500 文档描述与代码实现不符（React Query / Vite / 蓝图阶段）
- 800 文档 spec 链路停留在"返回违规统计"（实际已深度持久化 + 查询 API）

**更新了哪些知识文档**：
- `400-api-architecture.md` — 新增 Step 6/7 ValidationReport 持久化边界，GET /reports 端点，Section 6 新增
- `500-frontend-architecture.md` — 全面重写为代码事实态（Next.js / 无 react-query / access_token）
- `700-capability-map.md` — 更新待实现能力表（前端界面 + ValidationReport 查询 API）
- `800-cross-layer-call-chains.md` — 新增 4.5/4.6/4.7 三条 spec 链路，更新层间边界观察（Step 6A 架构修复）

**后续建议动作**：
- P2 决策：进入"前端继续扩展（修正文档下载）"还是"治理重构（API → application 下沉重构）"

---

## 2026-05-14 14:00 - Step 9: Correction Download Frontend Integration

**学习类型**：流程学习

**触发原因**：Step 8B 完成"登录→报告展示"闭环后，继续推进用户价值链到"修正文档下载"。

**阅读范围**：
- `backend/app/api/endpoints/corrections.py`（POST /corrections/、GET /corrections/{job_id}、GET /corrections/{job_id}/download）
- `backend/app/api/endpoints/spec_validation.py`（document_name 追加到 SpecValidationResponse）
- `clients/apps/web/src/app/spec/[sessionId]/report/[reportId]/page.tsx`
- `clients/apps/web/src/lib/api.ts`

**新确认的事实**：
- corrections.py 的 document_id 需要 UUID，必须先上传 thesis 到 DocumentModel
- 修正链路：corrections.py → DocumentRepository → 读取 file_path → DocumentParser → CorrectionExecutor → DocumentWriter
- spec 链路验证 thesis 后不上传到 DocumentModel（只做临时文件解析）
- Step 9 修复：POST /validate-with-spec 验证后立即持久化 thesis 为 DocumentModel（document_id = report_id）
- 轮询状态机：pending → running → completed/failed
- 下载 URL 无法直接通过 <a href=URL> 下载（token 丢失），改用 fetch + Authorization header + Blob.createObjectURL

**发现的空白或冲突**：
- spec 链路不上传 thesis 到 DocumentModel（只做临时文件解析），corrections.py 需要 document_id
- 当前 corrections.py 修正执行依赖 DocumentParser + DocumentWriter（基于 python-docx），不是 Docling 路径
- 下载 URL 直接放 href 会丢失 Bearer token，改用 fetch + Blob

**更新了哪些知识文档**：
- `docs/progress.md` — 更新 Step 9 进行中，追加 correction 链路到当前可用链路
- `backend/app/api/endpoints/spec_validation.py` — SpecValidationResponse 追加 document_name 字段 + thesis 持久化
- `backend/app/api/endpoints/corrections.py` — CorrectionResponse 追加 error_message 字段
- `clients/apps/web/src/lib/types.ts` — 新增 CorrectionJobResponse、CorrectionStatus 接口
- `clients/apps/web/src/lib/api.ts` — 新增 createCorrectionJob、getCorrectionJob、getCorrectionDownloadUrl
- `clients/apps/web/src/app/spec/[sessionId]/page.tsx` — 简化跳转
- `clients/apps/web/src/app/spec/[sessionId]/report/[reportId]/page.tsx` — 新增"Generate Corrected Document"按钮 + 轮询下载逻辑

**后续建议动作**：
- Step 9 四件套对账
- 端到端联调验证（修正文档下载）

---

## 2026-05-14 07:00 - Step 8B-Pre: ValidationReport 查询 API

**学习类型**：增量学习

**触发原因**：Step 8B 前端接入（Next.js）立项时发现前置阻塞 — 前端需要 GET /spec/reports/{report_id} 查询违规明细，但该 API 不存在。

**阅读范围**：
- `backend/app/api/endpoints/spec_validation.py`
- `backend/app/infrastructure/persistence/models.py`

**新确认的事实**：
- Step 7 已将 ValidationReport + ViolationDetail 持久化到数据库，但无查询 API
- 新增 GET /api/v1/spec/reports/{report_id} 端点
- 使用 joinedload 预加载 violations 避免 N+1 查询
- ViolationDetailResponse 包含：id, category, severity, description, paragraph_index, text, original_content, suggested_fix, context_before, context_after, user_modified_fix
- ValidationReportResponse 包含：report_id, session_id, document_name, template_name, created_at, total/error/warning/info_count, violations[]

**发现的空白或冲突**：
- 前端无法展示违规明细，因为 GET /spec/reports/{report_id} 不存在

**更新了哪些知识文档**：
- `backend/app/api/endpoints/spec_validation.py`（新增端点 + Response 模型）
- `docs/progress.md`（Active Step → Step 8B-Pre，已完成）
- `handoff/BUILD-LOG.md`（新增 Step 8B-Pre 记录）
- `docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md`（新增 Step 8B-Pre fix-development 记录）

**后续建议动作**：
- Step 8B 前端接入（Next.js 新建项目）
- 记录 OMA 借鉴点（可观测性/retry/多 provider 抽象）到技术债务

---

## 2026-05-14 06:45 - Step 8A: Governance Hardening

**学习类型**：流程学习

**触发原因**：Step 7 完成后 grill-me 确认的根因不是"功能缺"而是"门禁缺失"。优先修防复发机制，再做前端接入。

**阅读范围**：
- `.ai/skills/feature-readiness.md`（现有版本）
- `.github/copilot-instructions.md`（Section 3: 分层规则）

**新确认的事实**：
- 新增 `architecture-check.md` skill：分层合规检查（4项）+ 边界合规检查（3项）+ 持久化合规检查（3项）+ 例外记录机制
- feature-readiness.md 新增 Step 3 架构影响初筛（5项检查）：涉及跨层依赖变化、改变依赖方向、引入新外部依赖、修改持久化模型/schema、回归面超出当前范围
- 串联关系：feature-readiness → (Yellow) → architecture-check（强制双门禁）
- 优先级：P0 architecture-check + feature-readiness 架构初筛，P1 前端接入，P2 API→application 下沉重构

**发现的空白或冲突**：
- 之前 feature-readiness 只有技术就绪，无架构影响初筛，导致 Step 1-7 实现时无门禁拦截架构违规

**更新了哪些知识文档**：
- `.ai/skills/architecture-check.md`（新建）
- `.ai/skills/feature-readiness.md`（新增 Step 3 + 串联关系）
- `handoff/BUILD-LOG.md`（Step 7 COMPLETE + Step 8A 待完成）
- `docs/progress.md`（Active Step → Step 8A）

**后续建议动作**：
- Step 8A 四件套对账
- Step 8B 前端接入

---

## 2026-05-14 06:05 - Step 7: ValidationReport 深度持久化

**学习类型**：增量学习

**触发原因**：Step 6A 架构修复完成后，验证后端核心链路收敛性。选择 ValidationReport 深度持久化作为 Step 7 方向，原因：刚修完架构边界，最应该验证后端核心链路。

**阅读范围**：
- `backend/app/domain/entities/validation_report.py`
- `backend/app/infrastructure/persistence/models.py`
- `backend/app/api/endpoints/spec_validation.py`
- `handoff/ARCHITECT-BRIEF.md`（Step 7 Definition of Done）

**新确认的事实**：
- ValidationReport 领域实体已存在（含 violations 列表、_recalc_stats()）
- ViolationDetail 领域实体已存在（含 category/severity/description/location/suggested_fix）
- Spec 语义校验端点 `POST /spec/validate-with-spec` 当前仅返回计数
- 新增 ValidationReportModel + ViolationDetailModel 到 models.py
- SpecValidationResponse 追加 report_id 字段
- 同步落库在 API 编排层完成（spec_validation.py），Domain Service 仅产出 ValidationReport
- Architecture gate: feature-readiness ✅ Green, architecture-check 🟡 Yellow（MVP 例外）

**发现的空白或冲突**：
- 数据库迁移路径尚未定义（Alembic 未建立），MVP 阶段使用 create_all()
- API 层继续承担编排是 MVP 务实落点，后续需下沉到 application 层

**更新了哪些知识文档**：
- `handoff/ARCHITECT-BRIEF.md`（Step 7 Definition of Done + MVP 例外记录）
- `handoff/BUILD-LOG.md`（Step 6A + Step 7 待立项）
- `docs/progress.md`（Active Step → Step 7）

**后续建议动作**：
- Step 7 完成并通过四件套对账后，考虑前端接入
- application 层下沉重构作为未来工作项记录

---

## 2026-05-14 05:25 - Step 6A: Architecture Repair — 清除 domain → infrastructure 直接依赖

**学习类型**：增量学习

**触发原因**：grill-me 审查发现当前代码库存在系统性架构违规 — domain 层直接依赖 infrastructure 层（9 处违规 / 7 个 service 文件），违反 `api → application → domain → infrastructure` 分层约束。这些违规在实现时未被 skill 机制拦截，导致架构腐化已扩散。

**阅读范围**：
- `backend/app/domain/services/semantic_validation_service.py`
- `backend/app/domain/services/rule_extraction_service.py`
- `backend/app/domain/services/correction_service.py`
- `backend/app/domain/services/rule_engine.py`
- `backend/app/domain/services/correction_executor.py`
- `backend/app/domain/services/ai_enhancement_service.py`
- `backend/app/domain/services/template_service.py`
- `.github/copilot-instructions.md`（Section 3.1 分层规则）
- `docs/progress.md`、`handoff/BUILD-LOG.md`

**新确认的事实**：
- 确认 9 处违规分布：semantic_validation_service（2处）、rule_extraction_service（2处）、correction_service（1处）、rule_engine（1处）、correction_executor（2处）、ai_enhancement_service（1处）
- 违规类型：AI Provider 泄露（4处）、Docling 模型泄露（2处）、Docx Parser 模型泄露（3处）
- template_service.py ✅ 无违规（仅依赖 domain.entities 和 domain.repositories）
- 修复模式：domain 定义抽象接口（Protocol），application 层负责注入具体实现
- 新增 `domain/services/interfaces.py`：定义 `IAIProvider`、`IDocumentParser`、`IDocumentMerger`、`IDocumentWriter`、`IParsedDocument`、`ElementLike`
- 修复后 spec_validation.py 中的 wiring 已验证通过（RuleExtractionService + SemanticValidationService 可正确实例化）

**发现的空白或冲突**：
- feature-readiness.md 只检查"能不能开始做"，从未覆盖架构合规检查
- 流程上错误地把 readiness 当成了"架构安全检查"的替代品
- 问题根因在两层：skill 设计层（feature-readiness 缺维度）+ 流程门禁层（无强制架构检查）

**更新了哪些知识文档**：
- `handoff/ARCHITECT-BRIEF.md`（Step 6A 架构修复输入文档）
- `docs/progress.md`（Active Step → Step 6A）

**后续建议动作**：
- 完成四件套对账：900-learning-log.md（本条）+ 910-skill-run-log.md + memory/YYYY-MM-DD.md
- 刷新 300/600/800 知识文档为代码事实态（interfaces.py 新增 + 分层收敛）
- Step 7 立项前需重新完成 feature-readiness + architecture-check 双门禁

---

## 2026-05-06 11:30 - 建立 Step COMPLETE 四件套对账并刷新专题知识文档

**学习类型**：增量学习

**触发原因**：外部工程系统闭环审计后，发现 Step 完成后的知识与进度对账缺少强制机制，且 200/300/400/600/800 仍处于蓝图叙述。

**阅读范围**：
- `handoff/BUILD-LOG.md`
- `docs/progress.md`
- `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`
- `docs/knowledge/PaperNormAI-knowledge/200-database-models.md`
- `docs/knowledge/PaperNormAI-knowledge/300-backend-kernel-services.md`
- `docs/knowledge/PaperNormAI-knowledge/400-api-architecture.md`
- `docs/knowledge/PaperNormAI-knowledge/600-domain-models.md`
- `docs/knowledge/PaperNormAI-knowledge/800-cross-layer-call-chains.md`
- 相关代码：`backend/app/api/endpoints/*`、`backend/app/domain/*`、`backend/app/infrastructure/persistence/*`

**新确认的事实**：
- Step COMPLETE 后已明确四件套强制对账：`progress`、`900`、`910`、`memory`。
- API/领域/持久化核心链路均已代码落地，200/300/400/600/800 可切换到代码事实态。
- `000-doc-map.md` 中旧路径与旧状态描述已修正，导航与现状对齐。

**发现的空白或冲突**：
- 仍未把 `.ai/skills` 迁移为 IDE 原生技能目录（`.trae/skills/.../SKILL.md`）。
- 语义校验与规则引擎的双报告模型后续需要收敛策略。

**更新了哪些知识文档**：
- `handoff/BUILD-LOG.md`（新增 Step COMPLETE 四件套检查块）
- `.ai/skills/knowledge-sync.md`（新增四件套对账步骤）
- `docs/progress.md`（修复状态冲突）
- `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`（修复冲突与闭环图）
- `docs/knowledge/PaperNormAI-knowledge/200-database-models.md`
- `docs/knowledge/PaperNormAI-knowledge/300-backend-kernel-services.md`
- `docs/knowledge/PaperNormAI-knowledge/400-api-architecture.md`
- `docs/knowledge/PaperNormAI-knowledge/600-domain-models.md`
- `docs/knowledge/PaperNormAI-knowledge/800-cross-layer-call-chains.md`

**后续建议动作**：
- 对 100/700 做同样的代码事实态复核，避免局部漂移。
- 决策是否落地 `.trae/skills` 原生技能目录。

## 6. 与其他文档的关联

- 前置文档：
  - `.github/copilot-instructions.md`
  - `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`
- 相关文档：
  - `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`
  - `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`
  - `docs/knowledge/PaperNormAI-knowledge/700-capability-map.md`

## 7. 当前已知边界

1. 本文件当前只记录了知识库骨架建立阶段的学习活动。
2. 本文件的摘要日志应保持高价值、可回放，而不是变成逐步操作流水账。
3. 更细粒度的过程上下文可在 `logs/knowledge-builder/` 下扩展。

## 8. 待确认问题

1. 后续是否需要为每一次专题学习都同步生成独立详细日志文件。
2. 当业务代码开始落地后，学习日志是否需要增加”关联提交”字段。
3. 是否需要后续补建 `910-skill-run-log.md` 与 skill 体系同步使用。

## 9. 更新记录

**最近复核时间**：2026-05-14

**复核依据**：
- 代码范围：Step 8B 前端接入（Next.js App Router）
- 参考文档：
  - `clients/apps/web/src/lib/api.ts`
  - `clients/apps/web/src/app/`

**当前可信度**：高

**待确认点**：学习日志模板将来可能随着 skill 体系建立而扩展字段。

## 2026-05-15 02:00 - Step 9 端到端调试与 DocumentRepository UUID 类型修复

**学习类型**：专题学习 / 问题驱动

**触发原因**：Step 9 correction endpoint 持续返回 404 Document not found，despite document existing in DB.

**阅读范围**：
- `backend/app/infrastructure/persistence/document_repository.py`
- `backend/app/infrastructure/persistence/mappers.py`
- `backend/app/api/endpoints/corrections.py`

**新确认的事实**：
1. DocumentRepository.find_by_id uses raw SQL with `text()` to avoid PGUUID binding issues in SQLite
2. Raw SQL `SELECT * FROM documents WHERE id = :id` returns row with `str` types for id/user_id columns
3. Creating `DocumentModel(id=row.id, user_id=row.user_id, ...)` passed strings directly, NOT UUID objects
4. DocumentMapper.to_domain then passed `model.user_id` (string) to Document entity which has `user_id: UUID` field
5. The comparison `document.user_id != current_user.id` compared `str` vs `uuid.UUID`, always returning False
6. Fix: convert row.user_id to UUID when constructing DocumentModel in find_by_id
7. `.env` file with DEEPSEEK_API_KEY is required for AI features to work — without it, rules extract as 0

**发现的空白或冲突**：
1. `DocumentRepository.find_by_id` was passing raw strings to DocumentModel instead of UUID objects
2. This caused user_id comparison failure in corrections.py even though document was found
3. DeepSeek API key (sk-a2fb983c14e54ca68409923b6373fcb1) was invalid — "Authentication Fails, Your api key is invalid"
4. Without valid API key, rule extraction returns 0 rules, validation returns 0 violations

**知识增量**：
- SQLite stores UUID as text but SQLAlchemy PGUUID type requires UUID object binding
- Raw SQL with `text()` returns strings, must convert to UUID for ORM column assignment
- Document comparison should use `str()` on both sides to avoid type mismatch

**关联提交**：无直接提交（调试过程）

**后续建议动作**：
- 调查 DeepSeek API key 为何失效，是否需要更新
- 在 spec_validation.py parse-spec 中添加验证当 rules_count == 0 时的警告
