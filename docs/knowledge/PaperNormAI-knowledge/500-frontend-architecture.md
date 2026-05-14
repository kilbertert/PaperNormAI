# PaperNormAI 前端架构知识

## 1. 文档目的

记录 PaperNormAI 前端已落地的技术栈、架构决策与实现事实，替代早期蓝图设计。

## 2. 覆盖范围

- 技术栈（Next.js App Router / TypeScript / 无 react-query）
- 核心模块划分与文件结构
- 状态管理策略（useState + useEffect）
- 认证流程（localStorage access_token）
- 与后端 API 的交互方式

## 3. 核心事实（代码事实态，2026-05-14）

**技术栈：**
- 框架：Next.js 14+（App Router）
- 语言：TypeScript
- 构建工具：Next.js 内置（Turbopack 未启用）
- 样式：内联 style（最小化实现）
- **无 react-query** — 使用 `useState + useEffect` 管理加载态/提交态/错误态

**Token 管理：**
- 存储：`localStorage.setItem('access_token', token)`
- 读取：`localStorage.getItem('access_token')`
- Key：`access_token`（与后端 client.ts 一致）

**API 访问：**
- 环境变量：`NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1`
- 前端直连后端 FastAPI，无代理层
- 认证方式：JWT Bearer Token

## 4. 项目结构

```
clients/apps/web/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx           # 根布局（极简）
│   │   ├── page.tsx             # 首页 → 重定向 /spec
│   │   ├── globals.css
│   │   ├── login/
│   │   │   └── page.tsx        # 极简登录页（email + password）
│   │   └── spec/
│   │       ├── page.tsx        # Step 1: 上传 spec .docx
│   │       └── [sessionId]/
│   │           ├── page.tsx    # Step 2: 上传 thesis .docx
│   │           └── report/
│   │               └── [reportId]/
│   │                   └── page.tsx  # Step 3: 展示报告
│   ├── lib/
│   │   ├── api.ts              # API 调用（fetch + Bearer token）
│   │   ├── auth.ts             # getAccessToken / useRequireAuth
│   │   └── types.ts            # TypeScript 接口定义
│   └── .env.local              # NEXT_PUBLIC_API_BASE_URL
├── public/
├── next.config.ts
├── package.json
└── tsconfig.json
```

**所有页面和可交互组件顶部声明 `'use client'`，组件运行在浏览器环境。**

## 5. 核心页面与路由

### 5.1 路由结构

```
/                   → 重定向 /spec
/login              → 极简登录（email + password → POST /auth/login）
/spec               → Step 1: 上传 spec .docx
/spec/[sessionId]   → Step 2: 上传 thesis .docx
/spec/[sessionId]/report/[reportId] → Step 3: 展示报告统计 + 违规明细
```

### 5.2 页面实现约束

- 所有页面：纯 Client Components（`'use client'`）
- 无 SSR / 无服务端鉴权适配
- 无 react-query / 无 tanstack-query
- 状态管理：`useState + useEffect`
- Token 检查：`getAccessToken()` 在 `useEffect` 中调用

## 6. API 交互

### 6.1 API 端点映射

| 前端函数 | 后端端点 | 说明 |
|----------|----------|------|
| `login(email, password)` | `POST /auth/login` | 返回 access_token |
| `parseSpec(file)` | `POST /spec/parse-spec` | 返回 session_id + rules_count |
| `validateWithSpec(file, sessionId)` | `POST /spec/validate-with-spec` | 返回 report_id + 统计 |
| `getReport(reportId)` | `GET /spec/reports/{report_id}` | 返回完整报告 + violations[] |

### 6.2 API 客户端封装

```typescript
// src/lib/api.ts
'use client'
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1'

function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

export async function login(email: string, password: string): Promise<LoginResponse>
export async function parseSpec(file: File): Promise<SpecParseResponse>
export async function validateWithSpec(file: File, sessionId: string): Promise<SpecValidationResponse>
export async function getReport(reportId: string): Promise<ValidationReportResponse>
export { getToken }
```

### 6.3 错误处理策略

1. **401 错误**：清空 localStorage，跳转 `/login`
2. **网络错误**：显示 "Failed to fetch report" 等错误信息
3. **业务错误**：显示后端返回的错误消息

## 7. 认证流程

```
用户访问 /spec
  → 检查 localStorage.access_token
    → 有 token：正常流程
    → 无 token：跳转 /login

用户提交登录表单
  → POST /auth/login {email, password}
  → 成功：localStorage.setItem('access_token', token) → 跳转 /spec
  → 失败：显示错误信息
```

## 8. 报告展示（Step 3）

`/spec/[sessionId]/report/[reportId]` 页面：

1. 调用 `getReport(reportId)` 获取完整 `ValidationReportResponse`
2. 展示四格统计卡片：`total_count / error_count / warning_count / info_count`
3. 遍历 `violations[]` 展示违规明细：
   - `severity`（error/warning/info）+ `category` 标签
   - `description` 描述
   - `paragraph_index`（如有）
   - `original_content` + `suggested_fix` 对照

## 9. 与后端 API 的交互

- 前端直连 `NEXT_PUBLIC_API_BASE_URL`（后端 FastAPI）
- 无 Next.js API Routes 代理层
- CORS 已配置（FastAPI `CORSMiddleware` 允许 `http://localhost:3000`）

## 10. 当前已知边界

1. 前端当前为最小化实现（极简样式、无组件库、无 Loading skeleton）
2. 无报告导出（PDF/ DOCX）
3. 无修正文档下载（Step 3 仅展示报告）
4. 无注册页、忘记密码等辅助页面
5. 无暗色模式 / 无 i18n

## 11. 与其他文档的关联

- 前置文档：`100-system-overview.md`（系统级概述）
- 相关文档：`400-api-architecture.md`（前端调用后端 API）、`700-capability-map.md`（前端能力映射）、`800-cross-layer-call-chains.md`（完整调用链）

## 12. 待确认问题

1. 是否引入 UI 组件库（Ant Design / Material UI / Radix）
2. 是否增加报告导出功能
3. 是否增加修正文档下载链
4. 是否加入 loading skeleton / error boundary

## 13. 更新记录

**最近复核时间**：2026-05-14
**复核依据**：
- `clients/apps/web/src/app/login/page.tsx`
- `clients/apps/web/src/app/spec/page.tsx`
- `clients/apps/web/src/app/spec/[sessionId]/page.tsx`
- `clients/apps/web/src/app/spec/[sessionId]/report/[reportId]/page.tsx`
- `clients/apps/web/src/lib/api.ts`
- `clients/apps/web/src/lib/auth.ts`
- `clients/apps/web/src/lib/types.ts`
- `clients/apps/web/.env.local`

**当前可信度**：高（代码事实态，已通过端到端验证）

**待确认点**：样式方案、UI 组件库选型、报告导出需求。