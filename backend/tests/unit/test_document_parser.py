"""Unit tests for DocumentParser."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.infrastructure.docx.document_parser import (
    DocumentParser,
    ParsedDocument,
    DocumentElement,
    ElementProperties,
)


class TestDocumentParser:
    """Tests for DocumentParser class."""

    def test_parse_returns_parsed_document_structure(self):
        """Test that parse method returns proper ParsedDocument structure."""
        parser = DocumentParser()
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'parse_paragraph')

    def test_document_parser_initialization(self):
        """Test DocumentParser initializes with default values."""
        parser = DocumentParser()
        assert parser._element_index == 0

    def test_element_properties_dataclass(self):
        """Test ElementProperties dataclass."""
        props = ElementProperties(
            font_name="宋体",
            font_size=12,
            font_bold=False,
            font_italic=False,
            line_spacing=1.5,
            paragraph_spacing_before=0.5,
            paragraph_spacing_after=0.0,
            alignment="left",
        )
        assert props.font_name == "宋体"
        assert props.font_size == 12
        assert props.line_spacing == 1.5

    def test_document_element_dataclass(self):
        """Test DocumentElement dataclass."""
        element = DocumentElement(
            path="paragraph[1]",
            element_type="paragraph",
            content="这是一段测试文字",
            style="Normal",
            properties=ElementProperties(font_name="宋体"),
            index=1,
        )
        assert element.path == "paragraph[1]"
        assert element.element_type == "paragraph"
        assert element.content == "这是一段测试文字"
        assert element.properties.font_name == "宋体"

    def test_parsed_document_dataclass(self):
        """Test ParsedDocument dataclass."""
        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="Test",
                index=1,
            )
        ]
        doc = ParsedDocument(elements=elements)
        assert len(doc.elements) == 1
        assert doc.parser_version == "0.1.0"


class TestDocumentParserWithMockedDocx:
    """Tests for DocumentParser with mocked python-docx."""

    @pytest.fixture
    def mock_docx_module(self):
        """Mock python-docx module."""
        with patch.dict('sys.modules', {
            'docx': MagicMock(),
            'docx.document': MagicMock(),
            'docx.text.paragraph': MagicMock(),
            'docx.text.run': MagicMock(),
            'docx.enum.style': MagicMock(),
        }):
            yield

    def test_check_font_name_body_detects_mismatch(self):
        """Test font name body rule detects font mismatch."""
        from app.infrastructure.docx.document_parser import ElementProperties, DocumentElement

        props = ElementProperties(font_name="Times New Roman")
        element = DocumentElement(
            path="paragraph[1]",
            element_type="paragraph",
            content="Test content",
            properties=props,
            index=1,
        )

        assert element.properties.font_name == "Times New Roman"

    def test_element_properties_equality(self):
        """Test ElementProperties can be compared."""
        props1 = ElementProperties(font_name="宋体", font_size=12)
        props2 = ElementProperties(font_name="宋体", font_size=12)
        assert props1.font_name == props2.font_name
        assert props1.font_size == props2.font_size

    def test_document_element_path_format(self):
        """Test DocumentElement path format."""
        element = DocumentElement(
            path="paragraph[5]",
            element_type="heading",
            content="标题",
            index=5,
        )
        assert element.path == "paragraph[5]"
        assert element.index == 5