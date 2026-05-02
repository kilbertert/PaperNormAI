"""Tests for RulePatternExtractor."""

import pytest
from app.infrastructure.docx.rule_pattern_extractor import RulePatternExtractor, ExtractedRule


class TestRulePatternExtractor:
    """Test cases for pattern-based rule extraction."""

    def test_extract_page_margin(self):
        """Test extraction of page margin rules."""
        extractor = RulePatternExtractor()
        text = "页面设置：纸型为A4，上下页边距为2.54cm、左边距为3.0cm、右边距为2.6cm、正文行距为固定值23磅。"

        rules = extractor.extract_rules_from_text(text)

        margin_rules = [r for r in rules if 'margin' in r.rule_id]
        assert len(margin_rules) > 0, "Should extract page margin rule"

        margin_rule = margin_rules[0]
        assert margin_rule.params.get('top') == 2.54
        assert margin_rule.params.get('left') == 3.0
        assert margin_rule.params.get('right') == 2.6

    def test_extract_line_spacing(self):
        """Test extraction of line spacing rule."""
        extractor = RulePatternExtractor()
        text = "正文行距为固定值23磅"

        rules = extractor.extract_rules_from_text(text)

        line_rules = [r for r in rules if 'line_spacing' in r.rule_id]
        assert len(line_rules) > 0, "Should extract line spacing rule"
        assert line_rules[0].params.get('expected_value') == 23

    def test_extract_font_rules(self):
        """Test extraction of font rules."""
        extractor = RulePatternExtractor()
        text = "每章标题以三号黑体居中打印"

        rules = extractor.extract_rules_from_text(text)

        font_rules = [r for r in rules if 'font' in r.rule_id]
        assert len(font_rules) > 0, "Should extract font rule"

    def test_extract_abstract_rules(self):
        """Test extraction of abstract formatting rules."""
        extractor = RulePatternExtractor()
        text = """（1）"摘要"两字间空两格，三号黑体，加粗，居中打印。
（2）另起一行打印摘要内容，首行缩进2字符，小四号宋体。
（3）摘要内容后下空一行居左打印"关键词"三字，三号黑体，加粗"""

        rules = extractor.extract_rules_from_text(text)

        abstract_rules = [r for r in rules if 'abstract' in r.rule_id or 'keywords' in r.rule_id]
        assert len(abstract_rules) >= 2, "Should extract abstract and keywords rules"

    def test_extract_heading_rules(self):
        """Test extraction of heading rules."""
        extractor = RulePatternExtractor()
        text = "每章标题以三号黑体居中打印；章下空二行为节，以小四号黑体左起打印"

        rules = extractor.extract_rules_from_text(text)

        heading_rules = [r for r in rules if 'heading' in r.rule_id]
        assert len(heading_rules) > 0, "Should extract heading rules"

    def test_extract_first_line_indent(self):
        """Test extraction of first line indent."""
        extractor = RulePatternExtractor()
        text = "首行缩进2字符，小四号宋体"

        rules = extractor.extract_rules_from_text(text)

        indent_rules = [r for r in rules if 'indent' in r.rule_id]
        assert len(indent_rules) > 0, "Should extract first line indent rule"
        assert indent_rules[0].params.get('first_line_indent') == 2

    def test_extract_paper_size(self):
        """Test extraction of paper size."""
        extractor = RulePatternExtractor()
        text = "纸型为A4，上下页边距为2.54cm"

        rules = extractor.extract_rules_from_text(text)

        paper_rules = [r for r in rules if 'paper' in r.rule_id or 'setup' in r.rule_id]
        assert len(paper_rules) > 0, "Should extract paper size rule"


class TestSpecificationToRulesPipeline:
    """Test cases for specification to rules pipeline."""

    def test_split_into_sections(self):
        """Test section splitting logic."""
        from app.infrastructure.docx.specification_to_rules import SpecificationToRulesPipeline
        from app.infrastructure.docx.document_parser import ParsedDocument, DocumentElement, DocumentMetadata

        pipeline = SpecificationToRulesPipeline()

        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="heading",
                content="五、毕业论文（设计）排版规范",
                style="Heading 1",
            ),
            DocumentElement(
                path="paragraph[2]",
                element_type="paragraph",
                content="页面设置：纸型为A4，上下页边距为2.54cm、左边距为3.0cm、右边距为2.6cm。",
                style="Normal",
            ),
            DocumentElement(
                path="paragraph[3]",
                element_type="heading",
                content="1、中文摘要和关键词：",
                style="Heading 2",
            ),
            DocumentElement(
                path="paragraph[4]",
                element_type="paragraph",
                content="（1）"摘要"两字间空两格，三号黑体，加粗，居中打印。",
                style="Normal",
            ),
        ]

        parsed_doc = ParsedDocument(
            metadata=DocumentMetadata(),
            elements=elements,
        )

        sections = pipeline._split_into_sections(parsed_doc)

        assert len(sections) >= 2, "Should split into multiple sections"
        assert "general" in sections or "五、毕业论文（设计）排版规范" in sections
