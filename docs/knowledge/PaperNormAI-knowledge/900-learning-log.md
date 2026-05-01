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

**最近复核时间**：2026-05-01

**复核依据**：
- 代码范围：当前知识库目录与相关治理 / 蓝图文档
- 参考文档：
  - `.ai/agents/PaperNormAI-knowledge-builder.agent.md`
  - `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`

**当前可信度**：高

**待确认点**：学习日志模板将来可能随着 skill 体系建立而扩展字段。
