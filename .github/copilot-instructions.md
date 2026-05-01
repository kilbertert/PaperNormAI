# PaperNormAI Copilot Instructions

> 本文档定义 PaperNormAI 的 AI 工程治理规则，用于约束所有 AI 参与的开发活动。所有 agent、skill 和直接代码生成行为均应遵守本文档约束。

## 0. 前置阅读要求

在进入任何非 trivial 开发任务前，AI 必须先确认已读取：

1. 本文档（`.github/copilot-instructions.md`）
2. `docs/knowledge/PaperNormAI-knowledge/000-doc-map.md`
3. 与任务相关的知识文档（由 doc-map 指引）
4. 相关架构蓝图（`docs/architecture/`）

**Trivial 任务定义**：单文件、单函数、明确输入输出、无跨层依赖、无架构影响的简单修改。

---

## 1. 产品边界约束

### 1.1 MVP 范围

**当前 MVP 只做**：

- Web SaaS 应用
- `.docx` 文档格式检测与修正
- 基于高校模板的规则校验
- 规则引擎 + AI 增强的混合方案

**当前 MVP 明确不做**：

- 桌面客户端
- Word 插件
- PDF 自动修正
- LaTeX 支持
- 多租户组织空间
- 复杂后台管理系统
- 团队协作、评论流、审批流

**违规示例**：

- ❌ "我们可以顺便加个 Electron 打包配置"
- ❌ "这个功能可以同时支持 PDF"
- ❌ "先预留多租户字段"

**正确做法**：

- ✅ 如果需求超出 MVP 范围，明确指出并询问是否调整范围
- ✅ 如果必须预留扩展位，在知识库中记录设计意图，而不是直接实现

### 1.2 核心价值定位

PaperNormAI 的第一核心是 **规则引擎与模板系统**，不是 AI 接入本身。

**这意味着**：

- 确定性格式问题（字体、行距、页边距）必须由规则引擎处理
- AI 只负责语义性判断（参考文献格式、引用一致性）
- 规则引擎必须在没有 AI 的情况下也能独立工作

**违规示例**：

- ❌ "用 AI 判断字体是否符合要求"
- ❌ "让 AI 直接生成修正后的文档"
- ❌ "AI 检测失败时整个校验流程中断"

**正确做法**：

- ✅ 字体、行距、页边距等确定性问题用规则引擎
- ✅ AI 输出必须转换为结构化 `RuleViolation`
- ✅ AI 失败时降级为仅规则引擎模式

---

## 2. 架构边界约束

### 2.1 模块化单体原则

PaperNormAI 采用 **Modular Monolith**，不是微服务架构。

**这意味着**：

- 部署上是单个后端服务
- 代码组织上按领域拆分（document / template / validation / correction）
- 模块间通过明确的数据契约解耦
- 不引入分布式通信、服务发现、API 网关等微服务基础设施

**违规示例**：

- ❌ "我们可以把规则引擎拆成独立服务"
- ❌ "用消息队列解耦模板服务和校验服务"
- ❌ "引入 gRPC 做模块间通信"

**正确做法**：

- ✅ 模块间通过 Python 函数调用
- ✅ 用明确的领域模型和用例服务解耦
- ✅ 如果未来需要拆分，在知识库中记录拆分边界设计

### 2.2 中间文档模型优先

业务逻辑不能直接依赖 `python-docx` 的原始对象。

**这意味着**：

- 必须先将 `.docx` 解析为 `ParsedDocument` 中间模型
- 规则引擎只面向 `ParsedDocument` 工作
- 修正逻辑基于 `CorrectionPlan`，由 writer 统一写回

**违规示例**：

- ❌ 规则代码中直接操作 `document.paragraphs[0].runs[0].font`
- ❌ AI 服务直接返回修改后的 `python-docx` 对象
- ❌ 前端直接接收 `python-docx` 序列化结果

**正确做法**：

