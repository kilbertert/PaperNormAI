# PaperNormAI MVP 工程架构蓝图

> 本文档是 PaperNormAI 的 MVP 工程母文档，用于统一产品范围、工程边界、模块职责、数据流和后续实施顺序。后续实现计划、任务拆分、PRD 与技术设计均应以本文档为前置约束。
>
> AI 协作规则、知识沉淀路径、agent / skill 体系与日志机制，另见 `docs/architecture/2026-04-28-ai-engineering-collaboration-blueprint.md`。

## 1. 文档定位

### 1.1 这份文档解决什么问题

PaperNormAI 当前仍处于 idea 阶段，最大的工程风险不是“选错框架”，而是“在没有收敛产品核心之前就把交付形态和系统复杂度铺得过大”。

这份蓝图要解决的核心问题是：

1. 明确 MVP 的真实边界，避免 Web、桌面端、Word 插件三线并行。
2. 明确系统的第一核心是规则引擎与模板系统，而不是大模型接入本身。
3. 明确后端、前端、模板库、AI 服务、任务编排之间的职责边界。
4. 给后续实现计划提供统一的工程骨架，避免边做边改主结构。

### 1.2 本文档与现有实现计划的关系

- `docs/superpowers/plans/2026-04-28-paper-norm-ai.md` 是实现计划草案。
- 本文档是该计划的上位蓝图。
- 当两者冲突时，**以本蓝图的阶段范围、模块边界和工程约束为准**。

---

## 2. MVP 产品范围

### 2.1 MVP 要解决的单一核心问题

帮助学生上传 `.docx` 论文后，快速得到：

1. 当前论文与指定高校/规范模板之间的格式差异报告。
2. 可自动修正的问题的一键处理结果。
3. 不适合自动改动的问题说明与建议。

### 2.2 MVP 必须包含的能力

1. `.docx` 文档上传与解析。
2. 基于模板的确定性格式校验。
3. 基于规则结果的自动修正。
4. 检测报告展示与修正后文档下载。
5. 至少一套可运行的高校模板体系。
6. AI 对复杂格式问题的增强判断，但不主导核心流程。

### 2.3 MVP 明确不做的内容

以下内容不进入 MVP 首发范围：

1. Word 插件。
2. 桌面客户端。
3. PDF 自动修正。
4. LaTeX 支持。
5. 多租户组织空间。
6. 复杂后台管理系统。
7. 团队协作、评论流、审批流。
8. 全量高校模板覆盖。

### 2.4 MVP 成功标准

MVP 验证的不是“端覆盖”，而是以下三件事：

1. 规则引擎是否能稳定检测常见论文格式问题。
2. 自动修正是否能在用户可接受的精度上工作。
3. 模板系统是否能支撑后续高校扩展，而不需要反复改核心代码。

---

## 3. 架构原则

### 3.1 总体原则

1. **MVP 优先**：先闭环单一场景，不做三端齐发。
2. **模块化单体优先**：先用一个后端服务承载核心能力，不过早微服务化。
3. **规则优先于 AI**：确定性问题用规则解决，AI 只处理高歧义、高语义场景。
4. **模板即资产**：高校模板不是普通配置，而是产品核心资产。
5. **中间文档模型优先**：业务逻辑不直接耦合 `python-docx` 原始对象。
6. **异步任务优先**：文档检测与修正按 job 方式执行，而不是长同步请求。
7. **多端延后但预留扩展位**：MVP 只做 Web，但代码结构要给桌面和 Word 插件留出共享层。

### 3.2 架构风格

MVP 采用 **Modular Monolith（模块化单体）**：

- 部署上是一个后端服务。
- 代码组织上按领域拆边界。
- 外部接口统一由 HTTP API 暴露。
- 内部通过明确的数据契约和用例服务解耦。

这样做的原因是：

- 当前系统的复杂度来自规则、模板和文档处理，而不是分布式规模。
- 微服务会把早期精力浪费在网络边界、部署和运维上。
- 模块化单体允许未来按领域拆分，例如模板服务、校验服务、AI 服务。

---

## 4. 核心业务数据流

### 4.1 MVP 主流程

