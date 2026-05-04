"""Unit tests for SemanticValidationService."""

import pytest
from unittest.mock import MagicMock, patch

from app.domain.services.semantic_validation_service import SemanticValidationService
from app.domain.entities.validation_report import ValidationReport, ViolationSeverity
from app.infrastructure.docling.document_model import (
    DocumentModel, Paragraph, TextSegment, FontInfo,
    ParagraphFormat, PageFormat, LineSpacingType, Alignment
)


class TestSemanticValidationService:
    """Tests for SemanticValidationService."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock OpenAI provider."""
        provider = MagicMock()
        provider.is_configured.return_value = True
        provider._client = MagicMock()
        return provider

    @pytest.fixture
    def service(self, mock_provider):
        """Create SemanticValidationService with mock provider."""
        return SemanticValidationService(openai_provider=mock_provider)

    @pytest.fixture
    def sample_thesis_doc(self):
        """Create a sample thesis document."""
        return DocumentModel(
            paragraphs=[
                Paragraph(
                    text="第一章 研究背景",
                    segments=[TextSegment(content="第一章 研究背景", font=FontInfo(name="黑体", size=16, bold=True))],
                    paragraph_format=ParagraphFormat(line_spacing_type=LineSpacingType.DOUBLE),
                    style_name="Heading 1"
                ),
                Paragraph(
                    text="本文研究了相关问题。",
                    segments=[TextSegment(content="本文研究了相关问题。", font=FontInfo(name="宋体", size=12))],
                    paragraph_format=ParagraphFormat(
                        line_spacing_type=LineSpacingType.ONE_POINT_FIVE,
                        space_before=0,
                        space_after=6,
                        alignment=Alignment.JUSTIFY
                    ),
                    style_name="Normal"
                ),
            ],
            page_format=PageFormat(
                top_margin=72,
                bottom_margin=72,
                left_margin=72,
                right_margin=72,
                page_width=612,
                page_height=792
            )
        )

    @pytest.fixture
    def sample_rules(self):
        """Create sample rules list."""
        return [
            {'category': 'font', 'description': '正文字体应为宋体', 'priority': '必须'},
            {'category': 'font_size', 'description': '正文字号应为12pt', 'priority': '必须'},
            {'category': 'line_spacing', 'description': '正文行距为1.5倍行距', 'priority': '必须'},
        ]

    def test_validate_returns_validation_report(self, service, mock_provider):
        """Test that validate returns a ValidationReport."""
        mock_provider._client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="[校验结果]\n未发现格式违规，论文格式符合规范要求。"))]
        )

        report = service.validate(self.sample_thesis_doc, self.sample_rules, "test.docx", "spec.docx")

        assert isinstance(report, ValidationReport)
        assert report.document_name == "test.docx"
        assert report.template_name == "spec.docx"

    def test_validate_no_violations(self, service, mock_provider):
        """Test validation with no violations found."""
        mock_provider._client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="[校验结果]\n未发现格式违规，论文格式符合规范要求。"))]
        )

        report = service.validate(self.sample_thesis_doc, self.sample_rules, "test.docx")

        assert report.get_violation_count() == 0

    def test_validate_with_violations(self, service, mock_provider):
        """Test validation with violations found."""
        mock_response = """[违规]
段落: 1
原始内容: "黑体"
违规规则: 正文字体应为宋体
违规类型: font
严重程度: ERROR（必须修正）
修正建议: 改为宋体

[违规]
段落: 2
原始内容: "1.5倍"
违规规则: 正文字号应为12pt
违规类型: font_size
严重程度: WARNING（建议修正）
修正建议: 调整为12pt"""

        mock_provider._client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=mock_response))]
        )

        report = service.validate(self.sample_thesis_doc, self.sample_rules, "test.docx")

        assert report.get_violation_count() >= 1

    def test_validate_not_configured(self, service):
        """Test validation when AI provider is not configured."""
        provider = MagicMock()
        provider.is_configured.return_value = False
        service = SemanticValidationService(openai_provider=provider)

        report = service.validate(self.sample_thesis_doc, self.sample_rules, "test.docx")

        # Should return empty report
        assert report.get_violation_count() == 0

    def test_format_rules(self, service, sample_rules):
        """Test rules formatting for prompt."""
        formatted = service._format_rules(sample_rules)

        assert 'font' in formatted
        assert '正文字体应为宋体' in formatted
        assert '必须' in formatted

    def test_format_rules_empty(self, service):
        """Test formatting empty rules list."""
        formatted = service._format_rules([])
        assert '（无明确规则）' in formatted

    def test_format_paragraphs(self, service, sample_thesis_doc):
        """Test paragraph formatting for prompt."""
        formatted = service._format_paragraphs(sample_thesis_doc)

        assert '段落0' in formatted or '段落1' in formatted
        assert '第一章 研究背景' in formatted
        assert '宋体' in formatted or '黑体' in formatted
        assert 'line_spacing' in formatted

    def test_normalize_category(self, service):
        """Test category normalization."""
        from app.domain.entities.validation_report import ViolationCategory

        assert service._normalize_category('font') == ViolationCategory.FONT
        assert service._normalize_category('font_size') == ViolationCategory.FONT_SIZE
        assert service._normalize_category('size') == ViolationCategory.FONT_SIZE
        assert service._normalize_category('line_spacing') == ViolationCategory.LINE_SPACING
        assert service._normalize_category('spacing') == ViolationCategory.LINE_SPACING
        assert service._normalize_category('paragraph_spacing') == ViolationCategory.PARAGRAPH_SPACING
        assert service._normalize_category('page_margin') == ViolationCategory.PAGE_MARGIN
        assert service._normalize_category('heading') == ViolationCategory.HEADING

    def test_validate_paragraph_info_in_prompt(self, service, mock_provider, sample_thesis_doc, sample_rules):
        """Test that paragraph info is included in the prompt."""
        mock_provider._client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="[校验结果]\n未发现格式违规。"))]
        )

        service.validate(sample_thesis_doc, sample_rules, "test.docx")

        call_args = mock_provider._client.chat.completions.create.call_args
        prompt = call_args.kwargs['messages'][1]['content']

        assert '第一章 研究背景' in prompt
        assert '宋体' in prompt or '黑体' in prompt
        assert '页宽' in prompt
        assert '上边距' in prompt

    def test_validate_page_info_in_prompt(self, service, mock_provider, sample_thesis_doc, sample_rules):
        """Test that page format info is included in the prompt."""
        mock_provider._client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="[校验结果]\n未发现格式违规。"))]
        )

        service.validate(sample_thesis_doc, sample_rules, "test.docx")

        call_args = mock_provider._client.chat.completions.create.call_args
        prompt = call_args.kwargs['messages'][1]['content']

        assert '612' in prompt  # page_width
        assert '792' in prompt  # page_height
        assert '72' in prompt   # margins
