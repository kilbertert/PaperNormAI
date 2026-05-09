# PaperNormAI API 架构知识

## 1. 文档目的

记录 API 层已经落地的路由、鉴权和端点行为，替代早期蓝图态描述。

## 2. 覆盖范围

- 路由注册与分组
- 认证与鉴权依赖
- 已实现端点（auth/documents/templates/validations/corrections/spec）
- 异步任务端点的行为边界

## 3. 核心事实（代码事实态）

1. API 已采用 FastAPI，统一挂载在 `api_router`。  
2. 已注册路由前缀：`/auth`、`/documents`、`/templates`、`/validations`、`/corrections`、`/spec`。  
3. 认证采用 JWT Bearer，`get_current_user` 在依赖层完成 token 解析与用户校验。  
4. 校验与修正任务端点采用 `BackgroundTasks` 异步执行模式。

## 4. 路由清单（当前实现）

### 4.1 认证

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### 4.2 文档管理

- `POST /documents/upload`
- `GET /documents/`
- `GET /documents/{document_id}`
- `GET /documents/{document_id}/download`
- `DELETE /documents/{document_id}`

### 4.3 模板管理

- `GET /templates/`
- `GET /templates/{template_id}`
- `POST /templates/`
- `PUT /templates/{template_id}`
- `DELETE /templates/{template_id}`（软删除）

### 4.4 校验任务

- `POST /validations/`
- `GET /validations/{job_id}`

### 4.5 修正任务

- `POST /corrections/`
- `GET /corrections/{job_id}`
- `GET /corrections/{job_id}/download`

### 4.6 Spec 语义校验

- `POST /spec/parse-spec`
- `GET /spec/spec-sessions/{session_id}`
- `POST /spec/validate-with-spec`
- `DELETE /spec/spec-sessions/{session_id}`

## 5. 鉴权与权限边界

1. 需要用户上下文的端点均依赖 `get_current_user`。  
2. 用户访问文档、任务、规则会话时，均做 `user_id` 级别所有权校验。  
3. `get_optional_current_user` 已提供，但主要端点目前仍以强认证为主。

## 6. 当前已知边界

1. API 层部分端点仍承担较多编排逻辑（可继续下沉到 application/use case 层）。  
2. 返回模型以 Pydantic 手工组装为主，尚未统一响应封装中间层。  
3. 实时进度目前依赖轮询（`GET /validations/{job_id}`、`GET /corrections/{job_id}`），未使用 WebSocket。

## 7. 与其他文档的关联

- 前置文档：`100-system-overview.md`  
- 相关文档：`200-database-models.md`、`300-backend-kernel-services.md`、`800-cross-layer-call-chains.md`

## 8. 待确认问题

1. 是否在下一阶段引入统一 API 错误码与响应 Envelope。  
2. 是否把端点内部编排进一步迁移到 application 层。  
3. 是否引入 WebSocket/SSE 以替代高频轮询。

## 9. 更新记录

**最近复核时间**：2026-05-06  
**复核依据**：
- `backend/app/api/routes.py`
- `backend/app/api/dependencies.py`
- `backend/app/api/endpoints/auth.py`
- `backend/app/api/endpoints/documents.py`
- `backend/app/api/endpoints/templates.py`
- `backend/app/api/endpoints/validations.py`
- `backend/app/api/endpoints/corrections.py`
- `backend/app/api/endpoints/spec_validation.py`

**当前可信度**：高  
**待确认点**：API 编排职责下沉与实时推送机制。
