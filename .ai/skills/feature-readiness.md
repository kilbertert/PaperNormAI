# Feature Readiness Skill

> 本 skill 定义如何判断 PaperNormAI 中的功能是否具备开发就绪条件。在开始开发前，使用本 skill 检查功能的前置依赖、技术约束和知识准备。

## 1. 定位

Feature Readiness 是 `PaperNormAI-feature-development` 的辅助 skill。

在接收功能开发任务时，先使用本 skill 评估功能是否就绪，避免在条件不成熟时开始开发。

## 2. 就绪条件检查表

### 2.1 知识准备检查

| 检查项 | 要求 | 状态 |
|--------|------|------|
| 知识文档存在 | 对应的知识文档（200-800 系列）已存在 | ✅/❌ |
| 架构蓝图覆盖 | 功能在 MVP Engineering Blueprint 中有描述 | ✅/❌ |
| 边界已定义 | 功能边界和依赖清晰 | ✅/❌ |

### 2.2 技术准备检查

| 检查项 | 要求 | 状态 |
|--------|------|------|
| 技术选型确认 | 涉及的框架/库已选定 | ✅/❌ |
| API 契约明确 | 涉及的 API endpoint 已定义 | ✅/❌ |
| 数据模型明确 | 涉及的实体/值对象已定义 | ✅/❌ |

### 2.3 代码准备检查

| 检查项 | 要求 | 状态 |
|--------|------|------|
| 目标目录存在 | `backend/`、`clients/` 等目录已建立 | ✅/❌ |
| 模块边界清晰 | 目标模块的 `__init__.py` 已建立 | ✅/❌ |
| 依赖可注入 | 依赖反转接口已定义 | ✅/❌ |

### 2.4 测试准备检查

| 检查项 | 要求 | 状态 |
|--------|------|------|
| 测试框架选定 | pytest / Jest 已配置 | ✅/❌ |
| 测试工具可用 | testing fixtures 已准备 | ✅/❌ |

## 3. 就绪等级

### 3.1 就绪等级定义

| 等级 | 含义 | 行动 |
|------|------|------|
| **Green** | 完全就绪，可以立即开始开发 | 按计划执行 |
| **Yellow** | 部分就绪，有条件限制 | 明确限制后可以开始 |
| **Red** | 未就绪，有阻塞问题 | 解决阻塞问题后再开始 |

### 3.2 Yellow 的常见场景

- 知识文档存在但不完整
- API 契约有初步版本但待确认
- 技术选型已确定但具体实现方案未确定
- 代码骨架已建立但某些模块尚不存在

### 3.3 Red 的常见场景

- 功能在蓝图中没有覆盖
- 涉及的技术选型尚未确定
- 依赖的关键模块尚未建立
- 存在未解决的知识冲突

## 4. 评估流程

```
1. 接收功能描述
2. 逐项检查就绪条件
3. 识别阻塞问题
4. 给出就绪等级
5. 如果 Yellow/Red，提出解决建议
```

## 5. 输出格式

```markdown
## Feature Readiness 报告

**功能名称**：
{功能名称}

**涉及范围**：
- 知识文档：{docs/knowledge/...}
- 目标模块：{backend/app/domain/...}
- 依赖模块：{...}

**就绪检查**：

| 检查项 | 要求 | 当前状态 | 阻塞程度 |
|--------|------|----------|----------|
| 知识文档 | 对应知识文档存在 | ✅ | - |
| 技术选型 | Web 框架已选定 | ✅ | - |
| API 契约 | REST endpoint 已定义 | ❌ | 阻塞 |
| ... | ... | ... | ... |

**就绪等级**：{Green/Yellow/Red}

**如果 Yellow - 限制条件**：
- {限制1}
- {限制2}

**如果 Yellow/Red - 解决建议**：
1. {建议1}
2. {建议2}

**下一步行动**：
- {行动1}
- {行动2}

**需要用户确认**：
- {决策点1}
- {决策点2}
```

## 6. 示例

### 示例输入

```
功能：实现文档上传 API endpoint
```

### 示例输出

```markdown
## Feature Readiness 报告

**功能名称**：
文档上传 API Endpoint

**涉及范围**：
- 知识文档：`400-api-architecture.md`、`200-database-models.md`
- 目标模块：`backend/app/api/endpoints/document.py`
- 依赖模块：`backend/app/application/document_service.py`、`backend/app/infrastructure/storage.py`

**就绪检查**：

| 检查项 | 要求 | 当前状态 | 阻塞程度 |
|--------|------|----------|----------|
| 知识文档 | 400-api-architecture.md 存在 | ✅ | - |
| API 契约 | POST /api/v1/documents/upload 已定义 | ✅ | - |
| 数据模型 | Document 实体已定义 | ✅ | - |
| 技术选型 | 文件存储方式待定 | ❌ | 部分阻塞 |
| 依赖模块 | document_service 尚未建立 | ❌ | 阻塞 |

**就绪等级**：Red

**限制条件**：
- 文件存储方式尚未确定（本地存储 vs 云存储）

**解决建议**：
1. 先建立 `backend/app/application/document_service.py`（空壳即可）
2. 确认文件存储方式：当前可用本地存储，后续迁移云存储
3. 建立 `backend/app/infrastructure/storage.py` 接口定义

**下一步行动**：
1. 建立 application layer 的 document_service 空壳
2. 定义 storage 接口
3. 实现 API endpoint 时注入依赖

**需要用户确认**：
- 初始部署使用本地存储还是云存储？
```

## 7. 使用场景

- 接收功能开发任务时
- 评审功能设计时
- 制定迭代计划时

## 8. 更新记录

**创建时间**：2026-05-01

**依据**：PaperNormAI MVP Engineering Blueprint、Knowledge Base Structure