# PaperNormAI 后端核心服务知识

## 1. 文档目的

本文件用于记录 PaperNormAI 后端核心服务的职责、边界与设计约束，回答以下问题：

1. 后端有哪些核心服务，各自的职责边界在哪里。
2. 规则引擎的分层设计（L1/L2/L3）。
3. 模板系统与规则引擎如何协作。
4. 文档处理中间层如何设计。

## 2. 覆盖范围

- 规则引擎服务
- 模板加载服务
- 文档解析服务
- AI 增强服务
- 修正执行服务
- 任务调度服务

## 3. 核心事实

截至当前版本，后端核心服务仍处于蓝图设计阶段，尚未在代码中系统落地。

当前可确认的核心服务设计方向：

- 规则引擎是第一核心，采用 L1/L2/L3 分层设计
- 模板系统是第一核心资产，为规则引擎提供参数化规则集
- 中间文档模型是业务基础，让核心服务摆脱 python-docx 直接耦合

## 4. 核心服务详解

### 4.1 规则引擎服务（RuleEngine）

定位：**第一核心**。

职责：

- 加载模板对应的规则集
- 对中间文档模型执行规则检查
- 输出结构化的 ValidationResult 列表
- 触发 AI 增强层处理高歧义规则

#### L1 规则：确定性规则（Structural）

- 字体名称
- 字号大小
- 行距（单倍/1.5倍/2倍）
- 段前段后间距
- 页边距

特征：

- 结果确定，无歧义
- 可自动修正
- 不需要 AI 参与

#### L2 规则：模式化规则（Pattern-Based）

- 标题层级是否连续（1 -> 2 -> 3，不能跳级）
- 引用格式是否符合模板定义
- 目录生成是否正确

特征：

- 有一定模式，但存在边界情况
- 大部分可自动修正
- 部分场景需要 AI 辅助判断

#### L3 规则：语义化规则（AI-Enhanced）

- 参考文献格式是否规范（高歧义）
- 引用内容一致性判断
- 专业术语使用规范

特征：

- 高歧义，必须 AI 参与
- 通常不可完全自动修正
- 输出置信度，提示用户人工确认

#### L1/L2/L3 分层设计原因

1. **确定性优先**：L1 规则覆盖大部分常见问题，用确定性算法解决
2. **模式辅助**：L2 规则处理有规律的边界情况，降低 AI 调用频率
3. **AI 收尾**：L3 规则只对高歧义场景调用 AI，减少不必要的 API 成本

### 4.2 模板加载服务（TemplateLoader）

定位：**第一核心资产**。

职责：

- 管理高校模板的加载与缓存
- 将模板规则集解析为引擎可用的格式
- 维护模板版本，支持历史校验追溯

设计约束：

- 模板规则集应与业务代码解耦（文件存储或数据库）
- 模板版本必须进入校验报告
- 模板加载应有缓存机制，避免重复解析

### 4.3 文档解析服务（DocumentParser）

定位：**业务基础层**。

职责：

- 将 `.docx` 文件解析为中间文档模型（ParsedDocument）
- 提取文档元素（段落、标题、表格、图表、页脚等）
- 为规则引擎提供统一的文档访问接口

中间文档模型设计约束：

- 必须与 python-docx 原始对象解耦
- 必须包含元素路径（用于定位违规位置）
- 必须支持序列化（用于调试和审计）

ParsedDocument 核心结构：

```python
class ParsedDocument:
    metadata: DocumentMetadata  # 文档元数据
    elements: List[DocumentElement]  # 文档元素列表
    styles: Dict[str, StyleDefinition]  # 样式定义

class DocumentElement:
    path: ElementPath  # 元素路径（用于定位）
    type: ElementType  # 段落/标题/表格等
    content: str  # 文本内容
    style: str  # 关联样式名
    properties: Dict  # 格式属性（字号/行距等）
```

### 4.4 AI 增强服务（AIEnhancementService）

定位：**辅助增强层**。

职责：

- 接收规则引擎的 L3 规则调用
- 调用 AI 模型进行语义判断
- 返回带置信度的增强结果

设计约束：

- AI 服务不直接写文档，只返回判断结果
- AI 结果必须记录置信度
- AI 调用应有重试机制和超时控制

### 4.5 修正执行服务（CorrectionExecutor）

定位：**修正链路执行器**。

职责：

- 接收 CorrectionPlan 列表
- 将修正操作应用到中间文档模型
- 生成修正后的 `.docx` 文件

设计约束：

