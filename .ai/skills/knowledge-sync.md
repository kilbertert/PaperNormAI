# Skill: knowledge-sync

## 触发条件

在以下时机调用本 skill：
- Arch 在 BUILD-LOG.md 中将某个 Step 标记为 COMPLETE 后
- Richard 在 REVIEW-FEEDBACK.md 中确认通过后

**这是知识库自动更新的核心机制。**

## 输入

```
step_name: 刚完成的步骤名称（来自 BUILD-LOG.md）
files_changed: 本步骤修改的文件列表
decisions_made: 本步骤做出的关键决策
```

## 执行步骤

```
Step 1. 读取 handoff/BUILD-LOG.md 最新完成的 Step
  - 获取 files_changed 列表
  - 获取 decisions_made 列表

Step 2. 映射到知识文档（见文件映射速查表）

Step 3. 更新对应知识文档
  - 将"蓝图已定义，未落代码"改为"✅ 已实现"
  - 添加实际实现的类名、方法名、文件路径
  - 更新"最近复核时间"

Step 4. 更新 docs/progress.md
  - 反映最新完成状态
  - 更新"下一步"

Step 5. 写入 docs/memory/YYYY-MM-DD.md
  - 追加今日工作存档（如当日已有文件则追加，否则新建）

Step 6. 写入 docs/knowledge/PaperNormAI-knowledge/900-learning-log.md
  - 追加增量学习记录

Step 7. 写入 docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md
  - 追加 skill 运行记录

Step 8. 执行 Step COMPLETE 四件套对账
  - [ ] docs/progress.md 已更新
  - [ ] docs/knowledge/PaperNormAI-knowledge/900-learning-log.md 已追加
  - [ ] docs/knowledge/PaperNormAI-knowledge/910-skill-run-log.md 已追加
  - [ ] docs/memory/YYYY-MM-DD.md 已追加
  - 若任一未完成：本次 Step 不得进入下一 Step
```

## 输出格式

```markdown
## Knowledge Sync 报告

**触发步骤**：{step_name}
**更新文档**：
- {知识文档路径} — {更新内容摘要}

**新增事实**：
- {事实1}
- {事实2}

**日志已写入**：900-learning-log.md, 910-skill-run-log.md
```

## 成功标准

- 对应知识文档已从"蓝图态"更新为"代码事实态"
- 900-learning-log.md 有新记录
- 910-skill-run-log.md 有新记录
- 四件套对账全部通过

## 文件映射速查表

| 代码路径 | 对应知识文档 |
|----------|-------------|
| `backend/app/infrastructure/docling/` | `300-backend-kernel-services.md` |
| `backend/app/infrastructure/persistence/` | `200-database-models.md` |
| `backend/app/infrastructure/ai/` | `300-backend-kernel-services.md` |
| `backend/app/infrastructure/docx/` | `300-backend-kernel-services.md` |
| `backend/app/domain/services/` | `300-backend-kernel-services.md` |
| `backend/app/domain/entities/` | `600-domain-models.md` |
| `backend/app/api/endpoints/` | `400-api-architecture.md` |
| `backend/app/core/` | `200-database-models.md` |
| `clients/apps/web/` | `500-frontend-architecture.md` |

## 更新记录

**创建时间**：2026-05-06
**用途**：三人协作框架与外部工程系统的知识同步桥梁
