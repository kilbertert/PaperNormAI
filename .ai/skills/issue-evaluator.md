# Issue Evaluator Skill

> 本 skill 定义如何评估 PaperNormAI 项目中的问题（Issue）的复杂度、风险和优先级。为后续的 feature-development 或 fix-development 提供决策依据。

## 1. 定位

Issue Evaluator 是 `PaperNormAI-feature-development` 的辅助 skill。

当遇到需要评估的技术问题、功能需求或缺陷报告时，使用本 skill 进行系统化评估。

## 2. 评估维度

### 2.1 复杂度（Complexity）

评估问题的实现复杂度：

| 等级 | 描述 | 典型特征 |
|------|------|----------|
| Low | 单函数/单文件修改 | 逻辑清晰、无依赖 |
| Medium | 涉及模块内多个文件 | 需要理解模块边界 |
| High | 跨多层/跨模块 | 涉及 API 契约变更、多层调用 |
| Very High | 架构级变更 | 涉及模块边界重组、技术栈迁移 |

### 2.2 风险（Risk）

评估问题的影响范围和潜在危害：

| 等级 | 描述 | 典型特征 |
|------|------|----------|
| Low | 不影响核心流程 | UI 样式、文案修改 |
| Medium | 影响非核心功能 | 非关键路径的边界情况 |
| High | 影响核心功能 | 规则引擎、文档解析核心逻辑 |
| Critical | 影响系统可用性 | 数据丢失、安全漏洞、系统崩溃 |

### 2.3 优先级（Priority）

综合复杂度和风险，给出优先级建议：

| 优先级 | 描述 | 适用场景 |
|--------|------|----------|
| P0 | 立即处理 | Critical + High complexity |
| P1 | 尽快处理 | Critical + Medium complexity 或 High + High complexity |
| P2 | 计划处理 | Medium + Medium complexity |
| P3 | 后续处理 | Low complexity 或 Low risk |

### 2.4 不确定性（Uncertainty）

评估问题中尚未明确的点：

| 等级 | 描述 |
|------|------|
| Low | 需求明确、有参考实现 |
| Medium | 部分不明确、需要沟通 |
| High | 需求模糊、方案未知 |

## 3. 评估流程

```
1. 接收问题描述
2. 识别涉及的范围（代码、模块、层）
3. 评估各维度（复杂度、风险、优先级、不确定性）
4. 列出需要确认的问题
5. 给出处理建议
```

## 4. 输出格式

```markdown
## Issue 评估报告

**问题摘要**：
{一句话描述问题}

**涉及范围**：
- 模块：
- 代码文件：
- 层：

**复杂度评估**：{Low/Medium/High/Very High}
- 理由：{具体分析}
- 影响文件数：{预估}

**风险评估**：{Low/Medium/High/Critical}
- 理由：{具体分析}
- 影响用户：{预估范围}

**优先级建议**：{P0/P1/P2/P3}
- 理由：{综合评估}

**不确定性**：{Low/Medium/High}
- 待确认问题：
  1. {问题1}
  2. {问题2}

**处理建议**：
- {建议1}
- {建议2}

**需要用户确认**：
- {决策点1}
- {决策点2}
```

## 5. 示例

### 示例输入

```
Issue: 规则引擎在检测到 L3 规则违规时，没有正确调用 AI 增强服务
```

### 示例输出

```markdown
## Issue 评估报告

**问题摘要**：
L3 规则违规时 AI 增强服务未被调用

**涉及范围**：
- 模块：`RuleEngine`、`AIEnhancementService`
- 代码文件：`rule_engine.py`、`ai_service.py`
- 层：Domain Layer、Infrastructure Layer

**复杂度评估**：High
- 理由：涉及 L1/L2/L3 分层判断逻辑与 AI 服务调用的协调
- 影响文件数：2-4

**风险评估**：High
- 理由：影响 AI 增强功能的正确性，可能导致漏判
- 影响用户：所有使用 L3 规则的用户

**优先级建议**：P1
- 理由：Critical 功能（AI 增强）的阻断性问题

**不确定性**：Medium
- 待确认问题：
  1. AI 服务调用的超时设置是否合理
  2. AI 服务不可用时的降级策略是什么

**处理建议**：
1. 先写单元测试复现问题
2. 检查 RuleEngine 中 L3 规则的调用路径
3. 确认 AIEnhancementService 的依赖注入配置

**需要用户确认**：
- AI 服务不可用时的降级策略（跳过 AI 判断还是报错）？
```

## 6. 使用场景

- 评估新 issue 或 bug report 时
- 评估功能需求的技术复杂度时
- 评估技术债务的优先级时

## 7. 更新记录

**创建时间**：2026-05-01

**依据**：PaperNormAI MVP Engineering Blueprint、RuleEngine L1/L2/L3 设计