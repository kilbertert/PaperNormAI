# AI Prompt 设计

## 概述

本文档定义 PaperNormAI 中 AI 语义规则提取和校验的 prompt 设计。

## 前提：DocumentModel 结构

docling 解析后的 `DocumentModel` 包含：

```python
DocumentModel:
  - paragraphs: List[Paragraph]
      - text: str              # 段落文本
      - segments: List[TextSegment]
          - content: str       # 文本片段内容
          - font: FontInfo      # 字体信息
      - paragraph_format: ParagraphFormat
          - line_spacing_type: LineSpacingType  # SINGLE/ONE_POINT_FIVE/DOUBLE/EXACT/MULTIPLE
          - line_spacing_value: Optional[float]
          - space_before: float
          - space_after: float
          - alignment: Alignment
      - style_name: Optional[str]
  - page_format: PageFormat
      - top_margin, bottom_margin, left_margin, right_margin (points)
      - page_width, page_height (points)
  - structure: DocumentStructure
      - title: Optional[str]
      - sections: List[StructureItem]
          - title: str
          - level: int
          - paragraph_index: int
```

---

## Prompt 1: 规则提取 (Rule Extraction)

### 用途

从规范手册（spec_doc）的 `DocumentModel` 中提取语义规则。

### 输入

- 规范手册的完整文本内容（`DocumentModel.get_text_content()`）
- 可选：规范手册的段落结构和格式信息

### Prompt Template

```
# 角色
你是一位专业的论文格式规范专家。你需要从提供的论文格式规范文档中提取关键的格式要求。

# 任务
请仔细阅读以下论文格式规范文档，提取所有与以下方面相关的格式规则：

1. **字体规范**：正文字体、标题字体、英文/数字字体要求
2. **字号规范**：各层级标题字号、正文字号、页码字号
3. **行距规范**：正文行距、段前段后间距
4. **页边距规范**：上下左右边距要求
5. **标题层级规范**：章/节/条的编号格式和样式要求
6. **段落规范**：对齐方式、缩进要求

# 要求

1. 提取的规则应该是**抽象描述性规则**，而不是具体的数值参数
2. 例如："正文应使用宋体" 而非 {"font": "songti"}
3. 例如："标题应该加粗" 而非 {"bold": true}
4. 每条规则应包含：
   - 规则类别（font/size/spacing/margin/heading/paragraph）
   - 规则描述（用自然语言描述）
   - 优先级（必须/建议）

# 输出格式

请以结构化文本形式输出规则，每条规则格式如下：

[规则类别] 优先级: [具体描述]

---

示例输出：

[font] 必须: 正文字体应为宋体，不应使用黑体或楷体
[font] 必须: 英文和数字应使用 Times New Roman 字体
[size] 必须: 章标题使用三号黑体加粗（约16pt）
[size] 必须: 正文字号应为小四号（约12pt）
[spacing] 必须: 正文行距为1.5倍行距
[spacing] 建议: 段前段后间距各0.5行
[margin] 必须: 上边距30mm，下边距25mm，左边距30mm，右边距20mm
[heading] 必须: 章节标题应突出重点、简明扼要，不超过15字
[heading] 必须: 标题中尽量不采用英文缩写词
[paragraph] 必须: 正文段落采用两端对齐方式

---

# 规范文档内容

{规范文档文本内容}
```

### 输出处理

解析 AI 输出，生成规则列表（供后续校验使用）。

---

## Prompt 2: 语义校验 (Semantic Validation)

### 用途

基于提取的规则，对论文（thesis_doc）的 `DocumentModel` 进行语义校验。

### 输入

- 论文的 `DocumentModel`
- 规则列表（来自 Prompt 1 的输出）

### Prompt Template