```text
用户上传 .docx
  -> 创建 document 记录
  -> 创建 validation job
  -> 解析 Word 文档为中间文档模型
  -> 选择模板（用户手选或系统推荐）
  -> 加载模板规则
  -> 执行规则引擎
  -> 对需要 AI 的规则发起增强检查
  -> 生成统一 ValidationReport
  -> 对可自动修正的问题生成 CorrectionPlan
  -> 应用修正并输出 corrected.docx
  -> 前端展示报告并提供下载
```

### 4.2 数据流约束

1. 规则引擎只面向中间文档模型工作。
2. AI 不直接写 Word 文档。
3. 自动修正必须基于结构化违规结果执行。
4. 文档解析、校验、修正都必须可复跑、可审计。
5. 模板版本必须进入报告结果，避免后续不可追踪。

---

## 5. 工程目录蓝图

推荐将仓库逐步演进为以下结构：

```text
PaperNormAI/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── domain/
│   │   │   ├── document/
│   │   │   ├── template/
│   │   │   ├── validation/
│   │   │   └── correction/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   │   ├── docx/
│   │   │   ├── ai/
│   │   │   ├── storage/
│   │   │   └── persistence/
│   │   └── api/
│   ├── tests/
│   └── alembic/
│
├── clients/
│   ├── apps/
│   │   └── web/
│   └── packages/
│       ├── api-client/
│       ├── types/
│       └── ui/
│
├── template-library/
│   ├── schemas/
│   └── universities/
│
├── docs/
│   ├── architecture/
│   ├── rules/
│   └── superpowers/plans/
│
└── docker/
```

### 5.1 为什么不继续沿用 `frontend/ desktop/ word-addin/ shared/`

因为它把“交付形态”和“共享资产”混在了一起。更适合的方式是：

- `clients/apps/*` 表示最终交付端。
- `clients/packages/*` 表示复用资产。
- 桌面端与 Word 插件先不实现，但工程位置提前保留。

---

## 6. 后端模块边界

## 6.1 `core/`：基础设施入口层

职责：

- 配置管理
- 数据库连接
- 依赖注入
- 认证授权
- 全局异常处理
- 日志与追踪配置

不负责：

- 文档解析业务
- 规则判断
- 模板匹配逻辑

## 6.2 `domain/document/`：文档领域

职责：

- 定义中间文档模型
- 定义 Paragraph、Run、Section、Table 等值对象
- 提供面向校验与修正的统一访问接口

不负责：

- 直接读写 `.docx`
- 调用 AI
- 处理 HTTP 请求

建议对象：

- `ParsedDocument`
- `ParagraphNode`
- `RunNode`
- `SectionNode`
- `DocumentMetadata`

## 6.3 `domain/template/`：模板领域

职责：

- 定义高校模板模型
- 管理模板规则集合
- 管理模板版本、适用学历层级、年份
- 承担模板选择与模板匹配逻辑

建议对象：

- `Template`
- `TemplateMetadata`
- `TemplateRuleSet`
- `TemplateMatcher`

## 6.4 `domain/validation/`：校验领域

职责：

- 定义规则接口
- 定义违规结果模型
- 定义规则引擎调度逻辑
- 定义报告聚合模型

建议对象：

- `Rule`
- `RuleContext`
- `RuleViolation`
- `ValidationReport`
- `RuleEngine`

## 6.5 `domain/correction/`：修正领域

职责：

- 定义哪些问题可自动修正
- 基于违规结果生成修正计划
- 将修正动作组织为可执行步骤

建议对象：

- `CorrectionAction`
- `CorrectionPlan`
- `CorrectionResult`
- `AutoFixPolicy`

## 6.6 `application/`：用例编排层

职责：

- 组织完整业务用例
- 串联解析、模板匹配、规则执行、AI 增强、修正输出
- 管理 job 生命周期

建议用例服务：

- `UploadDocumentUseCase`
- `RunValidationUseCase`
- `GenerateCorrectionUseCase`
- `GetValidationReportUseCase`

## 6.7 `infrastructure/`：对接真实世界

职责：

- `.docx` 读写
- AI provider 调用
- 数据库存储
- 文件存储
- 异步任务队列

子模块建议：

- `docx/`：Word 文档读写
- `ai/`：大模型 provider 封装
- `storage/`：本地或对象存储
- `persistence/`：ORM / repository 实现