- ✅ `infrastructure/docx/parser.py` 负责 docx → ParsedDocument
- ✅ 规则引擎输入输出都是领域模型
- ✅ `infrastructure/docx/writer.py` 负责 CorrectionPlan → docx

### 2.3 异步任务优先

文档解析、校验、修正不应在同步 HTTP 请求中完成。

**这意味着**：

- 上传文档后立即返回 `job_id`
- 后台 worker 执行解析、校验、修正
- 前端通过轮询或 WebSocket 获取 job 状态

**违规示例**：

- ❌ `POST /documents/validate` 同步返回完整报告
- ❌ 用户等待 30 秒后才看到结果
- ❌ 超时后重试导致重复执行

**正确做法**：

- ✅ `POST /documents/upload` 返回 `{"job_id": "xxx"}`
- ✅ `GET /validation-jobs/{job_id}` 查询状态
- ✅ job 状态：`pending | running | succeeded | failed`

---

## 3. 分层规则约束

### 3.1 依赖方向规则

```text
api → application → domain → infrastructure
                      ↓
                    models (ORM)
```

**允许的依赖**：

- `api` 可以依赖 `application`
- `application` 可以依赖 `domain` 和 `infrastructure`
- `domain` 不能依赖 `infrastructure`、`application`、`api`
- `infrastructure` 可以依赖 `domain`

**违规示例**：

- ❌ `domain/validation/rule.py` 中 `import infrastructure.ai.openai_client`
- ❌ `domain/template/matcher.py` 中 `import application.use_cases`
- ❌ `infrastructure/docx/parser.py` 中 `import api.schemas`

**正确做法**：

- ✅ `domain` 定义抽象接口，`infrastructure` 实现
- ✅ `application` 负责组装 domain 和 infrastructure
- ✅ 依赖注入通过 `core/dependencies.py` 统一管理

### 3.2 领域边界规则

四大领域模块不能相互直接依赖：

- `domain/document/`
- `domain/template/`
- `domain/validation/`
- `domain/correction/`

**违规示例**：

- ❌ `domain/validation/rule.py` 中 `from domain.correction import CorrectionPlan`
- ❌ `domain/template/matcher.py` 中 `from domain.validation import RuleEngine`

**正确做法**：

- ✅ 领域间通过 `application` 层的用例服务编排
- ✅ 共享的值对象放在各自领域内，通过参数传递

---

## 4. 目录与命名规则

### 4.1 新增文件位置判断

**后端 Python 文件**：

- 领域模型 → `backend/app/domain/{领域}/`
- 用例服务 → `backend/app/application/`
- 基础设施适配器 → `backend/app/infrastructure/{子系统}/`
- HTTP 接口 → `backend/app/api/v1/`
- ORM 模型 → `backend/app/models/`
- Pydantic schemas → `backend/app/schemas/`

**前端 TypeScript 文件**：

- 页面组件 → `clients/apps/web/src/pages/{功能}/`
- 功能组件 → `clients/apps/web/src/features/{功能}/`
- 通用组件 → `clients/packages/ui/src/`
- API 调用 → `clients/packages/api-client/src/`
- 类型定义 → `clients/packages/types/src/`

**模板文件**：

- 模板定义 → `template-library/universities/{学校}-{学历}-{年份}.yaml`
- 模板 schema → `template-library/schemas/`

**知识文档**：

- 知识库 → `docs/knowledge/PaperNormAI-knowledge/`
- 架构蓝图 → `docs/architecture/`
- 规则说明 → `docs/rules/`

### 4.2 命名约定

**Python**：

- 文件名：`snake_case.py`
- 类名：`PascalCase`
- 函数名：`snake_case`
- 常量：`UPPER_SNAKE_CASE`

**TypeScript**：

- 文件名：`PascalCase.tsx` (组件) 或 `camelCase.ts` (工具)
- 组件名：`PascalCase`
- 函数名：`camelCase`
- 常量：`UPPER_SNAKE_CASE`

**YAML**：

- 模板文件：`{university}-{degree}-{year}.yaml`
- 字段名：`snake_case`

---

## 5. 开发约束