- 修正操作必须基于结构化违规结果
- 每个修正操作必须记录原始值（用于回滚）
- 修正结果必须可验证（重新校验）

### 4.6 任务调度服务（JobScheduler）

定位：**异步任务编排**。

职责：

- 管理 ValidationJob 和 CorrectionJob 的调度
- 维护 job 状态机转换
- 提供 job 重试机制

设计约束：

- 采用异步 job 模型，不阻塞 HTTP 请求
- job 状态必须有完整的审计记录
- 并发控制：一本文档同一时刻只有一个 running 状态的 job

## 5. 服务边界与依赖关系

```text
┌─────────────────────────────────────────────────┐
│                 API Layer                        │
│         (FastAPI / Flask endpoints)             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              Application Layer                   │
│    (Use Cases: ValidateDocument, CorrectDocument)│
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼───┐  ┌────▼────┐  ┌────▼────┐
│ RuleEngine│  │Template │  │Document │
│  Service  │  │ Loader  │  │ Parser  │
└───────┬───┘  └────┬────┘  └────┬────┘
        │            │            │
        │     ┌──────▼──────┐     │
        │     │ Intermediate │     │
        │     │Document Model│     │
        │     └──────┬──────┘     │
        │            │            │
        │     ┌──────▼──────┐     │
        │     │    AI       │     │
        │     │Enhancement  │     │
        │     └──────┬──────┘     │
        │            │            │
        │     ┌──────▼──────┐     │
        │     │Correction   │     │
        │     │ Executor    │     │
        │     └─────────────┘     │
        │                         │
        └─────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│           Infrastructure Layer                   │
│   (Storage, Persistence, External AI APIs)     │
└─────────────────────────────────────────────────┘
```

依赖约束：

- RuleEngine 依赖 TemplateLoader（获取规则集）
- RuleEngine 依赖 DocumentParser（获取中间文档）
- AIEnhancementService 是独立服务，被 RuleEngine 调用
- CorrectionExecutor 依赖 RuleEngine 的输出
- JobScheduler 编排所有服务的执行

## 6. 关键设计决策

### 6.1 为什么中间文档模型是必须的

1. **解耦**：规则引擎和修正引擎不直接依赖 python-docx
2. **可测试**：中间模型是纯数据结构，可以独立单元测试
3. **可追踪**：违规结果可以精确指向中间模型的路径
4. **可扩展**：未来支持 PDF/LaTeX 时，只需要改 Parser

### 6.2 为什么规则引擎采用 L1/L2/L3 分层

1. **成本优化**：L3 AI 调用成本高，尽量用 L1/L2 解决
2. **确定性优先**：论文格式问题大部分是确定性的
3. **渐进增强**：AI 作为增强层，不是替代层

### 6.3 为什么修正操作基于违规结果而不是直接修改

1. **可审计**：每条修正都有对应的违规记录
2. **可回滚**：修正前记录原始值，支持选择性回滚
3. **可验证**：修正后再跑规则引擎验证结果

## 7. 当前已知边界

1. 后端服务当前处于蓝图设计阶段，尚未在代码中系统落地。
2. 具体使用哪个 Python Web 框架（FastAPI / Flask）尚未确定。
3. AI 服务接入方式（OpenAI API / 本地模型）尚未确定。
4. job 队列的实现方式（Redis + RQ？Celery？数据库轮询？）尚未确定。

## 8. 与其他文档的关联

- 前置文档：
  - `100-system-overview.md`（系统级概述）
  - `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- 相关文档：
  - `200-database-models.md`（数据模型是服务层的基础）
  - `400-api-architecture.md`（API 层调用应用服务）
  - `600-domain-models.md`（领域模型与服务边界的关系）
  - `800-cross-layer-call-chains.md`（跨层调用链的设计）

## 9. 待确认问题

1. Python Web 框架的选型（FastAPI vs Flask）。
2. AI 服务接入方式（OpenAI API vs 本地模型）。
3. job 队列的选型（Redis + RQ vs Celery vs 数据库轮询）。
4. 中间文档模型的具体 Python 类型定义（Pydantic vs dataclass）。
5. 规则引擎的规则定义格式（JSON？YAML？代码内定义？）

## 10. 更新记录

**最近复核时间**：2026-04-28

**复核依据**：
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`（核心服务设计部分）
- `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`

**当前可信度**：中（蓝图设计阶段，尚未代码验证）

**待确认点**：Web 框架、AI 服务接入、job 队列选型需要在实现阶段确认。