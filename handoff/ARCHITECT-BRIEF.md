# Architect Brief
*Written by Architect. Read by Builder and Reviewer.*
*Overwrite this file each step — it is not a log, it is the current active brief.*

---

## Step 3 — 修复 Must Fix (Richard Review 反馈)

### 背景

Richard Review 发现 3 个 Must Fix 问题需要修复。

### Must Fix 清单

#### Fix 1: Corrections silently fail when no paragraph matches
**文件**: `backend/app/infrastructure/docx/document_merger.py`

**问题**: 当没有段落匹配时，`_replace_in_paragraphs()` 返回 `False` 但没有任何跟踪机制。调用方无法知道哪些修正失败了。

**修复**: 记录失败的修正，返回结构化结果而不是布尔值。

```python
@dataclass
class MergeResult:
    success: bool
    output_path: Optional[Path]
    applied_corrections: int
    failed_corrections: List[Dict]  # 记录失败的修正

def merge(self, original_path: Path, corrections: List[Dict]) -> MergeResult:
    # ... 返回结果中包含失败信息
```

---

#### Fix 2: paragraph_index hint is ignored in fallback path
**文件**: `backend/app/infrastructure/docx/document_merger.py`

**问题**: fallback 路径遍历所有段落，忽略了 `paragraph_index` 这个定位提示。

**修复**: 在 fallback 路径中优先检查指定的段落索引，再fallback 到全量搜索。

```python
if correction.get("paragraph_index"):
    target_idx = correction["paragraph_index"] - 1  # 转为 0-based
    if target_idx < len(doc.paragraphs):
        para = doc.paragraphs[target_idx]
        if self._paragraph_matches_context(para, correction):
            self._replace_in_paragraph(para, correction)
            continue  # 找到则跳到下一个 correction
# 如果指定段落没匹配，再全量搜索
```

---

#### Fix 3: AI-Word-Skill partial failure leaves document inconsistent
**文件**: `backend/app/infrastructure/docx/document_merger.py`

**问题**: 当 AI-Word-Skill 部分失败后 fallback 到同文档，潜在重复替换问题。

**修复**: 使用临时文件操作 + 原子性回退。

```python
def merge(self, original_path: Path, corrections: List[Dict]) -> MergeResult:
    # 1. 复制原文件到临时文件
    # 2. 在临时文件上操作
    # 3. 成功则返回临时文件路径
    # 4. 失败则删除临时文件，返回错误
    # 5. 调用方负责移动临时文件到最终位置
```

---

### Definition of Done

- [ ] Fix 1: 返回 MergeResult 包含失败跟踪
- [ ] Fix 2: fallback 路径优先使用 paragraph_index 提示
- [ ] Fix 3: 临时文件 + 原子性操作
- [ ] 测试验证

---

## Builder Plan
*[Builder fills this in]*

Architect approval: [ ] Approved / [ ] Redirect — see notes below