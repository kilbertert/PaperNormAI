# PaperNormAI API 架构知识

## 1. 文档目的

本文件用于记录 PaperNormAI API 层的设计约束与实现目标，回答以下问题：

1. API 层承担哪些职责，边界在哪里。
2. 核心 API 端点有哪些，签名设计如何。
3. 认证/授权策略如何设计。
4. 当前 API 设计是蓝图目标还是已实现事实。

## 2. 覆盖范围

- API 层职责边界
- 核心 API 端点设计
- 认证与授权策略
- 请求/响应格式设计
- 错误处理规范

## 3. 核心事实

截至当前版本，PaperNormAI API 层仍处于蓝图设计阶段，尚未在代码中系统落地。

当前可确认的 API 设计方向：

- 前后端通过 RESTful API 通信
- 文件上传采用 multipart/form-data
- 文档校验采用异步 job 模型
- 认证采用 JWT Token 方式

## 4. API 层职责边界

### 4.1 API 层在架构中的位置

```
Client (React Frontend)
      │
      │  HTTP/REST
      ▼
API Layer (FastAPI/Flask)
      │
      │  Use Case 调用
      ▼
Application Layer (Use Cases)
      │
      │  领域服务调用
      ▼
Domain Layer / Infrastructure Layer
```

### 4.2 API 层职责

1. **接收并验证请求**：解析请求参数、验证必填字段、处理文件上传
2. **调用应用服务**：将请求路由到对应的 Use Case
3. **格式化响应**：将业务结果格式化为统一 API 响应格式
4. **认证/授权**：验证用户身份、检查权限
5. **日志记录**：记录请求流水，用于审计

### 4.3 API 层不承担的职责

1. 业务逻辑（属于 Application Layer）
2. 数据校验规则（属于 Domain Layer，但 API 层做格式校验）
3. 文档解析处理（属于 Infrastructure Layer）
4. 规则引擎执行（属于 Domain Service）

## 5. 核心 API 端点设计

### 5.1 认证相关

#### POST /api/v1/auth/register

注册新用户。

Request：
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "nickname": "张三"
}
```

Response（201）：
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "张三",
  "created_at": "2026-04-28T10:00:00Z"
}
```

#### POST /api/v1/auth/login

用户登录。

Request：
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

Response（200）：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

### 5.2 文档管理

#### POST /api/v1/documents/upload

上传文档。

Request：multipart/form-data

- `file`：.docx 文件（二进制）
- `template_id`：模板 ID（可选）

Response（201）：
```json
{
  "id": "uuid",
  "original_filename": "论文.docx",
  "file_hash": "sha256_hash",
  "status": "pending",
  "template_id": "uuid",
  "uploaded_at": "2026-04-28T10:00:00Z"
}
```

#### GET /api/v1/documents/{document_id}

获取文档详情。

Response（200）：
```json
{
  "id": "uuid",
  "original_filename": "论文.docx",
  "status": "completed",
  "template_id": "uuid",
  "uploaded_at": "2026-04-28T10:00:00Z",
  "validation_job_id": "uuid"
}
```

#### GET /api/v1/documents

获取当前用户的文档列表。

Query Parameters：

- `page`：页码（默认 1）
- `page_size`：每页数量（默认 20）
- `status`：状态过滤（可选）

Response（200）：
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

#### GET /api/v1/documents/{document_id}/download

下载修正后的文档。

Response（200）：文件流（application/vnd.openxmlformats-officedocument.wordprocessingml.document）

### 5.3 模板相关

#### GET /api/v1/templates

获取可用模板列表。

Response（200）：
```json
{
  "items": [
    {
      "id": "uuid",
      "university": "清华大学",
      "degree_type": "硕士",
      "discipline": "计算机科学",
      "version": "1.0",
      "is_active": true
    }
  ]
}
```

#### GET /api/v1/templates/{template_id}

获取模板详情（包含规则集）。

Response（200）：
```json
{
  "id": "uuid",
  "university": "清华大学",
  "degree_type": "硕士",
  "discipline": "计算机科学",
  "version": "1.0",
  "rules": [
    {
      "id": "font_name",
      "level": "L1",
      "description": "正文字体应为宋体",
      "auto_fixable": true
    }
  ]
}
```

### 5.4 校验任务

#### POST /api/v1/validations

创建校验任务。

Request：
```json
{
  "document_id": "uuid",
  "template_id": "uuid"
}
```

Response（202）：
```json
{
  "job_id": "uuid",
  "status": "pending",
  "created_at": "2026-04-28T10:00:00Z"
}
```

#### GET /api/v1/validations/{job_id}

获取校验任务状态和结果。

