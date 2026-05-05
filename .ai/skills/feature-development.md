# Skill: feature-development

## 触发条件

当 feature-readiness 评估为 Green 或 Yellow 后，进入功能开发时调用本 skill。

## 输入

```
feature_name: 功能名称
feature_description: 功能描述
readiness_report: feature-readiness 的输出（可选）
```

## 执行步骤

```
Step 1. 读取相关知识文档
  - 100-system-overview.md（确认功能边界）
  - 对应的 200-800 专题文档
  - handoff/BUILD-LOG.md（了解当前状态）

Step 2. 理解现有代码
  - 读取涉及的现有文件
  - 确认接口契约和数据模型

Step 3. 实现代码（按层顺序）
  - Infrastructure 层（数据库/外部 API）
  - Domain 层（核心业务逻辑）
  - Application 层（用例编排）
  - API 层（endpoint）

Step 4. 验证
  - 运行相关测试
  - 确认功能正常

Step 5. 更新文档
  - 更新 handoff/BUILD-LOG.md
  - 更新 docs/progress.md
  - 如有重要决策，更新对应知识文档

Step 6. 写入 910-skill-run-log.md
```

## 输出格式

```markdown
## Feature 开发报告

**功能**：{feature_name}
**实现层**：{Infrastructure/Domain/Application/API}
**涉及文件**：{文件列表}
**验证结果**：{测试通过/验证方式}
**文档更新**：{更新了哪些文档}
```

## 成功标准

- 功能实现并验证通过
- BUILD-LOG.md 已更新
- 写入了 910-skill-run-log.md

## 更新记录

**最近更新**：2026-05-06
**变更**：从说明文档形态改为可执行 skill 形态