## 6.8 `api/`：HTTP 接口层

职责：

- 参数接收
- 权限验证
- DTO 转换
- 返回 job 状态与报告结果

不负责：

- 写业务规则
- 直接操作文档对象
- 编排完整检测逻辑

---

## 7. 文档模型与 docx 读写策略

### 7.1 中间文档模型必须存在

系统不能让规则直接依赖 `python-docx` 的 paragraph/run 原始对象。MVP 就应引入中间文档模型：

```text
ParsedDocument
  metadata
  sections[]
  paragraphs[]
  tables[]
  images[]
```

### 7.2 为什么必须做中间层

因为未来以下能力都依赖这层抽象：

1. 从不同来源统一进入规则引擎。
2. 让自动修正逻辑只依赖稳定结构。
3. 将来扩展 PDF 检测或 LaTeX 检测时，复用校验逻辑。
4. 降低对 `python-docx` 库细节的耦合。

### 7.3 `docx` 子模块建议拆分

```text
infrastructure/docx/
  parser.py     # 读取 docx -> ParsedDocument
  writer.py     # 应用 CorrectionPlan -> corrected docx
  mapper.py     # docx 对象与领域模型映射
  locator.py    # 将 violation 定位回原文档位置
```

### 7.4 读写分离原则

- 解析器只负责读。
- 写入器只负责根据修正计划改文档。
- 规则不直接写文档。
- AI 不直接写文档。

---

## 8. 规则引擎蓝图

## 8.1 规则系统是第一核心

PaperNormAI 的核心价值不是“调用了 AI”，而是“把论文格式规范变成了稳定可执行的系统能力”。

因此规则系统必须具备以下能力：

1. 可按模板动态加载。
2. 可区分规则类别与严重等级。
3. 可输出结构化违规结果。
4. 可声明是否支持自动修正。
5. 可挂接 AI 增强检查，但不依赖 AI 才能运行。

## 8.2 规则分层

### L1：确定性规则

完全由规则引擎处理：

- 字体
- 字号
- 行距
- 段前段后
- 页边距
- 对齐方式
- 首行缩进
- 页眉页脚距离

### L2：结构性规则

规则引擎为主，必要时允许 AI 辅助：

- 标题层级
- 章节顺序
- 编号格式
- 图表标题位置
- 目录结构一致性

### L3：语义性规则

规则预筛，AI 做判断增强：

- 参考文献格式合理性
- 引用与参考文献一致性
- 标题语义与层级是否匹配
- 特殊院校自定义文本规范

## 8.3 规则接口设计要求

每条规则至少要回答：

1. 检查对象是什么。
2. 违规时如何描述。
3. 是否支持自动修正。
4. 修正时如何落到具体文档位置。

## 8.4 违规结果统一数据契约

推荐统一为：

```text
RuleViolation
  rule_id
  category
  severity
  location
  message
  expected
  actual
  fix_mode        # auto | suggest | manual
  suggestion
```

这份契约必须稳定，因为它会被：

- 前端报告展示使用
- 修正引擎使用
- Word 插件未来复用
- 导出报告使用

## 8.5 报告聚合模型

```text
ValidationReport
  id
  document_id
  template_id
  template_version
  summary
  score
  violations[]
  auto_fixable_count
  suggest_fix_count
  manual_fix_count
  generated_at
```

---

## 9. 模板系统蓝图

## 9.1 模板是核心资产，不只是数据库记录

模板系统不是简单的“学校名 + 几个字段”。它应该表达：

- 适用学校
- 适用学历层级
- 适用年份/版本
- 一组完整规则参数
- 特殊自定义规则
- 规则启用范围

## 9.2 模板推荐存储方式

MVP 阶段采用：

- **模板定义文件放仓库**：便于评审、版本化、差异比较。
- **数据库保存模板索引与启用状态**：便于产品控制和统计。

推荐结构：

```text
template-library/
  schemas/
    template.schema.yaml
  universities/
    tsinghua-undergrad-2024.yaml
    pku-master-2024.yaml
```

## 9.3 模板模型建议

```text
Template
  id
  name
  university
  degree_level
  version
  locale
  ruleset
  metadata
```

