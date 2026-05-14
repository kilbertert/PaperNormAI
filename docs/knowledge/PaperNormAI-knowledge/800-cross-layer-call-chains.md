# PaperNormAI 跨层调用链知识

## 1. 文档目的

记录当前真实调用路径，明确请求如何在 API、领域服务、基础设施和持久化之间流转。

## 2. 覆盖范围

- 文档上传链路
- 模板规则校验链路（validations）
- 文档修正链路（corrections）
- spec 语义校验链路（spec）

## 3. 核心事实（代码事实态）

1. 当前主要编排发生在 API endpoint + domain service 组合，不是纯 application 层编排。  
2. 异步任务通过 FastAPI `BackgroundTasks`，任务状态落库到 `validation_jobs/correction_jobs`。  
3. spec 场景已使用 `SpecSessionRepository` 实现跨请求会话持久化。  
4. 鉴权在依赖层统一处理，资源访问在各 endpoint 内再次按 `user_id` 校验。

## 4. 关键调用链

### 4.1 文档上传

```text
POST /documents/upload
  -> 鉴权 get_current_user
  -> 临时文件落盘 + SHA256
  -> DocumentRepository.find_by_hash (去重)
  -> FileStorage.store
  -> DocumentRepository.save
  -> 返回 DocumentResponse
```

### 4.2 模板规则校验任务

```text
POST /validations/
  -> 参数校验 + 资源权限校验
  -> 创建 ValidationJobModel(status=pending)
  -> BackgroundTasks._run_validation_job
      -> job=running
      -> DocumentParser.parse
      -> TemplateService + RuleEngine.validate
      -> 写入 ValidationResultModel[]
      -> job=completed/failed
```

### 4.3 修正任务

```text
POST /corrections/
  -> 创建 CorrectionJobModel(status=pending)
  -> BackgroundTasks._run_correction_job
      -> 读取 CorrectionPlanModel
      -> CorrectionExecutor.execute
      -> DocumentWriter.write_to_docx
      -> job.output_path + status 更新
```

### 4.4 Spec 语义校验（Step 1: parse-spec）

```text
POST /spec/parse-spec
  -> DoclingDocumentParser.parse
  -> RuleExtractionService.extract_rules
  -> SpecSessionRepository.save
  -> 返回 session_id, rules_count
```

### 4.5 Spec 语义校验（Step 2: validate-with-spec）

```text
POST /spec/validate-with-spec
  -> SpecSessionRepository.find
  -> DoclingDocumentParser.parse
  -> SemanticValidationService.validate
  -> ValidationReportModel + ViolationDetailModel[] 同步落库
  -> 返回 report_id + 统计（total/error/warning/info_count）
```

### 4.6 Spec 语义校验（Step 3: get-report）

```text
GET /spec/reports/{report_id}
  -> ValidationReportModel + joinedload violations
  -> 校验 user_id 所有权
  -> 返回完整 ValidationReportResponse（含 violations[]）
```

### 4.7 前端完整用户流程

```text
浏览器 POST /auth/login
  -> 返回 access_token
  -> localStorage.setItem('access_token', token)

浏览器 POST /spec/parse-spec（携带 Bearer token）
  -> DoclingDocumentParser.parse
  -> RuleExtractionService.extract_rules
  -> SpecSessionRepository.save
  -> 返回 { session_id, rules_count }

浏览器 POST /spec/validate-with-spec（携带 Bearer token）
  -> SpecSessionRepository.find
  -> DoclingDocumentParser.parse
  -> SemanticValidationService.validate
  -> ValidationReportModel + ViolationDetailModel[] 落库
  -> 返回 { report_id, total_count, error_count, ... }

浏览器 GET /spec/reports/{report_id}（携带 Bearer token）
  -> ValidationReportModel + joinedload violations
  -> 返回 { report_id, session_id, total_count, violations[], ... }

前端渲染：
  -> 四格统计卡片（total/error/warning/info）
  -> violations[] 遍历展示（severity + category + description + original/suggested）
```

## 5. 层间边界观察

1. 前端纯 Client Components，`/spec` 链路无 SSR。
2. API 层承担编排（务实捷径），后续可下沉到 application 层。
3. Domain service 负责规则判定与修正策略，Infrastructure 负责解析/存储/AI 调用。
4. Repository 作为领域与 ORM 的桥接层已稳定使用。
5. Step 6A 修复后，domain 层不再直接依赖 infrastructure 层（依赖注入）。

## 6. 当前已知边界

1. `application/` 层存在但调用占比不高，尚未成为统一编排入口。  
2. 异步执行缺少独立队列中间件，任务可靠性依赖应用进程。  
3. 部分 endpoint 仍有较重逻辑，回归面扩大时维护成本会上升。

## 7. 与其他文档的关联

- 前置文档：`100-system-overview.md`  
- 相关文档：`300-backend-kernel-services.md`、`400-api-architecture.md`、`600-domain-models.md`、`200-database-models.md`

## 8. 待确认问题

1. 是否在下一阶段把编排逻辑统一迁移到 `application/` 用例层。  
2. 是否将后台任务迁移到 Celery/RQ 以提升可靠性。  
3. 调用链监控与可观测性（trace/log 关联）是否引入标准化方案。

## 9. 更新记录

**最近复核时间**：2026-05-14
**复核依据**：
- `backend/app/api/endpoints/spec_validation.py`
- `backend/app/infrastructure/persistence/spec_session_repository.py`
- `clients/apps/web/src/app/spec/[sessionId]/report/[reportId]/page.tsx`
- `clients/apps/web/src/lib/api.ts`

**当前可信度**：高  
**待确认点**：任务系统与 application 层收敛策略。
