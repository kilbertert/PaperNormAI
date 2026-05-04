# ValidationReport 数据结构设计

## 设计目标

ValidationReport 是 AI 语义校验的输出，用于：
1. Git-diff 风格展示检测结果（原始内容 vs 修正后内容）
2. 支持用户手动编辑修正内容
3. 供 AI-Word-Skill 合并回 .docx

## 核心数据结构

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from uuid import UUID

class ViolationSeverity(str, Enum):
    """违规严重程度"""
    ERROR = "error"       # 必须修正
    WARNING = "warning"  # 建议修正
    INFO = "info"         # 信息提示

class ViolationCategory(str, Enum):
    """违规类别"""
    FONT = "font"                    # 字体
    FONT_SIZE = "font_size"          # 字号
    LINE_SPACING = "line_spacing"   # 行距
    PARAGRAPH_SPACING = "paragraph_spacing"  # 段前段后
    PAGE_MARGIN = "page_margin"      # 页边距
    HEADING = "heading"              # 标题层级
    # Phase 2
    TABLE = "table"                  # 表格
    FORMULA = "formula"              # 公式
    FIGURE = "figure"                # 插图
    REFERENCE = "reference"         # 参考文献

@dataclass
class TextLocation:
    """文本位置（用于定位文档中的具体位置）"""
    paragraph_index: int      # 段落索引
    text: str                 # 该段落的原始文本（用于校验）
    start_offset: Optional[int] = None   # 文本内起始位置
    end_offset: Optional[int] = None     # 文本内结束位置

@dataclass
class ViolationDetail:
    """单个违规详情"""
    id: UUID = field(default_factory=uuid.uuid4)

    # 违规基本信息
    category: ViolationCategory
    severity: ViolationSeverity
    description: str                          # 违规描述（如"字体应为宋体"）

    # 位置信息
    location: TextLocation

    # 原始状态 vs 修正建议
    original_content: str                      # 原始内容（如"黑体"）
    suggested_fix: str                         # 修正建议（如"宋体"）

    # 用户编辑（用户可以修改 suggested_fix）
    user_modified_fix: Optional[str] = None   # 用户手动修改后的修正内容

    # 上下文（用于 AI-Word-Skill 定位）
    context_before: Optional[str] = None       # 违规处前一段文本
    context_after: Optional[str] = None        # 违规处后一段文本

@dataclass
class ValidationReport:
    """完整的校验报告"""
    id: UUID = field(default_factory=uuid. uuid4)

    # 报告元信息
    document_name: str                         # 被校验的文档名
    template_name: Optional[str] = None        # 使用的规范来源（用户上传的手册名 或 "系统默认规则"）
    created_at: datetime = field(default_factory=datetime.utcnow)

    # 违规列表
    violations: List[ViolationDetail] = field(default_factory=list)

    # 汇总统计
    total_violations: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0

    # 处理状态
    status: str = "pending"   # pending, reviewed, confirmed, applied

    def add_violation(self, violation: ViolationDetail) -> None:
        self.violations.append(violation)
        self._recalc_stats()

    def _recalc_stats(self) -> None:
        self.total_violations = len(self.violations)
        self.error_count = sum(1 for v in self.violations if v.severity == ViolationSeverity.ERROR)
        self.warning_count = sum(1 for v in self.violations if v.severity == ViolationSeverity.WARNING)
        self.info_count = sum(1 for v in self.violations if v.severity == ViolationSeverity.INFO)

    def get_effective_fix(self, violation_id: UUID) -> str:
        """获取实际的修正内容（用户修改优先于 AI 建议）"""
        for v in self.violations:
            if v.id == violation_id:
                return v.user_modified_fix or v.suggested_fix
        raise ValueError(f"Violation {violation_id} not found")

    def confirm_all(self) -> None:
        """用户确认所有修正"""
        self.status = "confirmed"

    def get_editable_violations(self) -> List[ViolationDetail]:
        """获取用户可编辑的修正列表"""
        return [v for v in self.violations if v.user_modified_fix is not None or v.suggested_fix is not None]
```

## Git-diff 风格展示

前端展示时，每个违规呈现为：

```
- 原始内容: "三号黑体加粗"
+ 修正为:   "三号宋体"

位置: 第 3 段
违规类型: 字体 (ERROR)
描述: 正文字体应为宋体
```

## 与 AI-Word-Skill 的对接

`ValidationReport` 被确认后，提取所有 `ViolationDetail` 的 `get_effective_fix()` 传给 AI-Word-Skill：

```python
corrections = [
    {
        "original": v.original_content,
        "fixed": v.get_effective_fix(v.id),
        "location": {
            "paragraph_index": v.location.paragraph_index,
            "context_before": v.context_before,
            "context_after": v.context_after,
        }
    }
    for v in report.violations
]
```

## 设计决策

1. **位置信息简化**：使用 `paragraph_index + text` 而非精确字符偏移，因为 docling 的解析结果可能没有精确偏移，AI 比对时也更容易
2. **用户编辑**：`user_modified_fix` 允许用户在 AI 建议的基础上手动修改
3. **严重程度分离**：ERROR/WARNING/INFO 三级，方便用户过滤和批量处理
4. **Phase 2 扩展**：ViolationCategory 预留了 TABLE/FORMULA/FIGURE/REFERENCE，但 Phase 1 只用 FONT 相关的

## 待确认

1. `context_before` 和 `context_after` 的长度是否足够定位？
2. 是否需要支持批量"全部接受"或"全部忽略"？
3. 用户确认后，是一次性合并还是分段合并？