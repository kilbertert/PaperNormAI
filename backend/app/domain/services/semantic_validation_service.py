"""Semantic validation service for validating thesis documents against rules."""

from typing import List, Dict, Optional
from datetime import datetime
from app.infrastructure.docling.document_model import DocumentModel
from app.infrastructure.ai.openai_provider import OpenAIProvider
from app.domain.entities.validation_report import (
    ValidationReport,
    ViolationDetail,
    ViolationCategory,
    ViolationSeverity,
    TextLocation,
)


class SemanticValidationService:
    """Service for semantic validation of thesis documents using AI."""

    PROMPT_TEMPLATE = """# 角色
你是一位专业的论文格式校验专家。你需要根据提供的格式规则，检查论文文档的格式是否符合规范。

# 任务
请仔细阅读论文内容和格式规则，逐项检查论文格式。

# 规则列表

{rules}

---

# 论文段落信息

以下是从论文中提取的段落信息（按顺序编号）：

{paragraphs_info}

# 页面格式

- 页宽: {page_width}pt
- 页高: {page_height}pt
- 上边距: {top_margin}pt ({top_margin_mm:.1f}mm)
- 下边距: {bottom_margin}pt ({bottom_margin_mm:.1f}mm)
- 左边距: {left_margin}pt ({left_margin_mm:.1f}mm)
- 右边距: {right_margin}pt ({right_margin_mm:.1f}mm)

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
"""

    def __init__(self, openai_provider: Optional[OpenAIProvider] = None):
        self._provider = openai_provider or OpenAIProvider()

    def validate(
        self,
        thesis_doc: DocumentModel,
        rules: List[Dict[str, str]],
        document_name: str = "unknown",
        template_name: Optional[str] = None,
    ) -> ValidationReport:
        """Validate thesis document against extracted rules.

        Args:
            thesis_doc: DocumentModel parsed from thesis document
            rules: List of rule dicts from RuleExtractionService
            document_name: Name of the thesis document
            template_name: Name of the template/spec document

        Returns:
            ValidationReport with violations found
        """
        report = ValidationReport(
            document_name=document_name,
            template_name=template_name,
        )

        rules_text = self._format_rules(rules)
        paragraphs_info = self._format_paragraphs(thesis_doc)

        prompt = self.PROMPT_TEMPLATE.format(
            rules=rules_text,
            paragraphs_info=paragraphs_info,
            page_width=thesis_doc.page_format.page_width,
            page_height=thesis_doc.page_format.page_height,
            top_margin=thesis_doc.page_format.top_margin,
            top_margin_mm=thesis_doc.page_format.top_margin / 28.35,
            bottom_margin=thesis_doc.page_format.bottom_margin,
            bottom_margin_mm=thesis_doc.page_format.bottom_margin / 28.35,
            left_margin=thesis_doc.page_format.left_margin,
            left_margin_mm=thesis_doc.page_format.left_margin / 28.35,
            right_margin=thesis_doc.page_format.right_margin,
            right_margin_mm=thesis_doc.page_format.right_margin / 28.35,
        )

        response = self._call_ai(prompt)

        if response:
            violations = self._parse_violations(response, thesis_doc)
            for v in violations:
                report.add_violation(v)

        return report

    def _format_rules(self, rules: List[Dict[str, str]]) -> str:
        """Format rules list for prompt."""
        if not rules:
            return "（无明确规则）"
        lines = []
        for i, rule in enumerate(rules, 1):
            category = rule.get('category', 'unknown')
            description = rule.get('description', '')
            priority = rule.get('priority', '建议')
            lines.append(f"{i}. [{category}] {priority}: {description}")
        return '\n'.join(lines)

    def _format_paragraphs(self, doc: DocumentModel) -> str:
        """Format paragraphs for prompt."""
        lines = []
        for i, para in enumerate(doc.paragraphs, start=1):
            font_info = ""
            if para.segments and len(para.segments) > 0:
                seg = para.segments[0]
                font_info = f"字体: {seg.font.name}, 字号: {seg.font.size}pt, 加粗: {seg.font.bold}, 斜体: {seg.font.italic}"
            else:
                font_info = "字体: unknown"

            lines.append(f"""段落{i}:
- 内容: "{para.text[:100]}{'...' if len(para.text) >= 100 else ''}"
- {font_info}
- 行距类型: {para.paragraph_format.line_spacing_type.value}
- 段前间距: {para.paragraph_format.space_before}pt
- 段后间距: {para.paragraph_format.space_after}pt
- 对齐方式: {para.paragraph_format.alignment.value}
- 样式: {para.style_name or 'Normal'}
---""")
        return '\n'.join(lines)

    def _call_ai(self, prompt: str) -> Optional[str]:
        """Call OpenAI API for semantic validation."""
        if not self._provider.is_configured():
            return None

        try:
            import openai
            response = self._provider._client.chat.completions.create(
                model=self._provider._model,
                messages=[
                    {"role": "system", "content": "你是一位专业的论文格式校验专家。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=3000,
                timeout=self._provider._timeout,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def _parse_violations(self, response: str, doc: DocumentModel) -> List[ViolationDetail]:
        """Parse AI response into ViolationDetail list."""
        violations = []
        lines = response.split('\n')

        pending_violation_data = {}
        current_paragraph = None

        for line in lines:
            line = line.strip()

            if not line or (line.startswith('[') and line.endswith(']')):
                section = line.strip('[]')
                if section == '校验结果':
                    break
                if pending_violation_data:
                    self._create_violation_from_data(pending_violation_data, doc, violations)
                    pending_violation_data = {}
                continue

            if line.startswith('段落:'):
                try:
                    current_paragraph = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    continue

            elif line.startswith('[违规]'):
                if pending_violation_data:
                    self._create_violation_from_data(pending_violation_data, doc, violations)
                pending_violation_data = {"paragraph": current_paragraph, "line_collected": []}
                pending_violation_data["line_collected"].append(line)

            elif pending_violation_data is not None:
                pending_violation_data["line_collected"].append(line)

                if line.startswith('原始内容:'):
                    pending_violation_data["original_content"] = line.split(':', 1)[1].strip().strip('"')
                elif line.startswith('违规规则:'):
                    pending_violation_data["description"] = line.split(':', 1)[1].strip()
                elif line.startswith('违规类型:'):
                    pending_violation_data["category"] = line.split(':', 1)[1].strip()
                elif line.startswith('严重程度:'):
                    severity_str = line.split(':', 1)[1].strip()
                    pending_violation_data["severity"] = ViolationSeverity.ERROR if 'ERROR' in severity_str.upper() else ViolationSeverity.WARNING
                elif line.startswith('修正建议:'):
                    pending_violation_data["suggested_fix"] = line.split(':', 1)[1].strip()

        if pending_violation_data:
            self._create_violation_from_data(pending_violation_data, doc, violations)

        return violations

    def _create_violation_from_data(self, data: dict, doc: DocumentModel, violations: list) -> None:
        """Create a ViolationDetail from parsed data."""
        paragraph = data.get("paragraph")
        if paragraph is None:
            return

        category_str = data.get("category", "")
        severity = data.get("severity", ViolationSeverity.WARNING)
        description = data.get("description", "")
        original_content = data.get("original_content", "")
        suggested_fix = data.get("suggested_fix", "")

        if not description:
            return

        violation = ViolationDetail(
            category=self._normalize_category(category_str),
            severity=severity,
            description=description,
            location=TextLocation(
                paragraph_index=paragraph,
                text=doc.paragraphs[paragraph - 1].text if paragraph > 0 and paragraph <= len(doc.paragraphs) else "",
            ),
            original_content=original_content,
            suggested_fix=suggested_fix,
            context_before=doc.paragraphs[paragraph - 1].text if paragraph > 0 else None,
            context_after=doc.paragraphs[paragraph + 1].text if paragraph < len(doc.paragraphs) - 1 else None,
        )
        violations.append(violation)

    def _normalize_category(self, category: str) -> ViolationCategory:
        """Normalize category string to ViolationCategory enum."""
        category_map = {
            'font': ViolationCategory.FONT,
            'font_size': ViolationCategory.FONT_SIZE,
            'size': ViolationCategory.FONT_SIZE,
            'line_spacing': ViolationCategory.LINE_SPACING,
            'spacing': ViolationCategory.LINE_SPACING,
            'paragraph_spacing': ViolationCategory.PARAGRAPH_SPACING,
            'page_margin': ViolationCategory.PAGE_MARGIN,
            'margin': ViolationCategory.PAGE_MARGIN,
            'heading': ViolationCategory.HEADING,
        }
        return category_map.get(category.lower(), ViolationCategory.FONT)
