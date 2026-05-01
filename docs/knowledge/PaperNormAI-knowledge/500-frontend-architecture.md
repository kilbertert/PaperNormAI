# PaperNormAI 前端架构知识

## 1. 文档目的

本文件用于记录 PaperNormAI 前端的技术选型、架构设计约束与实现目标，回答以下问题：

1. 前端的技术栈选择与原因。
2. 前端的核心模块划分与职责。
3. 前端如何与后端 API 交互。
4. 当前前端架构是蓝图目标还是已实现事实。

## 2. 覆盖范围

- 技术栈选型
- 核心模块划分
- 状态管理策略
- 组件设计规范
- 与后端 API 的交互方式

## 3. 核心事实

截至当前版本，PaperNormAI 前端仍处于蓝图设计阶段，尚未在代码中系统落地。

当前可确认的前端设计方向：

- 技术栈：React + TypeScript
- 状态管理：React Query（用于服务器状态）+ React Context（用于 UI 状态）
- 样式方案：待定（CSS Modules / Tailwind / styled-components）
- 构建工具：Vite

## 4. 技术栈选型

### 4.1 框架选择：React

选择原因：

1. **生态成熟**：组件库、工具链、社区资源丰富
2. **团队熟悉度**：假定团队对 React 有经验
3. **类型支持**：React + TypeScript 是当前主流选择

### 4.2 语言选择：TypeScript

选择原因：

1. **类型安全**：减少运行时错误，提升代码质量
2. **IDE 支持**：智能提示、跳转、重构更方便
3. **协作效率**：接口即文档，降低协作成本

### 4.3 状态管理

服务器状态（API 数据）：

- **React Query**（或 TanStack Query）
- 理由：自动缓存、后台更新、加载状态管理

UI 状态（本地状态）：

- **React Context**
- 理由：简单场景不需要 Redux，减少复杂度

### 4.4 样式方案（待确认）

当前未确定，可能的选择：

| 方案 | 优点 | 缺点 |
|------|------|------|
| CSS Modules | 原生支持、无运行时开销 | 类名哈希、复用性差 |
| Tailwind CSS | 快速开发、一致性 | 学习成本、类名长 |
| styled-components | 组件化、主题支持 | 运行时开销 |

## 5. 核心模块划分

### 5.1 目录结构（蓝图目标）

```text
clients/apps/web/
├── src/
│   ├── components/       # 可复用 UI 组件
│   │   ├── common/      # 通用组件（Button, Input, Modal 等）
│   │   ├── document/    # 文档相关组件
│   │   ├── template/    # 模板相关组件
│   │   └── report/      # 报告相关组件
│   ├── pages/           # 页面组件
│   │   ├── HomePage.tsx
│   │   ├── DocumentUploadPage.tsx
│   │   ├── ValidationReportPage.tsx
│   │   └── SettingsPage.tsx
│   ├── hooks/           # 自定义 Hooks
│   │   ├── useDocuments.ts
│   │   ├── useValidation.ts
│   │   └── useCorrection.ts
│   ├── services/        # API 调用封装
│   │   ├── documentService.ts
│   │   ├── templateService.ts
│   │   └── authService.ts
│   ├── stores/          # 全局状态（Context）
│   ├── utils/           # 工具函数
│   ├── types/           # TypeScript 类型定义
│   └── App.tsx
├── public/
└── package.json
```

### 5.2 模块职责

#### components/common/

通用 UI 组件库，与业务无关。

包含：Button, Input, Select, Modal, Card, Table, Pagination, Loading, ErrorMessage 等。

原则：

- 纯净样式，不包含业务逻辑
- 可复用，不绑定特定数据

#### components/document/

文档相关业务组件。

包含：

- `DocumentUploader`：文件上传组件
- `DocumentList`：文档列表展示
- `DocumentCard`：文档卡片展示

#### components/template/

模板相关业务组件。

包含：

- `TemplateSelector`：模板选择器
- `TemplateCard`：模板卡片展示

#### components/report/

校验报告相关组件。

包含：

- `ValidationSummary`：校验摘要展示
- `ValidationResultList`：校验结果列表
- `CorrectionPanel`：修正操作面板

#### pages/

页面级组件，组合 components。

每个页面对应一个路由。

#### hooks/

自定义 Hooks，封装逻辑复用。

命名规范：`use<Resource><Action>`，如 `useDocuments`, `useValidationCreate`。

#### services/

API 调用封装，统一管理后端交互。

每个服务对应一个资源：

- `authService`：认证相关
- `documentService`：文档相关
- `templateService`：模板相关
- `validationService`：校验相关
- `correctionService`：修正相关

## 6. 核心页面与路由设计

### 6.1 路由结构