### 5.1 继承 CLAUDE.md 的通用约束

本项目继承 `CLAUDE.md` 的所有约束，特别强调：

1. **Think Before Coding**：不确定时先问，不要猜
2. **Simplicity First**：最小化实现，不做推测性功能
3. **Surgical Changes**：只改必须改的，不顺手重构
4. **Goal-Driven Execution**：先定义验收标准，再开始实现

### 5.2 PaperNormAI 特有约束

#### 5.2.1 不做过度抽象

**违规示例**：

- ❌ 为单一规则创建抽象工厂
- ❌ 引入策略模式管理两个 AI provider
- ❌ 用观察者模式解耦 job 状态更新

**正确做法**：

- ✅ 三个以上相似场景再考虑抽象
- ✅ 简单 if-else 优于复杂设计模式
- ✅ 明确的函数调用优于隐式的事件驱动

#### 5.2.2 不引入无关依赖

**违规示例**：

- ❌ 引入 `pandas` 只为了读一个 CSV
- ❌ 引入 `celery` 但只用了最基础的任务队列
- ❌ 引入 `pydantic-settings` 但配置只有 3 个字段

**正确做法**：

- ✅ 优先使用标准库
- ✅ 引入新依赖前评估是否真的需要
- ✅ 在知识库中记录依赖选型理由

#### 5.2.3 不改无关模块

**违规示例**：

- ❌ 修复 validation bug 时顺便重构 template 模块
- ❌ 添加新规则时调整 docx parser 的代码风格
- ❌ 实现前端功能时"优化"后端 API 命名

**正确做法**：

- ✅ 一个任务只改一个模块
- ✅ 发现其他问题时记录到 issue，不要立即修复
- ✅ 重构需求单独提出，不混在功能开发中

---

## 6. 回归策略

### 6.1 功能开发的回归要求

新增功能必须满足：

1. **单元测试**：核心逻辑有测试覆盖
2. **集成测试**：跨层调用有端到端测试
3. **手动验证**：前端功能在浏览器中实际操作

**不允许**：

- ❌ "类型检查通过就算完成"
- ❌ "我测试过了，应该没问题"（没有测试代码）
- ❌ "这个改动很小，不需要测试"

### 6.2 缺陷修复的回归要求

修复 bug 必须：

1. **先写复现测试**：能稳定复现 bug 的测试用例
2. **确认测试失败**：运行测试，确认 FAIL
3. **最小化修复**：只改必须改的代码
4. **确认测试通过**：运行测试，确认 PASS
5. **回归验证**：确保没有破坏其他功能

### 6.3 规则调整的回归要求

调整规则引擎行为时：

1. **规则测试**：每条规则有独立测试
2. **模板测试**：模板加载规则的集成测试
3. **样本测试**：用真实论文样本验证

**测试样本库位置**：

- `backend/tests/fixtures/docs/valid/`
- `backend/tests/fixtures/docs/invalid/`

---

## 7. 文档更新规则

### 7.1 必须同步更新知识库的情况

以下变更必须评估是否需要更新知识库：

1. **新增或重构核心模块**
2. **API 契约变化**
3. **数据库模型变化**
4. **领域模型变化**
5. **规则引擎行为变化**
6. **模板系统结构变化**
7. **跨层调用链变化**
8. **Agent / skill 行为约束变化**

### 7.2 知识库更新流程

1. 完成代码变更
2. 识别受影响的知识文档（参考 `000-doc-map.md`）
3. 更新对应知识文档的"核心事实"部分
4. 更新"最近复核时间"和"复核依据"
5. 如果发现知识冲突，在"待确认问题"中记录
6. 在 `900-learning-log.md` 或 `910-skill-run-log.md` 中追加日志

### 7.3 不需要更新知识库的情况

- 单纯的 bug 修复（不改变模块职责）
- UI 样式调整
- 文案修改
- 测试代码补充
- 注释完善

---

## 8. 日志规则

### 8.1 学习日志

