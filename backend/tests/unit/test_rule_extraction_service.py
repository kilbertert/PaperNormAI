"""Unit tests for RuleExtractionService."""

import pytest
from unittest.mock import MagicMock, patch

from app.domain.services.rule_extraction_service import RuleExtractionService
from app.infrastructure.docling.document_model import DocumentModel, Paragraph, TextSegment, FontInfo


class TestRuleExtractionService:
    """Tests for RuleExtractionService."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock OpenAI provider."""
        provider = MagicMock()
        provider.is_configured.return_value = True
        provider._client = MagicMock()
        return provider

    @pytest.fixture
    def service(self, mock_provider):
        """Create RuleExtractionService with mock provider."""
        return RuleExtractionService(openai_provider=mock_provider)

    @pytest.fixture
    def sample_spec_doc(self):
        """Create a sample specification document."""
        return DocumentModel(
            paragraphs=[
                Paragraph(
                    text="论文格式规范手册",
                    segments=[
                        TextSegment(content="论文格式规范手册", font=FontInfo(name="宋体", size=16))
                    ],
                    style_name="Title"
                ),
                Paragraph(
                    text="第一章 字体规范",
                    segments=[
                        TextSegment(content="第一章 字体规范", font=FontInfo(name="黑体", size=16))
                    ],
                    style_name="Heading 1"
                ),
                Paragraph(
                    text="正文字体应为宋体，英文和数字应使用Times New Roman。",
                    segments=[
                        TextSegment(content="正文字体应为宋体，英文和数字应使用Times New Roman。", font=FontInfo(name="宋体", size=12))
                    ],
                    style_name="Normal"
                ),
            ]
        )

    def test_extract_rules_success(self, service, mock_provider):
        """Test successful rule extraction."""
        mock_response = """[font] 必须: 正文字体应为宋体，不应使用黑体或楷体
[font] 必须: 英文和数字应使用 Times New Roman 字体
[size] 必须: 正文字号应为小四号（约12pt）"""

        mock_provider._client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=mock_response))]
        )

        doc = DocumentModel(paragraphs=[
            Paragraph(text="Test content", segments=[TextSegment(content="Test", font=FontInfo())])
        ])

        rules = service.extract_rules(doc)

        assert len(rules) == 3
        assert rules[0]['category'] == 'font'
        assert rules[0]['priority'] == '必须'
        assert '宋体' in rules[0]['description']

    def test_extract_rules_empty_content(self, service):
        """Test extraction with empty document content."""
        doc = DocumentModel(paragraphs=[])
        rules = service.extract_rules(doc)
        assert rules == []

    def test_extract_rules_not_configured(self):
        """Test extraction when AI provider is not configured."""
        provider = MagicMock()
        provider.is_configured.return_value = False
        service = RuleExtractionService(openai_provider=provider)

        doc = DocumentModel(paragraphs=[
            Paragraph(text="Test", segments=[TextSegment(content="Test", font=FontInfo())])
        ])

        rules = service.extract_rules(doc)
        assert rules == []

    def test_parse_rules_valid_response(self, service):
        """Test parsing valid AI response."""
        response = """[font] 必须: 正文字体应为宋体
[font] 建议: 英文字体应使用Times New Roman
[size] 必须: 正文字号为12pt"""

        rules = service._parse_rules(response)

        assert len(rules) == 3
        assert rules[0]['category'] == 'font'
        assert rules[0]['priority'] == '必须'
        assert rules[1]['category'] == 'font'
        assert rules[1]['priority'] == '建议'

    def test_parse_rules_with_noise(self, service):
        """Test parsing response with noise lines."""
        response = """
        # 这是注释
        [font] 必须: 正文字体应为宋体

        示例输出：
        [font] 建议: 另一种规则
        ---
        """

        rules = service._parse_rules(response)

        assert len(rules) == 2
        assert rules[0]['category'] == 'font'
        assert rules[1]['category'] == 'font'

    def test_normalize_category(self, service):
        """Test category normalization."""
        assert service._normalize_category('font') == 'font'
        assert service._normalize_category('size') == 'font_size'
        assert service._normalize_category('spacing') == 'line_spacing'
        assert service._normalize_category('margin') == 'page_margin'
        assert service._normalize_category('heading') == 'heading'
        assert service._normalize_category('paragraph') == 'paragraph_spacing'
        assert service._normalize_category('unknown') == 'unknown'

    def test_get_text_content_used(self, service, mock_provider):
        """Test that document text content is used in prompt."""
        mock_provider._client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="[font] 必须: 测试"))]
        )

        doc = DocumentModel(paragraphs=[
            Paragraph(text="这是测试内容", segments=[TextSegment(content="这是测试内容", font=FontInfo())])
        ])

        service.extract_rules(doc)

        call_args = mock_provider._client.chat.completions.create.call_args
        prompt = call_args.kwargs['messages'][1]['content']
        assert '这是测试内容' in prompt
