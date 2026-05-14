# Skill: feature-readiness

## 触发条件

在开始任何功能开发前调用本 skill，确认前置条件已满足。

## 输入

```
feature_name: 功能名称
feature_description: 功能描述（一句话）
```

## 执行步骤

```
Step 1. 读取相关知识文档
  - 100-system-overview.md（确认功能在 MVP 范围内）
  - 700-capability-map.md（确认功能状态）
  - 对应的 200-800 专题文档

Step 2. 逐项检查就绪条件
  [ ] 功能在 MVP 范围内（100-system-overview.md 有描述）
  [ ] 对应知识文档存在（200-800 系列）
  [ ] 技术选型已确认（框架/库已选定）
  [ ] 目标模块目录已存在（backend/app/...）
  [ ] 依赖模块已实现或有明确接口

Step 3. 架构影响初筛（新增）
  [ ] 是否涉及跨层依赖变化（api/application/domain/infrastructure 任一层）
  [ ] 是否改变已有依赖方向
  [ ] 是否引入新的外部依赖（第三方库、服务）
  [ ] 是否修改持久化模型或数据库 schema
  [ ] 预计回归面是否超出当前功能范围

  如果以上任何一项为"是"：
    → 标记为 Yellow（需触发 architecture-check）
    → 不自动进入 feature-development

Step 4. 识别阻塞项
  - 标记每个未通过的检查项为 Yellow（有限制）或 Red（阻塞）

Step 5. 给出就绪等级
  - Green: 所有检查通过，架构影响初筛通过
  - Yellow: 有限制但可以开始，或需要 architecture-check 确认
  - Red: 有阻塞，不能开始

Step 6. 输出就绪报告（见输出格式）

Step 7. 如果 Yellow，触发 architecture-check skill

Step 8. 写入 910-skill-run-log.md
```

## 输出格式

```markdown
## Feature Readiness 报告

**功能**：{feature_name}

**就绪检查**：
| 检查项 | 状态 | 阻塞程度 |
|--------|------|----------|
| MVP 范围内 | ✅/❌ | - / 阻塞 |
| 知识文档存在 | ✅/❌ | - / 阻塞 |
| 技术选型确认 | ✅/❌ | - / 阻塞 |
| 目标模块存在 | ✅/❌ | - / 阻塞 |
| 依赖已实现 | ✅/❌ | - / 阻塞 |

**架构影响初筛**（Step 3 结果）：
| 检查项 | 结果 | 说明 |
|--------|------|------|
| 涉及跨层依赖变化 | ✅/❌ | |
| 改变依赖方向 | ✅/❌ | |
| 引入新外部依赖 | ✅/❌ | |
| 修改持久化模型/schema | ✅/❌ | |
| 回归面超出当前范围 | ✅/❌ | |

**就绪等级**：Green / Yellow / Red

**阻塞项**（如有）：
- {阻塞描述} → 解决方案：{建议}

**下一步**：{进入 feature-development / 先解决阻塞 / 触发 architecture-check}
```

## 成功标准

- 输出了就绪报告
- 明确了是否可以开始开发
- 架构影响初筛已执行（如需触发 architecture-check 已触发）
- 写入了 910-skill-run-log.md

## 串联关系（与 architecture-check）

```
feature-readiness
  → 架构影响初筛通过 → 输出 Green → 进入 feature-development
  → 架构影响初筛发现风险 → 输出 Yellow → 触发 architecture-check
    → architecture-check Green → 接受例外，进入 feature-development
    → architecture-check Yellow → 记录例外，有约束进入 feature-development
    → architecture-check Red → 阻塞，不进入 feature-development
  → 发现明确阻塞 → 输出 Red → 不进入 feature-development
```

## 更新记录

**最近更新**：2026-05-14
**变更**：新增 Step 3 架构影响初筛（5项检查）；串联 architecture-check 形成双门禁