```
# 角色
你是一位专业的论文格式校验专家。你需要根据提供的格式规则，检查论文文档的格式是否符合规范。

# 任务
请仔细阅读论文内容和格式规则，逐项检查论文格式。

# 规则列表

{规则列表}

---

# 论文段落信息

以下是从论文中提取的段落信息（按顺序编号）：

{for paragraph_index, para in enumerate(paragraphs)}
段落{paragraph_index}:
- 内容: "{para.text}"
- 字体: {para.segments[0].font.name if para.segments else 'unknown'}
- 字号: {para.segments[0].font.size if para.segments else 'unknown'}pt
- 是否加粗: {para.segments[0].font.bold if para.segments else False}
- 是否斜体: {para.segments[0].font.italic if para.segments else False}
- 行距类型: {para.paragraph_format.line_spacing_type.value}
- 段前间距: {para.paragraph_format.space_before}pt
- 段后间距: {para.paragraph_format.space_after}pt
- 对齐方式: {para.paragraph_format.alignment.value}
- 样式: {para.style_name or 'Normal'}
---

# 页面格式

- 页宽: {page_format.page_width}pt
- 页高: {page_format.page_height}pt
- 上边距: {page_format.top_margin}pt ({page_format.top_margin/28.35:.1f}mm)
- 下边距: {page_format.bottom_margin}pt ({page_format.bottom_margin/28.35:.1f}mm)
- 左边距: {page_format.left_margin}pt ({page_format.left_margin/28.35:.1f}mm)
- 右边距: {page_format.right_margin}pt ({page_format.right_margin/28.35:.1f}mm)

# 要求

1. 逐条检查规则是否被违反
2. 对于每条违规，提供：
   - 违规所在的段落编号
   - 原始内容（该段落的相关文本）
   - 违规描述
   - 修正建议（如果可以自动修正）
3. 如果规则被正确遵守，无需报告
4. 如果无法确定是否违规，基于"建议修正"而非"必须修正"处理

# 输出格式

请以结构化文本形式输出违规列表，格式如下：

[违规]
段落: {段落编号}
原始内容: "{相关文本片段}"
违规规则: {规则描述}
违规类型: {font/size/spacing/margin/heading/paragraph}
严重程度: ERROR（必须修正）/ WARNING（建议修正）
修正建议: {具体的修正方式}

---

如果没有发现任何违规，请输出：

[校验结果]
未发现格式违规，论文格式符合规范要求。

---

# 开始校验
```

### 输出处理

解析 AI 输出，生成 `ValidationReport`（包含 `ViolationDetail` 列表）。

---

## Prompt 3: 修正内容生成 (Fix Generation)

### 用途

当用户需要了解修正详情时，生成具体的修正对比（用于 Git-diff 展示）。

### 输入

- 单个违规的 `ViolationDetail`
- 相关段落完整内容

### Prompt Template

```
# 角色
你是一位专业的论文格式修正助手。

# 任务
给定一个格式违规和原始段落内容，请生成修正后的内容。

# 违规信息

- 违规类型: {violation.category}
- 当前状态: {original_content}
- 修正目标: {suggested_fix}

# 原始段落内容

"{paragraph_text}"

# 要求

1. 只修改需要修正的部分，保持段落其他内容不变
2. 修正后的内容应该自然流畅
3. 输出格式：
   - 原始内容（需要修改的部分）
   - 修正后内容
   - 完整修正后段落

# 输出格式

原始内容: {original_content}
修正后内容: {corrected_content}
完整段落: {full_corrected_paragraph}
```

---

## 设计决策

1. **规则形态为描述性文本** — 避免结构化参数，确保覆盖完整语义
2. **三阶段分离** — 规则提取 → 语义校验 → 修正生成，职责单一
3. **段落编号作为位置标识** — 避免字符偏移的复杂性
4. **严重程度分级** — ERROR（必须修正）和 WARNING（建议修正）分离，方便用户批量处理
5. **上下文信息完整** — 每个违规都包含前后段落，便于定位和理解

---

*本文件由 Architect 维护，定义 AI 语义处理的 prompt 模板*