当 `PaperNormAI-knowledge-builder` agent 执行学习任务时，必须在 `900-learning-log.md` 中追加记录：

```markdown
## YYYY-MM-DD HH:MM - {学习目标}

**触发原因**：{为什么发起这次学习}

**阅读范围**：
- {文件路径或模块范围}

**新确认的事实**：
- {发现的架构事实}

**发现的空白或冲突**：
- {知识缺口或与现有认知的冲突}

**更新了哪些知识文档**：
- {文档路径}
```

### 8.2 技能运行日志

当任何 skill 被调用时，必须在 `910-skill-run-log.md` 中追加记录：

```markdown
## YYYY-MM-DD HH:MM - {skill 名称}

**解决了什么问题**：{任务描述}

**读了哪些知识源**：
- {知识文档路径}

**产出了哪些变更或判断**：
- {代码变更 / 评估结论}

**是否需要补知识库**：{是 / 否，原因}
```

### 8.3 详细日志

对于复杂任务，可在 `logs/{agent-or-skill}/YYYY-MM-DD-{task-name}.md` 中记录详细上下文。

---

## 9. 风险动作约束

### 9.1 高风险操作必须人工确认

以下操作不允许 AI 自动执行，必须先征得用户明确同意：

- 删除核心模块或文件
- 修改数据库 migration 文件
- 修改 `.github/` 下的 CI/CD 配置
- 修改 `copilot-instructions.md` 本身
- 修改架构蓝图文档
- 强制推送或重写 git 历史
- 修改生产环境配置

### 9.2 中风险操作需要说明理由

以下操作需要在执行前说明理由和影响范围：

- 引入新的第三方依赖
- 修改核心领域模型
- 调整 API 契约
- 重构跨层调用链
- 修改规则引擎核心逻辑

---

## 10. 知识优先策略

### 10.1 非 trivial 任务的标准流程

1. **读取治理规则**：本文档
2. **读取导航入口**：`000-doc-map.md`
3. **读取相关知识**：由 doc-map 指引的专题文档
4. **评估就绪性**：知识是否足够？需求是否清晰？
5. **进入实现**：基于知识和规则进行开发
6. **回写知识**：更新受影响的知识文档
7. **记录日志**：追加学习日志或技能运行日志

### 10.2 知识不足时的处理

如果发现知识库缺失或过时：

1. **不要猜测**：不要基于局部代码推断全局架构
2. **不要发明**：不要创造不存在于蓝图中的新结构
3. **先补认知**：调用 `PaperNormAI-knowledge-builder` 补充知识
4. **再进入开发**：基于更新后的知识库进行实现

### 10.3 知识冲突时的处理

如果代码与知识库冲突：

1. **代码是当前事实源**：以实际代码为准
2. **蓝图是目标约束源**：以架构蓝图为方向
3. **知识库是可维护认知层**：标记冲突，更新知识库
4. **不要盲目信任知识库**：知识可能过时，需要验证

---

## 11. 本文档的维护

### 11.1 谁可以修改本文档

- 项目负责人
- 经团队评审通过的架构调整

### 11.2 修改本文档时必须同步

- 更新 `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md` 中的治理层描述
- 更新 `docs/knowledge/PaperNormAI-knowledge/010-knowledge-governance.md`
- 通知所有相关 agent 和 skill 的维护者

### 11.3 本文档的版本管理

本文档的每次重大修改应：

- 在文档顶部记录修改日期和原因
- 在 git commit message 中明确标注
- 在团队内部同步变更内容

---

## 12. 总结：核心原则

1. **先认知，后开发**：非 trivial 任务必须先读知识库
2. **守边界，不越界**：严格遵守产品范围和架构边界
3. **重规则，轻 AI**：确定性问题用规则，AI 只做增强
4. **小步快跑，频繁验证**：最小化实现，持续回归
5. **留痕迹，可回放**：所有学习和执行都要有日志
6. **知识即资产**：把经验沉淀为可复用的外部系统

**当你不确定某个行为是否符合本文档约束时，默认选择：问清楚，再行动。**
