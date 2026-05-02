"""Pattern-based rule extractor from specification documents.

Extracts formatting rules from natural language specification text
using regex patterns for known formats like font sizes, margins, etc.

The extractor produces rules with handler-compatible IDs directly,
NOT generated IDs that need mapping later.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ExtractedRule:
    """A rule extracted from specification text."""
    rule_id: str  # Must be a RuleEngine-compatible handler name
    name: str
    level: str  # L1, L2, L3
    description: str
    severity: str
    auto_fixable: bool
    params: Dict
    source_text: str
    confidence: float = 1.0


class RulePatternExtractor:
    """Extracts rules using regex patterns from known specification formats.

    Rule IDs are generated directly as RuleEngine handler names:
    - font_name_body, font_name_heading
    - font_size_body
    - line_spacing, paragraph_spacing
    - page_margin
    - heading_level, citation_format, reference_format
    """

    # Font size patterns: 三号, 四号, 小四, 12pt, 12磅
    FONT_SIZE_PATTERNS = [
        (r'三号', 16),
        (r'二号', 22),
        (r'四号', 14),
        (r'小四', 12),
        (r'五号', 10.5),
        (r'(\d+)[pt磅]', None),  # e.g., 12pt, 23磅
        (r'(\d+\.?\d*)号', None),  # e.g., 12号
    ]

    # Font name patterns
    FONT_NAME_PATTERNS = [
        (r'黑体', '黑体'),
        (r'宋体', '宋体'),
        (r'仿宋', '仿宋'),
        (r'楷体', '楷体'),
        (r'Times\s*New\s*Roman', 'Times New Roman'),
        (r'宋体', 'SimSun'),
        (r'黑体', 'SimHei'),
    ]

    # Margin patterns: 2.54cm, 3.0cm
    MARGIN_PATTERNS = [
        (r'上.*?[页边距]?[为:]?\s*(\d+\.?\d*)\s*cm', 'top'),
        (r'下.*?[页边距]?[为:]?\s*(\d+\.?\d*)\s*cm', 'bottom'),
        (r'左.*?[页边距]?[为:]?\s*(\d+\.?\d*)\s*cm', 'left'),
        (r'右.*?[页边距]?[为:]?\s*(\d+\.?\d*)\s*cm', 'right'),
        (r'[上下左右].*?[页边距为、为:]?\s*(\d+\.?\d*)\s*cm', None),  # 复合
    ]

    # Line spacing patterns: 23磅, 1.5倍, 固定值23磅
    LINE_SPACING_PATTERNS = [
        (r'固定值\s*(\d+)\s*磅', 'fixed_pt'),
        (r'(\d+\.?\d*)\s*倍\s*行距', 'multiplier'),
        (r'行距.*?[为:]?\s*(\d+\.?\d*)\s*磅', 'fixed_pt'),
        (r'行距.*?[为:]?\s*(\d+\.?\d*)\s*倍', 'multiplier'),
    ]

    # Paper size patterns
    PAPER_SIZE_PATTERNS = [
        (r'A4', 'A4'),
        (r'A3', 'A3'),
        (r'B5', 'B5'),
    ]

    # Alignment patterns
    ALIGNMENT_PATTERNS = [
        (r'居中', 'center'),
        (r'居左|左起', 'left'),
        (r'居右|右起', 'right'),
        (r'两端', 'justify'),
    ]

    # Bold patterns
    BOLD_PATTERNS = [
        (r'加粗', True),
        (r'不加粗', False),
    ]

    # Heading level patterns
    HEADING_LEVEL_PATTERNS = [
        (r'章标题', 1),
        (r'节标题', 2),
        (r'小节标题', 3),
    ]

    def __init__(self):
        self._element_type_counter = {}  # Track counts per element type for params

    def extract_rules_from_text(self, text: str) -> List[ExtractedRule]:
        """Extract all rules from a block of specification text.

        Args:
            text: Natural language specification text

        Returns:
            List of extracted rules with correct handler-compatible IDs
        """
        rules = []

        rules.extend(self._extract_page_setup_rules(text))
        rules.extend(self._extract_font_rules(text))
        rules.extend(self._extract_paragraph_rules(text))
        rules.extend(self._extract_heading_rules(text))
        rules.extend(self._extract_abstract_rules(text))
        rules.extend(self._extract_toc_rules(text))

        return rules

    def _extract_page_setup_rules(self, text: str) -> List[ExtractedRule]:
        """Extract page setup rules (margins, paper size, line spacing)."""
        rules = []

        # Paper size
        paper_match = re.search(r'纸型\s*为\s*([A-Z]\d)', text)
        if paper_match:
            rules.append(ExtractedRule(
                rule_id="page_margin",  # Direct handler name
                name="纸型",
                level="L1",
                description=f"纸型为{paper_match.group(1)}",
                severity="error",
                auto_fixable=False,
                params={"paper_size": paper_match.group(1)},
                source_text=paper_match.group(0),
            ))

        # Margins - 复合提取
        margin_text = re.search(
            r'上下.*?[页边距为、为:]?\s*(\d+\.?\d*)\s*cm.*?'
            r'左边距\s*为\s*(\d+\.?\d*)\s*cm.*?'
            r'右边距\s*为\s*(\d+\.?\d*)\s*cm',
            text, re.DOTALL
        )
        if margin_text:
            top_bottom = margin_text.group(1)
            left = margin_text.group(2)
            right = margin_text.group(3)
            rules.append(ExtractedRule(
                rule_id="page_margin",  # Direct handler name
                name="页边距",
                level="L1",
                description=f"上下{top_bottom}cm，左右{left}cm、{right}cm",
                severity="error",
                auto_fixable=False,
                params={
                    "top": float(top_bottom),
                    "bottom": float(top_bottom),
                    "left": float(left),
                    "right": float(right),
                    "unit": "cm",
                    "tolerance": 0.1,
                },
                source_text=margin_text.group(0),
            ))

        # Line spacing - "正文行距为固定值23磅"
        line_spacing_match = re.search(r'正文\s*行距\s*为\s*固定值\s*(\d+)\s*磅', text)
        if line_spacing_match:
            rules.append(ExtractedRule(
                rule_id="line_spacing",  # Direct handler name
                name="正文行距",
                level="L1",
                description=f"正文行距为固定值{line_spacing_match.group(1)}磅",
                severity="error",
                auto_fixable=True,
                params={
                    "expected_value": int(line_spacing_match.group(1)),
                    "unit": "pt",
                    "line_spacing_type": "fixed",
                    "tolerance": 0.5,
                },
                source_text=line_spacing_match.group(0),
            ))

        return rules

    def _extract_font_rules(self, text: str) -> List[ExtractedRule]:
        """Extract font name and size rules with correct handler IDs."""
        rules = []

        # Detect element context
        element_type = self._detect_element_type(text)

        # Detect font name
        font_name = None
        for pattern, font in self.FONT_NAME_PATTERNS:
            if re.search(pattern, text):
                font_name = font
                break

        # Detect font size
        font_size = None
        for pattern, size in self.FONT_SIZE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                if size:
                    font_size = size
                elif match.groups()[0]:
                    font_size = int(match.groups()[0])
                break

        # Determine correct handler based on element type
        if element_type in ['heading_chapter', 'heading_section', 'heading_subsection']:
            handler_id = 'font_name_heading'
        else:
            handler_id = 'font_name_body'

        if font_name or font_size:
            name = "正文字体" if handler_id == 'font_name_body' else "标题字体"

            params = {}
            if font_name:
                params["expected_value"] = font_name
                params["allowed_fonts"] = [font_name]
            if font_size:
                params["expected_size"] = font_size
                params["font_size_unit"] = "pt"

            rules.append(ExtractedRule(
                rule_id=handler_id,  # Direct handler name, not generated
                name=name,
                level="L1",
                description=text[:100] if len(text) > 100 else text,
                severity="error",
                auto_fixable=True,
                params=params,
                source_text=text[:200],
            ))

        return rules

    def _extract_paragraph_rules(self, text: str) -> List[ExtractedRule]:
        """Extract paragraph spacing rules."""
        rules = []

        # First line indent: "首行缩进2字符"
        indent_match = re.search(r'首行缩进\s*(\d+)\s*字符', text)
        if indent_match:
            rules.append(ExtractedRule(
                rule_id="paragraph_spacing",  # Direct handler name
                name="首行缩进",
                level="L1",
                description=f"首行缩进{indent_match.group(1)}字符",
                severity="warning",
                auto_fixable=True,
                params={
                    "first_line_indent": int(indent_match.group(1)),
                    "indent_unit": "character",
                },
                source_text=indent_match.group(0),
            ))

        # Paragraph spacing before/after
        space_before_match = re.search(r'段前\s*(\d+\.?\d*)\s*行', text)
        space_after_match = re.search(r'段后\s*(\d+\.?\d*)\s*行', text)

        if space_before_match or space_after_match:
            params = {}
            if space_before_match:
                params["space_before"] = float(space_before_match.group(1))
            if space_after_match:
                params["space_after"] = float(space_after_match.group(1))

            rules.append(ExtractedRule(
                rule_id="paragraph_spacing",  # Direct handler name
                name="段落间距",
                level="L1",
                description=text[:100],
                severity="warning",
                auto_fixable=True,
                params=params,
                source_text=text[:200],
            ))

        return rules

    def _extract_heading_rules(self, text: str) -> List[ExtractedRule]:
        """Extract heading formatting rules with correct handler IDs."""
        rules = []

        # Detect heading level from text content
        heading_level = None
        for pattern, lvl in self.HEADING_LEVEL_PATTERNS:
            if re.search(pattern, text):
                heading_level = lvl
                break

        # Check explicit level mentions
        level_match = re.search(r'(\d级)标题', text)
        if level_match:
            level_text = level_match.group(1)
            if '1' in level_text:
                heading_level = 1
            elif '2' in level_text:
                heading_level = 2
            elif '3' in level_text:
                heading_level = 3

        # Font for heading
        font_name = None
        for pattern, font in self.FONT_NAME_PATTERNS:
            if re.search(pattern, text):
                font_name = font
                break

        # Alignment
        alignment = None
        for pattern, align in self.ALIGNMENT_PATTERNS:
            if re.search(pattern, text):
                alignment = align
                break

        if font_name or alignment:
            params = {}
            if font_name:
                params["expected_value"] = font_name
                params["allowed_fonts"] = [font_name]
            if alignment:
                params["alignment"] = alignment
            if heading_level:
                params["heading_level"] = heading_level

            name = f"{heading_level}级标题" if heading_level else "标题字体"

            rules.append(ExtractedRule(
                rule_id="font_name_heading",  # Direct handler name
                name=name,
                level="L1",
                description=text[:100],
                severity="error",
                auto_fixable=True,
                params=params,
                source_text=text[:200],
            ))

        return rules

    def _extract_abstract_rules(self, text: str) -> List[ExtractedRule]:
        """Extract abstract/keywords formatting rules."""
        rules = []

        # Abstract heading (Chinese)
        if re.search(r'"摘要"|“摘要”', text) and not re.search(r'英文', text):
            rules.append(ExtractedRule(
                rule_id="font_name_body",  # Use body font handler
                name="中文摘要标题",
                level="L1",
                description=text[:100],
                severity="error",
                auto_fixable=True,
                params={"text": "摘要"},
                source_text=text[:200],
            ))

        # Keywords heading (Chinese)
        if re.search(r'"关键词"|"关键词"|关键词', text) and not re.search(r'英文', text):
            rules.append(ExtractedRule(
                rule_id="font_name_body",
                name="中文关键词标题",
                level="L1",
                description=text[:100],
                severity="warning",
                auto_fixable=True,
                params={"text_pattern": "关键词"},
                source_text=text[:200],
            ))

        # English abstract
        if re.search(r'ABSTRACT', text):
            rules.append(ExtractedRule(
                rule_id="font_name_body",
                name="英文摘要标题",
                level="L1",
                description=text[:100],
                severity="error",
                auto_fixable=True,
                params={"text": "ABSTRACT", "expected_font": "Times New Roman"},
                source_text=text[:200],
            ))

        # English keywords
        if re.search(r'KEY WORDS', text):
            rules.append(ExtractedRule(
                rule_id="font_name_body",
                name="英文关键词标题",
                level="L1",
                description=text[:100],
                severity="warning",
                auto_fixable=True,
                params={"text_pattern": "KEY WORDS", "expected_font": "Times New Roman"},
                source_text=text[:200],
            ))

        return rules

    def _extract_toc_rules(self, text: str) -> List[ExtractedRule]:
        """Extract table of contents rules."""
        rules = []

        if re.search(r'目录', text):
            rules.append(ExtractedRule(
                rule_id="heading_level",  # Direct handler name
                name="目录",
                level="L2",
                description="目录格式要求",
                severity="warning",
                auto_fixable=False,
                params={},
                source_text=text[:200],
            ))

        return rules

    def _detect_element_type(self, text: str) -> str:
        """Detect the element type from text content."""
        text_lower = text.lower()

        if any(kw in text_lower for kw in ['章标题', '每章标题']):
            return 'heading_chapter'
        elif any(kw in text_lower for kw in ['节标题', '小节', '2级', '3级']):
            return 'heading_section'
        elif any(kw in text_lower for kw in ['图题', '图号']):
            return 'figure'
        elif any(kw in text_lower for kw in ['表题', '表格']):
            return 'table'
        elif any(kw in text_lower for kw in ['公式']):
            return 'formula'
        elif any(kw in text_lower for kw in ['参考文献', '引用']):
            return 'reference'
        else:
            return 'body'
