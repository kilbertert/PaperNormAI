# Skill: architecture-check

## 触发条件

在 `feature-readiness` 输出 Yellow/Red，或检测到以下情况时调用本 skill：
- 功能涉及跨层依赖变化
- 功能涉及依赖方向改变
- 功能涉及新的外部依赖引入
- 功能涉及持久化模型变更

## 输入

```
feature_name: 功能名称
feature_description: 功能描述
proposed_architecture: 拟议的实现方案（可选）
```

## 执行步骤

```
Step 1. 读取架构约束文档
  - .github/copilot-instructions.md（Section 3: 分层规则, Section 4: 目录与命名规则）
  - docs/knowledge/PaperNormAI-knowledge/000-doc-map.md（确认知识文档状态）
  - backend/app/domain/services/interfaces.py（如已存在）

Step 2. 检查分层合规性
  [ ] 是否引入新的 domain -> infrastructure 依赖
  [ ] 是否改变 api -> application -> domain -> infrastructure 依赖方向
  [ ] 是否绕过 domain 抽象接口直接使用 infrastructure 实现
  [ ] 是否在 domain 层引入新的跨层 import

Step 3. 检查边界合规性
  [ ] 领域边界是否被尊重（四大领域模块：document/template/validation/correction 不能相互直接依赖）
  [ ] 领域实体是否保持纯净（不直接依赖 infrastructure）
  [ ] Repository 接口是否在 domain 层定义（而非 infrastructure 层）

Step 4. 检查持久化合规性
  [ ] 新增模型是否与现有模型体系兼容
  [ ] 外键关系是否正确
  [ ] 是否需要 migration（SQLite create_all vs PostgreSQL Alembic）

Step 5. 识别架构例外
  - 如果存在已知偏差（如 API 层直接调用 repository 的 MVP 务实选择），标记为"例外"
  - 记录例外原因和后续收敛计划

Step 6. 输出架构合规报告（见输出格式）

Step 7. 写入 910-skill-run-log.md
```

## 输出格式

```markdown
## Architecture Check 报告

**功能**：{feature_name}

**分层合规检查**：
| 检查项 | 状态 | 说明 |
|--------|------|------|
| 无新增 domain→infrastructure 依赖 | ✅/❌ | |
| 依赖方向正确 | ✅/❌ | |
| 未绕过 domain 抽象接口 | ✅/❌ | |
| domain 层无跨层 import | ✅/❌ | |

**边界合规检查**：
| 检查项 | 状态 | 说明 |
|--------|------|------|
| 领域边界未破坏 | ✅/❌ | |
| 领域实体保持纯净 | ✅/❌ | |
| Repository 接口在 domain 层 | ✅/❌ | |

**持久化合规检查**：
| 检查项 | 状态 | 说明 |
|--------|------|------|
| 新增模型兼容现有体系 | ✅/❌ | |
| 外键关系正确 | ✅/❌ | |
| Migration 路径明确 | ✅/❌ | |

**架构合规等级**：Green / Yellow / Red

**例外记录**（如有）：
- {例外描述} → 原因：{原因} → 收敛计划：{计划}

**阻塞项**（如有）：
- {阻塞描述} → 解决方案：{建议}

**下一步**：{进入 feature-development / 先解决阻塞 / 接受例外继续}
```

## 成功标准

- 输出了架构合规报告
- 明确了是否存在架构违规或已知例外
- 写入了 910-skill-run-log.md

## 与 feature-readiness 的串联关系

```
feature-readiness → (输出 Yellow)
  → architecture-check（强制）
  → 如果 Green：可以继续
  → 如果 Yellow：记录例外，可以继续（有约束）
  → 如果 Red：阻塞，不能继续
```

## 更新记录

**创建时间**：2026-05-14
**用途**：治理硬门禁 — 防止架构腐化在功能开发中复发