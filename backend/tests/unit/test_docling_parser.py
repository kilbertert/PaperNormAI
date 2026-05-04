"""Tests for DoclingDocumentParser."""
import pytest
from pathlib import Path

from backend.app.infrastructure.docling import (
    DoclingDocumentParser,
    DocumentModel,
    FontInfo,
    Paragraph,
    ParagraphFormat,
    PageFormat,
    StructureItem,
)


@pytest.fixture
def parser():
    """Create a parser instance."""
    return DoclingDocumentParser()


@pytest.fixture
def sample_docx_path():
    """Path to a sample docx file for testing."""
    # Use the test_line_spacing.docx which is a smaller test file
    path = Path("D:/AI/project/PaperNormAI/test_line_spacing.docx")
    if path.exists():
        return path

    # Try alternative paths
    alt_paths = [
        Path("D:/AI/project/PaperNormAI/temp.docx"),
        Path("D:/AI/project/PaperNormAI/(学生版)关于学生做好毕业设计、实习后期工作的通知(3).docx"),
    ]
    for p in alt_paths:
        if p.exists():
            return p

    pytest.skip("No sample docx file found")


class TestDoclingDocumentParser:
    """Tests for DoclingDocumentParser class."""

    def test_parser_initialization(self, parser):
        """Test that parser initializes correctly."""
        assert parser is not None
        assert parser.validate is True

    def test_parse_returns_document_model(self, parser, sample_docx_path):
        """Test that parse() returns a DocumentModel instance."""
        result = parser.parse(sample_docx_path)
        assert isinstance(result, DocumentModel)

    def test_parse_contains_paragraphs(self, parser, sample_docx_path):
        """Test that parsed document contains paragraphs."""
        result = parser.parse(sample_docx_path)
        assert isinstance(result.paragraphs, list)
        # At least some paragraphs should be extracted
        assert len(result.paragraphs) > 0

    def test_parse_page_format(self, parser, sample_docx_path):
        """Test that page format is extracted."""
        result = parser.parse(sample_docx_path)
        assert isinstance(result.page_format, PageFormat)
        # Check that page format has reasonable values
        assert result.page_format.page_width > 0
        assert result.page_format.page_height > 0

    def test_parse_structure(self, parser, sample_docx_path):
        """Test that document structure is extracted."""
        result = parser.parse(sample_docx_path)
        assert hasattr(result, "structure")
        assert isinstance(result.structure.sections, list)

    def test_paragraph_has_text(self, parser, sample_docx_path):
        """Test that paragraphs contain text content."""
        result = parser.parse(sample_docx_path)
        for para in result.paragraphs:
            assert isinstance(para, Paragraph)
            assert para.text is not None
            assert len(para.text) > 0

    def test_paragraph_format_defaults(self):
        """Test ParagraphFormat default values."""
        pf = ParagraphFormat()
        assert pf.space_before == 0.0
        assert pf.space_after == 0.0
        assert pf.left_indent == 0.0
        assert pf.right_indent == 0.0

    def test_font_info_defaults(self):
        """Test FontInfo default values."""
        fi = FontInfo()
        assert fi.name == "Calibri"
        assert fi.size == 11.0
        assert fi.bold is False
        assert fi.italic is False

    def test_page_format_defaults(self):
        """Test PageFormat default values (in points)."""
        pf = PageFormat()
        assert pf.top_margin == 72.0  # 1 inch
        assert pf.bottom_margin == 72.0
        assert pf.left_margin == 72.0
        assert pf.right_margin == 72.0

    def test_document_model_text_content(self, parser, sample_docx_path):
        """Test get_text_content() method."""
        result = parser.parse(sample_docx_path)
        text = result.get_text_content()
        assert isinstance(text, str)
        assert len(text) > 0

    def test_file_not_found_raises(self, parser):
        """Test that non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parser.parse(Path("nonexistent_file.docx"))

    def test_wrong_extension_raises(self, parser):
        """Test that wrong file extension raises ValueError."""
        # Create a temp file with wrong extension
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Expected .docx"):
                parser.parse(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)


class TestDocumentModel:
    """Tests for DocumentModel class."""

    def test_empty_document_model(self):
        """Test creating an empty DocumentModel."""
        model = DocumentModel()
        assert model.paragraphs == []
        assert model.structure is not None

    def test_get_paragraph_count(self):
        """Test get_paragraph_count() method."""
        model = DocumentModel()
        assert model.get_paragraph_count() == 0

        model.paragraphs = [
            Paragraph(text="First"),
            Paragraph(text="Second"),
        ]
        assert model.get_paragraph_count() == 2

    def test_get_section_titles(self):
        """Test get_section_titles() method."""
        model = DocumentModel()
        model.structure.sections = [
            StructureItem(title="Chapter 1", level=1),
            StructureItem(title="Section 1.1", level=2),
        ]
        assert model.get_section_titles() == ["Chapter 1", "Section 1.1"]