Response（200）：
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "template_id": "uuid",
  "status": "completed",
  "started_at": "2026-04-28T10:00:01Z",
  "completed_at": "2026-04-28T10:00:05Z",
  "results": [
    {
      "id": "uuid",
      "rule_id": "font_name",
      "severity": "error",
      "element_path": "paragraph[3]",
      "expected_value": "宋体",
      "actual_value": "Times New Roman",
      "auto_fixable": true,
      "ai_enhanced": false
    }
  ],
  "summary": {
    "total": 10,
    "errors": 3,
    "warnings": 5,
    "infos": 2,
    "auto_fixable": 6
  }
}
```

### 5.5 修正任务

#### POST /api/v1/corrections

创建修正任务。

Request：
```json
{
  "document_id": "uuid",
  "plan_ids": ["uuid1", "uuid2"]
}
```

Response（202）：
```json
{
  "job_id": "uuid",
  "status": "pending",
  "created_at": "2026-04-28T10:00:00Z"
}
```

#### GET /api/v1/corrections/{job_id}

获取修正任务状态。

Response（200）：
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "status": "completed",
  "output_path": "/documents/uuid/corrected.docx",
  "started_at": "2026-04-28T10:00:01Z",
  "completed_at": "2026-04-28T10:00:08Z"
}
```

### 5.6 用户

#### GET /api/v1/users/me

获取当前用户信息。

Response（200）：
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "张三",
  "role": "student",
  "created_at": "2026-04-28T10:00:00Z"
}
```

## 6. 认证与授权策略

### 6.1 认证方式

- 采用 JWT Token
- Access Token 有效期 24 小时
- Token 放在 Authorization Header：`Bearer <token>`

### 6.2 授权策略

- 用户只能访问自己的文档
- Admin 角色可以访问所有文档（用于管理后台）
- 模板读取对所有认证用户开放
- 校验任务创建需要认证

### 6.3 权限矩阵

| 操作 | 游客 | 学生 | 管理员 |
|------|------|------|--------|
| 注册/登录 | ✅ | ✅ | ✅ |
| 查看模板列表 | ❌ | ✅ | ✅ |
| 上传文档 | ❌ | ✅ | ✅ |
| 查看自己的文档 | ❌ | ✅ | ✅ |
| 创建校验任务 | ❌ | ✅ | ✅ |
| 创建修正任务 | ❌ | ✅ | ✅ |
| 下载自己的文档 | ❌ | ✅ | ✅ |
| 管理所有用户文档 | ❌ | ❌ | ✅ |

## 7. 错误处理规范

### 7.1 错误响应格式

```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "文档不存在或无权访问",
    "details": {}
  }
}
```

### 7.2 HTTP 状态码使用规范

- `200`：成功
- `201`：创建成功
- `202`：异步任务已接受
- `400`：请求参数错误
- `401`：未认证
- `403`：无权限
- `404`：资源不存在
- `409`：资源冲突（如文档已在处理中）
- `422`：业务逻辑错误（如无法应用修正）
- `500`：服务器内部错误

### 7.3 常见错误码

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| VALIDATION_ERROR | 400 | 请求参数校验失败 |
| UNAUTHORIZED | 401 | 未登录或 Token 过期 |
| FORBIDDEN | 403 | 无权限访问 |
| DOCUMENT_NOT_FOUND | 404 | 文档不存在 |
| TEMPLATE_NOT_FOUND | 404 | 模板不存在 |
| JOB_NOT_FOUND | 404 | 任务不存在 |
| DOCUMENT_PROCESSING | 409 | 文档正在处理中 |
| FILE_TYPE_NOT_SUPPORTED | 422 | 不支持的文件类型 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

## 8. 请求/响应格式设计

### 8.1 分页响应格式

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 8.2 时间格式

- 所有时间使用 ISO 8601 格式：`2026-04-28T10:00:00Z`
- UTC 时间

### 8.3 文件上传

- 最大文件大小：50MB
- 支持格式：`.docx`
- 文件上传使用 multipart/form-data

## 9. 当前已知边界

1. API 层当前处于蓝图设计阶段，尚未在代码中系统落地。
2. 具体使用哪个 Python Web 框架（FastAPI / Flask）尚未确定。
3. 数据库迁移和模型尚未确认。
4. 是否需要 WebSocket 用于实时进度推送尚未确定。

## 10. 与其他文档的关联

- 前置文档：
  - `100-system-overview.md`（系统级概述）
  - `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- 相关文档：
  - `200-database-models.md`（数据库模型影响 API 响应设计）
  - `300-backend-kernel-services.md`（API 层调用后端服务）
  - `500-frontend-architecture.md`（前端调用 API 的方式）

## 11. 待确认问题

1. 是否需要 WebSocket 支持实时进度推送。
2. API 版本策略（v1 之后的演进方式）。
3. 是否需要 OpenAPI 文档生成（Swagger UI）。
4. 文件上传的断点续传需求。

## 12. 更新记录

**最近复核时间**：2026-04-28

**复核依据**：
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`（API 设计部分）
- `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`

**当前可信度**：中（蓝图设计阶段，尚未代码验证）

**待确认点**：WebSocket 需求、API 版本策略需要在实现阶段确认。