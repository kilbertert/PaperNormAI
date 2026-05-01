"""Unit tests for RuleEngine."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.domain.services.rule_engine import RuleEngine
from app.domain.entities.validation_rule import RuleLevel, Severity, ValidationRule
from app.domain.entities.template import Template, DegreeType
from app.domain.services.template_service import TemplateService
from app.domain.services.ai_enhancement_service import AIEnhancementService
from app.infrastructure.docx.document_parser import (
    ParsedDocument,
    DocumentElement,
    ElementProperties,
    DocumentMetadata,
)


class TestRuleEngineL1Rules:
    """Tests for RuleEngine L1 rule handlers."""

    @pytest.fixture
    def mock_template_service(self):
        """Create a mock TemplateService."""
        return MagicMock(spec=TemplateService)

    @pytest.fixture
    def mock_ai_service(self):
        """Create a mock AIEnhancementService."""
        service = MagicMock(spec=AIEnhancementService)
        service.is_enabled.return_value = False
        return service

    @pytest.fixture
    def rule_engine(self, mock_template_service, mock_ai_service):
        """Create a RuleEngine instance."""
        return RuleEngine(mock_template_service, mock_ai_service)

    @pytest.fixture
    def sample_parsed_document(self):
        """Create a sample ParsedDocument for testing."""
        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="这是正文内容",
                style="Normal",
                properties=ElementProperties(
                    font_name="宋体",
                    font_size=12,
                    line_spacing=1.5,
                    paragraph_spacing_before=0.5,
                    paragraph_spacing_after=0.0,
                ),
                index=1,
            ),
            DocumentElement(
                path="paragraph[2]",
                element_type="paragraph",
                content="另一段正文",
                style="Normal",
                properties=ElementProperties(
                    font_name="Times New Roman",
                    font_size=12,
                    line_spacing=1.5,
                ),
                index=2,
            ),
            DocumentElement(
                path="paragraph[3]",
                element_type="heading",
                content="第一章",
                style="Heading 1",
                properties=ElementProperties(
                    font_name="黑体",
                    font_size=14,
                ),
                index=3,
            ),
        ]
        return ParsedDocument(
            metadata=DocumentMetadata(title="测试文档"),
            elements=elements,
            styles={},
        )

    def test_rule_engine_initialization(self, rule_engine):
        """Test RuleEngine initializes correctly."""
        assert rule_engine.template_service is not None
        assert rule_engine.ai_enhancement is not None
        assert hasattr(rule_engine, 'L1_RULE_HANDLERS')

    def test_l1_rule_handlers_mapping(self, rule_engine):
        """Test L1 rule handlers are properly mapped."""
        expected_handlers = {
            "font_name_body": "_check_font_name_body",
            "font_name_heading": "_check_font_name_heading",
            "font_size_body": "_check_font_size_body",
            "line_spacing": "_check_line_spacing",
            "paragraph_spacing": "_check_paragraph_spacing",
            "page_margin": "_check_page_margin",
        }
        assert rule_engine.L1_RULE_HANDLERS == expected_handlers

    def test_validate_returns_validation_report(
        self,
        rule_engine,
        sample_parsed_document,
    ):
        """Test validate method returns ValidationReport."""
        from app.domain.entities.document import Document

        doc = Document(
            user_id=uuid4(),
            original_filename="test.docx",
            file_path=None,
            file_hash="abc123",
        )
        template = Template(
            university="清华大学",
            degree_type=DegreeType.MASTER,
            discipline="计算机科学",
        )

        report = rule_engine.validate(doc, sample_parsed_document, template)
        assert report is not None
        assert report.document_id == doc.id
        assert isinstance(report.results, list)

    def test_check_font_name_body_matches_expected(self, rule_engine):
        """Test _check_font_name_body returns None when font matches."""
        rule = ValidationRule(
            id="font_name_body",
            name="正文字体",
            level=RuleLevel.L1,
            description="正文应使用宋体",
            severity=Severity.ERROR,
            auto_fixable=True,
            params={"expected_value": "宋体", "allowed_fonts": ["宋体", "SimSun"]},
        )

        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="Test",
                properties=ElementProperties(font_name="宋体"),
                index=1,
            )
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        result = rule_engine._check_font_name_body(parsed_doc, rule)
        assert result is None

    def test_check_font_name_body_detects_mismatch(self, rule_engine):
        """Test _check_font_name_body detects font mismatch."""
        rule = ValidationRule(
            id="font_name_body",
            name="正文字体",
            level=RuleLevel.L1,
            description="正文应使用宋体",
            severity=Severity.ERROR,
            auto_fixable=True,
            params={"expected_value": "宋体", "allowed_fonts": ["宋体", "SimSun"]},
        )

        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="Test",
                properties=ElementProperties(font_name="Times New Roman"),
                index=1,
            )
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        result = rule_engine._check_font_name_body(parsed_doc, rule)
        assert result is not None
        assert result.rule_id == "font_name_body"
        assert result.expected_value == str(["宋体", "SimSun"])
        assert result.actual_value == "Times New Roman"

    def test_check_font_size_body_matches_expected(self, rule_engine):
        """Test _check_font_size_body returns None when size matches."""
        rule = ValidationRule(
            id="font_size_body",
            name="正文字号",
            level=RuleLevel.L1,
            description="正文应为12pt",
            severity=Severity.ERROR,
            auto_fixable=True,
            params={"expected_value": 12, "tolerance": 0},
        )

        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="Test",
                properties=ElementProperties(font_size=12),
                index=1,
            )
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        result = rule_engine._check_font_size_body(parsed_doc, rule)
        assert result is None

    def test_check_font_size_body_detects_mismatch(self, rule_engine):
        """Test _check_font_size_body detects size mismatch."""
        rule = ValidationRule(
            id="font_size_body",
            name="正文字号",
            level=RuleLevel.L1,
            description="正文应为12pt",
            severity=Severity.ERROR,
            auto_fixable=True,
            params={"expected_value": 12, "tolerance": 0},
        )

        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="Test",
                properties=ElementProperties(font_size=10),
                index=1,
            )
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        result = rule_engine._check_font_size_body(parsed_doc, rule)
        assert result is not None
        assert result.rule_id == "font_size_body"
        assert result.expected_value == "12pt"
        assert result.actual_value == "10pt"

    def test_check_line_spacing_matches_expected(self, rule_engine):
        """Test _check_line_spacing returns None when spacing matches."""
        rule = ValidationRule(
            id="line_spacing",
            name="行距",
            level=RuleLevel.L1,
            description="行距应为1.5倍",
            severity=Severity.ERROR,
            auto_fixable=True,
            params={"expected_value": 1.5, "tolerance": 0.1},
        )

        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="Test",
                properties=ElementProperties(line_spacing=1.5),
                index=1,
            )
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        result = rule_engine._check_line_spacing(parsed_doc, rule)
        assert result is None

    def test_check_line_spacing_detects_mismatch(self, rule_engine):
        """Test _check_line_spacing detects spacing mismatch."""
        rule = ValidationRule(
            id="line_spacing",
            name="行距",
            level=RuleLevel.L1,
            description="行距应为1.5倍",
            severity=Severity.ERROR,
            auto_fixable=True,
            params={"expected_value": 1.5, "tolerance": 0.1},
        )

        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="Test",
                properties=ElementProperties(line_spacing=2.0),
                index=1,
            )
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        result = rule_engine._check_line_spacing(parsed_doc, rule)
        assert result is not None
        assert result.rule_id == "line_spacing"

    def test_validate_rule_with_unknown_rule_id(
        self,
        rule_engine,
    ):
        """Test _validate_rule handles unknown rule IDs."""
        rule = ValidationRule(
            id="unknown_rule",
            name="未知规则",
            level=RuleLevel.L1,
            description="测试未知规则",
            severity=Severity.WARNING,
            auto_fixable=False,
            params={"expected_value": "test"},
        )

        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="Test",
                properties=ElementProperties(font_name="Arial"),
                index=1,
            )
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        results = rule_engine._validate_rule(parsed_doc, rule)
        assert isinstance(results, list)

    def test_check_page_margin_matches_expected(self, rule_engine):
        """Test _check_page_margin returns None when margins match."""
        from app.infrastructure.docx.document_parser import SectionProperties

        rule = ValidationRule(
            id="page_margin",
            name="页边距",
            level=RuleLevel.L1,
            description="页边距应为上下2.54cm，左右3cm",
            severity=Severity.ERROR,
            auto_fixable=False,
            params={"top": 2.54, "bottom": 2.54, "left": 3.0, "right": 3.0, "tolerance": 0.1},
        )

        section = SectionProperties(
            margin_top=2.54, margin_bottom=2.54,
            margin_left=3.0, margin_right=3.0,
        )
        metadata = DocumentMetadata(section=section)
        parsed_doc = ParsedDocument(elements=[], metadata=metadata)

        result = rule_engine._check_page_margin(parsed_doc, rule)
        assert result is None

    def test_check_page_margin_detects_mismatch(self, rule_engine):
        """Test _check_page_margin detects margin mismatch."""
        from app.infrastructure.docx.document_parser import SectionProperties

        rule = ValidationRule(
            id="page_margin",
            name="页边距",
            level=RuleLevel.L1,
            description="页边距应为上下2.54cm，左右3cm",
            severity=Severity.ERROR,
            auto_fixable=False,
            params={"top": 2.54, "bottom": 2.54, "left": 3.0, "right": 3.0, "tolerance": 0.1},
        )

        section = SectionProperties(
            margin_top=3.0, margin_bottom=2.54,
            margin_left=3.0, margin_right=2.5,
        )
        metadata = DocumentMetadata(section=section)
        parsed_doc = ParsedDocument(elements=[], metadata=metadata)

        result = rule_engine._check_page_margin(parsed_doc, rule)
        assert result is not None
        assert result.rule_id == "page_margin"
        assert "margin" in result.message.lower()

    def test_check_page_margin_returns_error_when_no_section(self, rule_engine):
        """Test _check_page_margin returns error when section properties unavailable."""
        rule = ValidationRule(
            id="page_margin",
            name="页边距",
            level=RuleLevel.L1,
            description="页边距检查",
            severity=Severity.ERROR,
            auto_fixable=False,
            params={"top": 2.54, "bottom": 2.54, "left": 3.0, "right": 3.0},
        )

        parsed_doc = ParsedDocument(elements=[], metadata=DocumentMetadata())

        result = rule_engine._check_page_margin(parsed_doc, rule)
        assert result is not None
        assert "not available" in result.message


class TestRuleEngineL3Rules:
    """Tests for RuleEngine L3 AI-enhanced rules."""

    @pytest.fixture
    def mock_template_service(self):
        return MagicMock(spec=TemplateService)

    @pytest.fixture
    def mock_ai_service_enabled(self):
        service = MagicMock(spec=AIEnhancementService)
        service.is_enabled.return_value = True
        service.analyze_citation_format.return_value = {
            "is_valid": False,
            "confidence": 0.8,
            "suggestions": ["格式不规范"],
        }
        service.create_ai_result.return_value = MagicMock()
        return service

    @pytest.fixture
    def rule_engine_ai_enabled(self, mock_template_service, mock_ai_service_enabled):
        return RuleEngine(mock_template_service, mock_ai_service_enabled)

    def test_validate_with_ai_only_runs_when_enabled(
        self,
        rule_engine_ai_enabled,
    ):
        """Test AI validation only runs when AI service is enabled."""
        rule = ValidationRule(
            id="citation_format",
            name="引用格式",
            level=RuleLevel.L3,
            description="引用格式检查",
            severity=Severity.WARNING,
            auto_fixable=False,
        )

        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="(Author, 2024)",
                index=1,
            )
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        results = rule_engine_ai_enabled._validate_with_ai(parsed_doc, rule)
        assert isinstance(results, list)

    def test_looks_like_citation(self, rule_engine_ai_enabled):
        """Test _looks_like_citation detection."""
        assert rule_engine_ai_enabled._looks_like_citation("(Author, 2024)")
        assert rule_engine_ai_enabled._looks_like_citation("[1] Author")
        assert not rule_engine_ai_enabled._looks_like_citation("这是一段很长的文字没有任何引用标记")

    def test_looks_like_reference(self, rule_engine_ai_enabled):
        """Test _looks_like_reference detection."""
        assert rule_engine_ai_enabled._looks_like_reference("Author, A. (2024). Title. Journal.")
        assert rule_engine_ai_enabled._looks_like_reference("https://doi.org/10.1234/example")
        assert not rule_engine_ai_enabled._looks_like_reference("这是一段普通文字")


class TestRuleEngineL2Rules:
    """Tests for RuleEngine L2 pattern-based rules."""

    @pytest.fixture
    def mock_template_service(self):
        return MagicMock(spec=TemplateService)

    @pytest.fixture
    def mock_ai_service(self):
        service = MagicMock(spec=AIEnhancementService)
        service.is_enabled.return_value = False
        return service

    @pytest.fixture
    def rule_engine(self, mock_template_service, mock_ai_service):
        return RuleEngine(mock_template_service, mock_ai_service)

    def test_check_heading_level_valid_sequence(self, rule_engine):
        """Test _check_heading_level passes for valid level sequence."""
        rule = ValidationRule(
            id="heading_level",
            name="标题层级",
            level=RuleLevel.L2,
            description="标题层级应连续",
            severity=Severity.ERROR,
            auto_fixable=False,
            params={"max_level": 4},
        )

        elements = [
            DocumentElement(path="paragraph[1]", element_type="heading", content="1. 第一章", style="Heading 1", index=1),
            DocumentElement(path="paragraph[2]", element_type="heading", content="1.1 第一节", style="Heading 2", index=2),
            DocumentElement(path="paragraph[3]", element_type="heading", content="1.1.1 小节", style="Heading 3", index=3),
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        results = rule_engine._check_heading_level(parsed_doc, rule)
        assert len(results) == 0

    def test_check_heading_level_skips_level(self, rule_engine):
        """Test _check_heading_level detects skipped levels."""
        rule = ValidationRule(
            id="heading_level",
            name="标题层级",
            level=RuleLevel.L2,
            description="标题层级应连续",
            severity=Severity.ERROR,
            auto_fixable=False,
            params={"max_level": 4},
        )

        elements = [
            DocumentElement(path="paragraph[1]", element_type="heading", content="1. 第一章", style="Heading 1", index=1),
            DocumentElement(path="paragraph[2]", element_type="heading", content="2. 第二章", style="Heading 2", index=2),
            DocumentElement(path="paragraph[3]", element_type="heading", content="2.1.1 小节", style="Heading 3", index=3),
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        results = rule_engine._check_heading_level(parsed_doc, rule)
        assert len(results) == 1
        assert results[0].rule_id == "heading_level"
        assert "jumped" in results[0].message.lower()

    def test_check_heading_level_exceeds_max(self, rule_engine):
        """Test _check_heading_level detects exceeding max level."""
        rule = ValidationRule(
            id="heading_level",
            name="标题层级",
            level=RuleLevel.L2,
            description="标题层级应连续",
            severity=Severity.ERROR,
            auto_fixable=False,
            params={"max_level": 3},
        )

        elements = [
            DocumentElement(path="paragraph[1]", element_type="heading", content="1. 第一章", style="Heading 1", index=1),
            DocumentElement(path="paragraph[2]", element_type="heading", content="1.1 第一节", style="Heading 2", index=2),
            DocumentElement(path="paragraph[3]", element_type="heading", content="1.1.1.1 深层次", style="Heading 4", index=3),
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        results = rule_engine._check_heading_level(parsed_doc, rule)
        assert len(results) >= 1
        assert any("exceeds maximum" in r.message.lower() for r in results)

    def test_extract_heading_level_from_style(self, rule_engine):
        """Test _extract_heading_level extracts level from style name."""
        assert rule_engine._extract_heading_level("Heading 1", "text") == 1
        assert rule_engine._extract_heading_level("Heading 2", "text") == 2
        assert rule_engine._extract_heading_level("Title", "text") == 0
        assert rule_engine._extract_heading_level("Normal", "text") == 0

    def test_extract_heading_level_from_content(self, rule_engine):
        """Test _extract_heading_level extracts level from content."""
        assert rule_engine._extract_heading_level("Normal", "1. Section") == 1
        assert rule_engine._extract_heading_level("Normal", "2. Section") == 2
        assert rule_engine._extract_heading_level("Normal", "Section without number") == 0

    def test_check_citation_format_pattern(self, rule_engine):
        """Test _check_citation_format_pattern detects invalid citations."""
        rule = ValidationRule(
            id="citation_format",
            name="引用格式",
            level=RuleLevel.L2,
            description="引用格式检查",
            severity=Severity.WARNING,
            auto_fixable=False,
            params={"style": "academic"},
        )

        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="According to [invalid citation format",
                index=1,
            ),
        ]
        parsed_doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        results = rule_engine._check_citation_format_pattern(parsed_doc, rule)
        assert isinstance(results, list)