其中 `ruleset` 可进一步拆成：

- `font_rules`
- `spacing_rules`
- `margin_rules`
- `heading_rules`
- `reference_rules`
- `custom_rules`

## 9.4 模板匹配策略

MVP 建议分两步：

1. **用户手选模板为主**。
2. **系统推荐模板为辅**。

原因：

- 学校模板错配的代价很高。
- AI 自动推断学校/学历信息的稳定性前期不够可信。
- 用户手选更符合 MVP 的确定性目标。

---

## 10. AI 增强层蓝图

## 10.1 AI 的角色定位

AI 是增强器，不是主引擎。

它只应该处理：

1. 参考文献格式分析。
2. 引文与参考文献一致性检查。
3. 标题层级的语义建议。
4. 模板推荐辅助。
5. 自然语言说明生成。

它不应该直接负责：

1. 字体判断。
2. 行距判断。
3. 页边距计算。
4. Word 样式底层读写。
5. 结构化修正的直接执行。

## 10.2 AI 层工程结构建议

```text
infrastructure/ai/
  base.py
  factory.py
  providers/
    openai.py
    claude.py
    qwen.py
  prompts/
    reference_check.md
    citation_consistency.md
    heading_level.md
  cache.py
```

## 10.3 AI 接入约束

1. 所有 AI 输出必须结构化。
2. 不允许自由文本直接进入自动修正链路。
3. AI 调用结果要可缓存。
4. AI 失败不能阻塞整个规则引擎，只能降低增强能力。

## 10.4 模型供应商策略

MVP 阶段建议：

- 接入 1 个主 provider。
- 预留 provider 抽象层。
- 不要一开始就做多 provider 调度与竞价。

因为当前真正问题不是模型路由，而是业务结构是否收敛。

---

## 11. 存储与任务编排

## 11.1 数据库存储什么

MVP 数据库建议只存最必要的业务元数据：

- `users`
- `documents`
- `validation_jobs`
- `validation_reports`
- `templates`

## 11.2 文件存储什么

文档文件建议与数据库分离：

- 原始上传 `.docx`
- 修正后 `.docx`
- 未来可选导出的报告附件

MVP 可以先本地存储，部署阶段再切对象存储。

## 11.3 为什么要 job 模型

文档解析、规则执行、AI 检查、修正生成都不是轻请求。MVP 也不应把它们放在同步 HTTP 生命周期里。

推荐流程：

```text
POST /documents/upload
  -> create document
  -> create validation_job(status=pending)
  -> worker/process runs validation
  -> report ready
```

## 11.4 异步实现建议

MVP 可以按以下顺序渐进：

1. 第一步：应用内后台任务，先把 job 模型立起来。
2. 第二步：接入 Redis + 队列。
3. 第三步：需要时拆独立 worker。

这比一开始上完整分布式任务系统更稳。

---

## 12. API 边界建议

MVP 的 API 应该围绕“文档任务流”设计，而不是围绕数据库表 CRUD 设计。

推荐最小接口集合：

```text
POST   /api/v1/documents
GET    /api/v1/documents/{document_id}
GET    /api/v1/documents/{document_id}/download

POST   /api/v1/validation-jobs
GET    /api/v1/validation-jobs/{job_id}
GET    /api/v1/validation-jobs/{job_id}/report

POST   /api/v1/correction-jobs
GET    /api/v1/correction-jobs/{job_id}
GET    /api/v1/correction-jobs/{job_id}/download

GET    /api/v1/templates
GET    /api/v1/templates/{template_id}
```

### 12.1 接口设计原则

1. 面向任务，而不是面向表。
2. 报告与修正结果可独立查询。
3. job 状态必须清晰：`pending | running | succeeded | failed`。
4. 大文件下载与 JSON 查询分离。

---

## 13. Web MVP 前端蓝图

## 13.1 MVP 只实现 Web 端

前端第一阶段只做一个 Web 应用：

- 上传论文
- 选择模板
- 查看检测进度
- 查看检测报告
- 触发自动修正
- 下载修正后文档

## 13.2 前端工程结构建议

```text
clients/
  apps/
    web/
      src/
        pages/
        features/
        components/
        hooks/
        store/
  packages/
    api-client/
    types/
    ui/
```