```text
/                    -> HomePage（首页）
/documents           -> DocumentListPage（文档列表）
/documents/upload    -> DocumentUploadPage（文档上传）
/documents/:id       -> DocumentDetailPage（文档详情，包含校验报告）
/templates           -> TemplateListPage（模板列表）
/settings            -> SettingsPage（设置）
/login               -> LoginPage（登录）
/register            -> RegisterPage（注册）
```

### 6.2 核心页面说明

#### HomePage

- 展示产品简介
- 快捷上传入口
- 用户状态（登录/未登录）

#### DocumentUploadPage

- 文件上传（拖拽 + 点击）
- 模板选择
- 上传进度展示

#### DocumentDetailPage

- 文档基本信息
- 校验报告展示（核心）
- 修正操作入口
- 修正后文档下载

#### ValidationReportPage

- 校验结果详情
- 按 severity 分组展示
- 可修正项的操作入口
- AI 增强结果的置信度展示

## 7. 与后端 API 的交互

### 7.1 API 客户端封装

使用 Axios 或 Fetch 封装 API 客户端：

```typescript
// services/apiClient.ts
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

// 请求拦截器：添加 JWT Token
apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：统一错误处理
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 统一错误处理
    throw new ApiError(error.response?.data?.error);
  }
);
```

### 7.2 错误处理策略

1. **网络错误**：提示"网络连接失败，请重试"
2. **401 错误**：跳转登录页
3. **403 错误**：提示"无权限访问"
4. **4xx 业务错误**：显示后端返回的错误消息
5. **5xx 错误**：提示"服务器错误，请稍后重试"

### 7.3 轮询策略（Job 状态）

校验和修正任务是异步的，前端需要轮询获取状态：

```typescript
// usePolling hook
function usePolling<T>(
  fetchFn: () => Promise<T>,
  condition: (data: T) => boolean,
  interval = 2000
) {
  // 状态：idle / polling / completed / error
  // 轮询直到 condition 返回 false 或超时
}
```

## 8. 状态管理设计

### 8.1 React Query 配置

```typescript
// 缓存配置
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 分钟
      gcTime: 1000 * 60 * 30, // 30 分钟
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});
```

### 8.2 缓存策略

| 资源 | 缓存时间 | 失效策略 |
|------|----------|----------|
| 模板列表 | 30 分钟 | 手动刷新 |
| 文档列表 | 5 分钟 | 列表操作后 invalidate |
| 文档详情 | 5 分钟 | 校验/修正后 invalidate |
| 校验结果 | 不缓存 | 每次重新获取 |

## 9. 组件设计规范

### 9.1 组件分类

| 类型 | 说明 | 示例 |
|------|------|------|
| Presentational | 只负责展示，props 传入数据 | DocumentCard, ValidationSummary |
| Container | 负责数据获取和状态管理 | DocumentList（使用 React Query） |
| Layout | 布局组件，组合多个子组件 | PageLayout, SidebarLayout |

### 9.2 组件文件组织

```text
components/
├── DocumentCard/
│   ├── index.ts          # 导出
│   ├── DocumentCard.tsx  # 组件实现
│   ├── DocumentCard.css # 样式（如果用 CSS Modules）
│   └── DocumentCard.test.tsx # 测试
```

### 9.3 Props 定义规范

使用 TypeScript interface 定义 props：

```typescript
interface DocumentCardProps {
  document: Document;
  onView: (id: string) => void;
  onDelete: (id: string) => void;
  className?: string;
}
```

## 10. 当前已知边界

1. 前端当前处于蓝图设计阶段，尚未在代码中系统落地。
2. 样式方案尚未确定（CSS Modules / Tailwind / styled-components）。
3. 是否使用 UI 组件库（Ant Design / Material UI / Radix）尚未确定。
4. 桌面客户端和 Word 插件的具体技术方案尚未确定。

## 11. 与其他文档的关联

- 前置文档：
  - `100-system-overview.md`（系统级概述）
  - `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`
- 相关文档：
  - `400-api-architecture.md`（前端调用后端 API）
  - `700-capability-map.md`（前端能力映射）

## 12. 待确认问题

1. 样式方案的选择（CSS Modules / Tailwind / styled-components）。
2. UI 组件库的选型（Ant Design / Material UI / Radix / 自研）。
3. 是否需要暗色模式支持。
4. 国际化（i18n）需求是否在 MVP 范围内。

## 13. 更新记录

**最近复核时间**：2026-04-28

**复核依据**：
- `docs/architecture/2026-04-28-mvp-engineering-blueprint.md`（前端架构部分）
- `docs/knowledge/PaperNormAI-knowledge/100-system-overview.md`

**当前可信度**：中（蓝图设计阶段，尚未代码验证）

**待确认点**：样式方案、UI 组件库选型需要在实现阶段确认。