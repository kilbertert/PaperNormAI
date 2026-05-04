"""Rule extraction service for extracting semantic rules from specification documents."""

from typing import List, Dict, Optional
from app.infrastructure.docling.document_model import DocumentModel
from app.infrastructure.ai.openai_provider import OpenAIProvider


class RuleExtractionService:
    """Service for extracting semantic rules from spec documents using AI."""

    PROMPT_TEMPLATE = """# 角色
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
2. 例如："正文应使用宋体" 而非 {{"font": "songti"}}
3. 例如："标题应该加粗" 而非 {{"bold": true}}
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

{content}
"""

    def __init__(self, openai_provider: Optional[OpenAIProvider] = None):
        self._provider = openai_provider or OpenAIProvider()

    def extract_rules(self, spec_doc: DocumentModel) -> List[Dict[str, str]]:
        """Extract semantic rules from a specification document.

        Args:
            spec_doc: DocumentModel parsed from specification document

        Returns:
            List of rule dicts, each containing:
            - category: str (font/size/spacing/margin/heading/paragraph)
            - description: str (natural language description)
            - priority: str (必须/建议)
        """
        content = spec_doc.get_text_content()

        if not content.strip():
            return []

        prompt = self.PROMPT_TEMPLATE.format(content=content)
        response = self._call_ai(prompt)

        if not response:
            return []

        return self._parse_rules(response)

    def _call_ai(self, prompt: str) -> Optional[str]:
        """Call OpenAI API for rule extraction."""
        if not self._provider.is_configured():
            return None

        try:
            import openai
            response = self._provider._client.chat.completions.create(
                model=self._provider._model,
                messages=[
                    {"role": "system", "content": "你是一位专业的论文格式规范专家。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=2000,
                timeout=self._provider._timeout,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def _parse_rules(self, response: str) -> List[Dict[str, str]]:
        """Parse AI response into rule list."""
        rules = []
        lines = response.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('示例') or line.startswith('---'):
                continue

            # Parse format: [category] priority: description
            if line.startswith('[') and ']' in line:
                try:
                    bracket_end = line.index(']')
                    category_part = line[1:bracket_end]
                    rest = line[bracket_end + 1:].strip()

                    if rest.startswith('必须:') or rest.startswith('建议:'):
                        priority = rest[:2]
                        description = rest[3:]
                        category = self._normalize_category(category_part)

                        rules.append({
                            'category': category,
                            'description': description,
                            'priority': priority,
                        })
                except (ValueError, IndexError):
                    continue

        return rules

    def _normalize_category(self, category: str) -> str:
        """Normalize category string to match ViolationCategory enum values."""
        category_map = {
            'font': 'font',
            'size': 'font_size',
            'spacing': 'line_spacing',
            'margin': 'page_margin',
            'heading': 'heading',
            'paragraph': 'paragraph_spacing',
        }
        return category_map.get(category.lower(), category.lower())