## 13.3 前端模块划分

推荐按 feature 组织：

- `document-upload`
- `template-selection`
- `validation-report`
- `correction-download`
- `job-status`

而不是把所有页面组件堆在通用 `components/` 目录下。

## 13.4 为什么现在就预留 `packages/`

因为未来桌面端和 Word 插件都会复用：

- 类型定义
- API 客户端
- 部分 UI 组件
- 报告展示组件

但 MVP 只真正落地：

- `apps/web`
- `packages/types`
- `packages/api-client`

---

## 14. 测试策略

## 14.1 测试重点不在页面，而在规则稳定性

PaperNormAI 的测试重点应按以下优先级排序：

1. **规则单元测试**：每条规则的输入与输出是否稳定。
2. **模板集成测试**：同一模板下规则组合是否符合预期。
3. **文档往返测试**：修正后文档是否真的被正确写回。
4. **API 集成测试**：任务流是否跑通。
5. **前端交互测试**：报告展示与下载链路是否正常。

## 14.2 测试夹具建议

建立标准测试样本库：

```text
backend/tests/fixtures/
  docs/
    valid/
    invalid/
  templates/
  reports/
```

样本库应覆盖：

- 正文字体错误
- 标题字号错误
- 页边距错误
- 行距错误
- 参考文献格式错误
- 混合中英文样式错误

---

## 15. 安全、隐私与运维约束

## 15.1 安全边界

MVP 至少要满足：

1. 仅允许上传受支持文件类型。
2. 限制文件体积。
3. 对下载链接做鉴权或签名控制。
4. 将用户文档与公开模板资产隔离。
5. 避免把原文档内容无控制地发给外部模型。

## 15.2 AI 隐私策略

需要在产品与工程层面先定原则：

1. 哪些内容会发送给大模型。
2. 是否默认脱敏。
3. 是否允许用户选择关闭 AI 增强。
4. 是否承诺不将用户文件用于模型训练。

这些虽然不是最先编码的部分，但必须尽早在架构里预留开关和文案位置。

## 15.3 运维建议

MVP 只需要最小可用运维能力：

- API 服务健康检查
- job 失败日志
- AI 调用失败日志
- 基础性能指标
- 文件存储清理策略

---

## 16. 实施顺序建议

### Phase 0：工程骨架

1. 建立模块化单体目录。
2. 建立 `clients/apps/web` 与 `clients/packages/*` 骨架。
3. 建立 `template-library/`。
4. 建立基础数据库与 job 模型。

### Phase 1：核心引擎闭环

1. `.docx` 解析为中间模型。
2. 模板加载。
3. L1 规则引擎。
4. 统一违规结果与报告输出。
5. 自动修正基础能力。

### Phase 2：产品可用化

1. Web 上传和报告界面。
2. 异步任务状态查询。
3. 下载修正文档。
4. 模板选择与基础推荐。

### Phase 3：AI 增强

1. 参考文献格式检查。
2. 引用一致性检查。
3. 标题层级语义建议。

### Phase 4：扩展端能力

1. 桌面端。
2. Word 插件。
3. 更多模板。
4. 更多文档格式。

---

## 17. 当前明确决策

截至本文档产出时，建议锁定以下决策：

1. **MVP 只做 Web + `.docx`**。
2. **后端采用模块化单体，不做微服务**。
3. **规则引擎为主，AI 为辅**。
4. **模板定义文件入仓库，数据库存索引与状态**。
5. **文档必须先映射为中间模型再进入校验和修正**。
6. **检测与修正采用 job 模型**。
7. **前端按 monorepo/workspace 预埋扩展位，但只实现 web app**。

---

## 18. 后续文档衔接建议

接下来建议基于本蓝图继续产出以下文档：

1. 《规则引擎技术设计》
2. 《模板系统数据规范》
3. 《文档中间模型设计》
4. 《MVP API 契约》
5. 《Web MVP 实现计划》

其中，现有的 `docs/superpowers/plans/2026-04-28-paper-norm-ai.md` 应在后续重构为：

- 以本蓝图为前置约束
- 仅覆盖 MVP 范围
- 将桌面端与 Word 插件移出首发实施阶段
