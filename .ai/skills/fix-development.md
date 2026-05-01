# Fix Development Skill

> 本 skill 定义 PaperNormAI 缺陷修复的标准流程和最佳实践。为 `PaperNormAI-feature-development` agent 提供缺陷修复指导。

## 1. 定位

Fix Development 是 `PaperNormAI-feature-development` 的辅助 skill。

当收到缺陷报告或 bug 时，使用本 skill 指导修复流程。

## 2. 修复流程

### 阶段 1：复现问题

```
1. 读取缺陷描述
2. 理解预期行为 vs 实际行为
3. 找到触发缺陷的最小条件
4. 编写失败的测试用例（复现测试）
5. 运行测试，确认失败
```

### 阶段 2：定位根因

```
1. 分析失败测试的调用栈
2. 定位到具体的问题代码
3. 分析为什么代码出错：
   - 逻辑错误？
   - 边界条件未处理？
   - 依赖问题？
   - 环境问题？
4. 记录根因
```

### 阶段 3：制定修复方案

```
1. 确定修复范围（只改必要代码）
2. 评估对其他功能的影响（回归风险）
3. 确定修复策略：
   - 改代码？还是改测试？还是改设计？
4. 编写修复计划
```

### 阶段 4：实现修复

```
1. 修复代码
2. 修复后运行复现测试，确认通过
3. 运行相关单元测试，确认无回归
4. 运行集成测试（如果涉及 API）
```

### 阶段 5：验证

```
1. 测试覆盖率检查（修复不降低覆盖率）
2. Linting 和类型检查
3. 如果是安全相关，进行安全审查
```

### 阶段 6：同步知识

```
1. 记录根因和修复方案到知识库（如需要）
2. 如果是知识文档与代码不一致，更新知识文档
3. 更新 900-learning-log.md
```

## 3. 修复优先级

| 优先级 | 场景 | 处理策略 |
|--------|------|----------|
| P0-Critical | 系统崩溃、数据丢失、安全漏洞 | 立即修复，24小时内上线 |
| P1-High | 核心功能不可用 | 快速修复，1-3天内修复 |
| P2-Medium | 非核心功能异常、边界情况 | 计划修复，下个迭代 |
| P3-Low |  UI 细节、文档错误 | 后续修复 |

## 4. 修复规范

### 4.1 最小修复原则

只修复报告的问题，不借机"改进"无关代码。

如果发现其他问题：
- 记录到 BUILD-LOG.md 的 Known Gaps
- 不在本次修复中处理

### 4.2 测试追加原则

每个修复必须追加测试，防止回归。

```
修复 + 新增测试 = 完整修复
```

### 4.3 回归测试原则

修复后必须运行相关测试，确保不破坏已有功能。

```
如果时间紧迫，优先保证核心路径的回归测试
```

## 5. 常见缺陷类型与处理

### 5.1 逻辑错误

```python
# 错误示例
if age > 18 and age < 65:  # 应该是 <= 65
    pass

# 修复后
if 18 <= age <= 65:
    pass
```

### 5.2 空指针/None 检查缺失

```python
# 错误示例
def get_template(self, template_id):
    return self.templates[template_id]  # 可能 KeyError

# 修复后
def get_template(self, template_id):
    return self.templates.get(template_id)  # 返回 None
```

### 5.3 边界条件未处理

```python
# 错误示例
def calculate_line_spacing(spacing_type):
    if spacing_type == "single":
        return 1.0
    elif spacing_type == "double":
        return 2.0
    # else 未处理

# 修复后
def calculate_line_spacing(spacing_type):
    mapping = {"single": 1.0, "double": 2.0, "1.5": 1.5}
    return mapping.get(spacing_type, 1.0)  # 默认值
```

### 5.4 并发问题

```python
# 错误示例（多线程不安全）
class ValidationJobManager:
    _current_job = None  # 类变量，线程共享

    def set_job(self, job):
        self._current_job = job  # 竞态条件

# 修复后
from threading import Lock

class ValidationJobManager:
    _lock = Lock()

    def set_job(self, job):
        with self._lock:
            self._current_job = job
```

### 5.5 文件路径问题

```python
# 错误示例
def save_document(path):
    with open(path, "w") as f:  # Windows 路径问题
        f.write(content)

# 修复后
from pathlib import Path

def save_document(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
```

## 6. 输出格式

```markdown
## Fix 报告

**缺陷描述**：
{缺陷的一句话描述}

**预期行为**：
{期望的行为}

**实际行为**：
{实际观察到的行为}

**根因分析**：
{根本原因分析}

**修复方案**：
{修复的具体方案}

**涉及文件**：
- {file1}
- {file2}

**新增测试**：
- {test1}
- {test2}

**回归测试**：
- {test3}
- {test4}

**后续建议**：
- {建议1}（如果有限）
- {建议2}
```

## 7. 示例

### 示例输入

```
Bug: 上传 5MB 以上的文件时返回 500 错误
```

### 示例输出

```markdown
## Fix 报告

**缺陷描述**：
大文件上传返回 500 错误

**预期行为**：
正常处理 5MB 以上文件，返回 201

**实际行为**：
返回 500，内部错误信息待查

**根因分析**：
服务器默认请求体大小限制为 10MB，但 FastAPI 默认限制较小。
文件写入时使用同步方式，导致大文件处理超时。

**修复方案**：
1. 在 FastAPI app 中配置 `max_upload_size`
2. 使用异步文件处理替代同步写入
3. 添加文件大小验证

**涉及文件**：
- `backend/app/api/main.py`
- `backend/app/infrastructure/storage.py`

**新增测试**：
- `test_upload_large_file_succeeds`
- `test_upload_exceeds_limit_returns_413`

**回归测试**：
- `test_upload_small_file_succeeds`
- `test_upload_normal_file_succeeds`

**后续建议**：
- 考虑添加文件大小配置项
- 考虑流式处理以支持更大文件
```

## 8. 使用场景

- 收到 bug report 时
- 发现缺陷需要修复时
- 代码审查中发现问题需要修复时

## 9. 更新记录

**创建时间**：2026-05-01

**依据**：PaperNormAI MVP Engineering Blueprint、Testing Principles