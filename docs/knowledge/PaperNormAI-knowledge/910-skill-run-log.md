# PaperNormAI Skill 运行日志

## 1. 文档目的

本文件用于记录 `PaperNormAI-feature-development` agent 调用 skill 的执行日志，形成 skill 使用的可追溯记录。

## 2. 覆盖范围

- skill 调用的时间、意图和结果
- skill 输出的关键结论
- 关联的 feature/issue/fix 记录

## 3. 日志格式

每次 skill 调用后，按以下格式追加：

```markdown
## YYYY-MM-DD HH:MM - {skill_name}

**调用者**：`PaperNormAI-feature-development`

**调用场景**：
{为什么调用这个 skill}

**调用参数**：
- 场景：{feature/issue/fix}
- 目标：{具体描述}

**skill 输出摘要**：
- 评估结果：{关键结论}
- 建议行动：{1-2 句}

**关联记录**：
- Feature/Issue/Fix：{关联的名称}
- 相关文档：{知识文档路径}
- 代码变更：{涉及的文件}

**后续行动**：
- {下一步}
```

## 4. 使用规范

1. **立即记录**：skill 调用后立即记录，不等待后续活动。
2. **摘要优先**：不需要记录完整输出，只记录关键结论。
3. **保持简洁**：每条记录不超过 20 行。
4. **真实记录**：记录实际发生的情况，不做假设。

## 5. 初始化说明

本文件于 2026-05-01 创建，用于记录 Phase 4 起的 skill 调用历史。

在知识库骨架建设阶段（Phase 2），knowledge-builder 主要执行文档学习和沉淀，skill 调用记录从 Phase 4 开始。

## 6. 更新记录

**创建时间**：2026-05-01

**依据**：
- `.ai/agents/PaperNormAI-feature-development.agent.md`
- `.ai/skills/issue-evaluator.md`
- `.ai/skills/feature-readiness.md`
- `.ai/skills/feature-development.md`
- `.ai/skills/fix-development.md`