"""Document parser for .docx files.

Converts .docx files into the intermediate ParsedDocument model,
isolating business logic from python-docx dependencies.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Iterator
from datetime import datetime

try:
    import docx
    from docx.document import Document as DocxDocument
    from docx.text.paragraph import Paragraph
    from docx.text.run import Run
    from docx.enum.style import WD_STYLE_TYPE
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


@dataclass
class SectionProperties:
    """Page section properties (margins, orientation, etc.)."""
    page_width: Optional[float] = None  # in cm
    page_height: Optional[float] = None  # in cm
    margin_top: Optional[float] = None
    margin_bottom: Optional[float] = None
    margin_left: Optional[float] = None
    margin_right: Optional[float] = None
    orientation: Optional[str] = None  # portrait / landscape


@dataclass
class DocumentMetadata:
    """Metadata extracted from a document."""
    title: Optional[str] = None
    author: Optional[str] = None
    word_count: int = 0
    page_count: int = 0
    section: Optional[SectionProperties] = None


@dataclass
class ElementProperties:
    """Properties of a document element."""
    font_name: Optional[str] = None
    font_size: Optional[int] = None
    font_bold: bool = False
    font_italic: bool = False
    line_spacing: Optional[float] = None
    line_spacing_rule: Optional[str] = None  # 'multiple', 'fixed', 'at_least'
    paragraph_spacing_before: Optional[float] = None
    paragraph_spacing_after: Optional[float] = None
    alignment: Optional[str] = None


@dataclass
class DocumentElement:
    """A single element in a parsed document."""
    path: str
    element_type: str  # paragraph, heading, table, etc.
    content: str
    style: Optional[str] = None
    properties: ElementProperties = field(default_factory=ElementProperties)
    index: int = 0


@dataclass
class ParsedDocument:
    """Intermediate document model for business logic.

    This model isolates rule engine and correction logic from
    python-docx raw objects.
    """
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    elements: List[DocumentElement] = field(default_factory=list)
    styles: Dict[str, dict] = field(default_factory=dict)
    parsed_at: datetime = field(default_factory=datetime.utcnow)
    parser_version: str = "0.1.0"


class DocumentParser:
    """Parser that converts .docx to ParsedDocument."""

    def __init__(self):
        self._element_index = 0

    def parse(self, file_path: Path) -> ParsedDocument:
        """Parse a .docx file into ParsedDocument.

        Args:
            file_path: Path to the .docx file

        Returns:
            ParsedDocument containing all elements

        Raises:
            RuntimeError: If python-docx is not installed
        """
        if not DOCX_AVAILABLE:
            raise RuntimeError(
                "python-docx is not installed. Install it with: pip install python-docx"
            )

        doc = docx.Document(str(file_path))
        self._element_index = 0

        elements = []
        elements.extend(self._parse_paragraphs(doc))
        elements.extend(self._parse_tables(doc))

        styles = self._extract_styles(doc)
        section_props = self._extract_section_properties(doc)

        metadata = DocumentMetadata(
            title=self._extract_title(doc),
            author=self._extract_author(doc),
            word_count=self._count_words(doc),
            page_count=self._estimate_page_count(doc),
            section=section_props,
        )

        return ParsedDocument(
            metadata=metadata,
            elements=elements,
            styles=styles,
            parsed_at=datetime.utcnow(),
            parser_version="0.1.0",
        )

    def _parse_paragraphs(self, doc: DocxDocument) -> List[DocumentElement]:
        """Parse all paragraphs from the document."""
        elements = []
        for para in doc.paragraphs:
            element = self._parse_paragraph(para)
            if element:
                elements.append(element)
        return elements

    def _parse_paragraph(self, para: Paragraph) -> Optional[DocumentElement]:
        """Parse a single paragraph element."""
        content = para.text.strip()
        if not content:
            return None

        self._element_index += 1
        path = f"paragraph[{self._element_index}]"

        style_name = para.style.name if para.style else None

        properties = ElementProperties(
            font_name=self._get_run_font_name(para),
            font_size=self._get_run_font_size(para),
            font_bold=self._is_bold(para),
            font_italic=self._is_italic(para),
            line_spacing=self._get_line_spacing(para),
            line_spacing_rule=self._get_line_spacing_rule(para),
            paragraph_spacing_before=self._get_spacing_before(para),
            paragraph_spacing_after=self._get_spacing_after(para),
            alignment=self._get_alignment(para),
        )

        element_type = self._determine_element_type(style_name, content)

        return DocumentElement(
            path=path,
            element_type=element_type,
            content=content,
            style=style_name,
            properties=properties,
            index=self._element_index,
        )

    def _parse_tables(self, doc: DocxDocument) -> List[DocumentElement]:
        """Parse all tables from the document."""
        elements = []
        for table_index, table in enumerate(doc.tables):
            self._element_index += 1
            path = f"table[{table_index}]"
            rows = len(table.rows)
            cols = len(table.columns) if rows > 0 else 0
            content = f"Table: {rows} rows x {cols} cols"

            elements.append(DocumentElement(
                path=path,
                element_type="table",
                content=content,
                style=None,
                properties=ElementProperties(),
                index=self._element_index,
            ))
        return elements

    def _get_run_font_name(self, para: Paragraph) -> Optional[str]:
        """Get font name from first run with font info."""
        for run in para.runs:
            if run.font and run.font.name:
                return run.font.name
        return None

    def _get_run_font_size(self, para: Paragraph) -> Optional[int]:
        """Get font size (in pt) from first run with font info."""
        for run in para.runs:
            if run.font and run.font.size:
                return int(run.font.size.pt)
        return None

    def _is_bold(self, para: Paragraph) -> bool:
        """Check if paragraph has bold text."""
        for run in para.runs:
            if run.font and run.font.bold:
                return True
        return False

    def _is_italic(self, para: Paragraph) -> bool:
        """Check if paragraph has italic text."""
        for run in para.runs:
            if run.font and run.font.italic:
                return True
        return False

    def _get_line_spacing(self, para: Paragraph) -> Optional[float]:
        """Get line spacing value (either multiplier or fixed pt value).

        Returns:
            - Multiplier value (e.g., 1.5) for MULTIPLE/ONE_POINT_FIVE spacing
            - Fixed pt value (e.g., 23) for EXACTLY spacing
            - None if no line spacing is set
        """
        # Check direct paragraph format first
        if para.paragraph_format:
            pf = para.paragraph_format
            if pf.line_spacing is not None and pf.line_spacing > 0:
                return float(pf.line_spacing)

        # Fall back to style's paragraph format
        if para.style and para.style.paragraph_format:
            style_pf = para.style.paragraph_format
            if style_pf.line_spacing is not None and style_pf.line_spacing > 0:
                return float(style_pf.line_spacing)

        return None

    def _get_line_spacing_rule(self, para: Paragraph) -> Optional[str]:
        """Get line spacing rule type.

        Returns:
            - 'multiple' for MULTIPLE, ONE_POINT_FIVE, SINGLE, DOUBLE
            - 'fixed' for EXACTLY
            - 'at_least' for AT_LEAST
            - None if no rule is set
        """
        from docx.enum.text import WD_LINE_SPACING

        # Check direct paragraph format first
        if para.paragraph_format and para.paragraph_format.line_spacing_rule is not None:
            rule = para.paragraph_format.line_spacing_rule
            if rule == WD_LINE_SPACING.EXACTLY:
                return 'fixed'
            elif rule in (WD_LINE_SPACING.MULTIPLE, WD_LINE_SPACING.ONE_POINT_FIVE,
                          WD_LINE_SPACING.SINGLE, WD_LINE_SPACING.DOUBLE):
                return 'multiple'
            elif rule == WD_LINE_SPACING.AT_LEAST:
                return 'at_least'

        # Fall back to style's paragraph format
        if para.style and para.style.paragraph_format:
            style_pf = para.style.paragraph_format
            if style_pf.line_spacing_rule is not None:
                rule = style_pf.line_spacing_rule
                if rule == WD_LINE_SPACING.EXACTLY:
                    return 'fixed'
                elif rule in (WD_LINE_SPACING.MULTIPLE, WD_LINE_SPACING.ONE_POINT_FIVE,
                              WD_LINE_SPACING.SINGLE, WD_LINE_SPACING.DOUBLE):
                    return 'multiple'
                elif rule == WD_LINE_SPACING.AT_LEAST:
                    return 'at_least'

        return None

    def _get_spacing_before(self, para: Paragraph) -> Optional[float]:
        """Get spacing before in lines."""
        if para.paragraph_format and para.paragraph_format.space_before:
            return float(para.paragraph_format.space_before)
        return None

    def _get_spacing_after(self, para: Paragraph) -> Optional[float]:
        """Get spacing after in lines."""
        if para.paragraph_format and para.paragraph_format.space_after:
            return float(para.paragraph_format.space_after)
        return None

    def _get_alignment(self, para: Paragraph) -> Optional[str]:
        """Get paragraph alignment."""
        if para.paragraph_format and para.paragraph_format.alignment:
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            alignment_map = {
                WD_ALIGN_PARAGRAPH.LEFT: "left",
                WD_ALIGN_PARAGRAPH.CENTER: "center",
                WD_ALIGN_PARAGRAPH.RIGHT: "right",
                WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
            }
            return alignment_map.get(para.paragraph_format.alignment)
        return None

    def _determine_element_type(self, style_name: Optional[str], content: str) -> str:
        """Determine element type based on style and content."""
        if style_name:
            style_lower = style_name.lower()
            if "heading" in style_lower or "title" in style_lower or "toc" in style_lower:
                return "heading"
        if content.startswith("Table:") or content.startswith("表格"):
            return "table"
        return "paragraph"

    def _extract_styles(self, doc: DocxDocument) -> Dict[str, dict]:
        """Extract document styles."""
        styles = {}
        for style in doc.styles:
            if style.type == WD_STYLE_TYPE.PARAGRAPH:
                styles[style.name] = {
                    "type": "paragraph",
                    "name": style.name,
                    "font_name": style.font.name if style.font else None,
                    "font_size": style.font.size.pt if style.font and style.font.size else None,
                }
        return styles

    def _extract_title(self, doc: DocxDocument) -> Optional[str]:
        """Extract document title."""
        if doc.core_properties.title:
            return doc.core_properties.title
        for para in doc.paragraphs[:5]:
            if para.style and "title" in para.style.name.lower():
                return para.text
        return None

    def _extract_author(self, doc: DocxDocument) -> Optional[str]:
        """Extract document author."""
        return doc.core_properties.author if hasattr(doc.core_properties, 'author') else None

    def _extract_section_properties(self, doc: DocxDocument) -> Optional[SectionProperties]:
        """Extract page section properties (margins, page size, etc.).

        python-docx provides access to section properties via doc.sections.
        """
        try:
            if not doc.sections:
                return None

            section = doc.sections[0]
            section_props = SectionProperties()

            from docx.shared import Inches, Cm, Mm

            def pt_to_cm(pt_val):
                """Convert points to centimeters."""
                return pt_val * 2.54 / 72 if pt_val else None

            if section.page_width and section.page_height:
                section_props.page_width = pt_to_cm(section.page_width.pt)
                section_props.page_height = pt_to_cm(section.page_height.pt)

                if section.page_width.pt > section.page_height.pt:
                    section_props.orientation = "landscape"
                else:
                    section_props.orientation = "portrait"

            if hasattr(section, 'top_margin') and section.top_margin:
                section_props.margin_top = pt_to_cm(section.top_margin.pt)

            if hasattr(section, 'bottom_margin') and section.bottom_margin:
                section_props.margin_bottom = pt_to_cm(section.bottom_margin.pt)

            if hasattr(section, 'left_margin') and section.left_margin:
                section_props.margin_left = pt_to_cm(section.left_margin.pt)

            if hasattr(section, 'right_margin') and section.right_margin:
                section_props.margin_right = pt_to_cm(section.right_margin.pt)

            return section_props

        except Exception as e:
            print(f"Failed to extract section properties: {e}")
            return None

    def _count_words(self, doc: DocxDocument) -> int:
        """Count words in document."""
        count = 0
        for para in doc.paragraphs:
            count += len(para.text.split())
        return count

    def _estimate_page_count(self, doc: DocxDocument) -> int:
        """Estimate page count based on word count."""
        words = self._count_words(doc)
        return max(1, words // 300)