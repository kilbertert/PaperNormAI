# Skill: issue-evaluator

## 触发条件

当遇到以下情况时调用本 skill：
- 收到 bug 报告或技术问题
- 评估新功能需求的技术复杂度
- 决定是否进入 feature-development 或 fix-development

## 输入

```
issue_description: 问题或需求的一句话描述
context: 涉及的模块/文件（可选）
```

## 执行步骤

```
Step 1. 识别涉及范围
  - 列出涉及的模块、文件、层（Infrastructure/Domain/Application/API）

Step 2. 评估复杂度
  - Low: 单函数/单文件修改
  - Medium: 模块内多文件
  - High: 跨层/跨模块
  - Very High: 架构级变更

Step 3. 评估风险
  - Low: 不影响核心流程
  - Medium: 影响非核心功能
  - High: 影响核心功能（解析/校验/修正）
  - Critical: 数据丢失/安全/系统崩溃

Step 4. 给出优先级
  - P0: Critical 风险
  - P1: High 风险 + High 复杂度
  - P2: Medium 风险 + Medium 复杂度
  - P3: Low 风险或 Low 复杂度

Step 5. 列出不确定点
  - 需要用户确认的决策点

Step 6. 输出评估报告（见输出格式）

Step 7. 写入 910-skill-run-log.md
```

## 输出格式

```markdown
## Issue 评估报告

**问题摘要**：{一句话}

**涉及范围**：
- 模块：{模块名}
- 文件：{文件路径}
- 层：{层名}

**复杂度**：{Low/Medium/High/Very High} — {理由}
**风险**：{Low/Medium/High/Critical} — {理由}
**优先级**：{P0/P1/P2/P3} — {理由}
**不确定性**：{Low/Medium/High}

**待确认**：
- {决策点}

**建议**：进入 {feature-development / fix-development}
```

## 成功标准

- 输出了完整的评估报告
- 明确了优先级和下一步行动
- 写入了 910-skill-run-log.md

## 更新记录

**最近更新**：2026-05-06
**变更**：从说明文档形态改为可执行 skill 形态
