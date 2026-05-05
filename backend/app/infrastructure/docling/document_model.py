"""Document model for holding parsed document content."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Alignment(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


class LineSpacingType(Enum):
    SINGLE = "single"
    ONE_POINT_FIVE = "one_point_five"
    DOUBLE = "double"
    EXACT = "exact"
    MULTIPLE = "multiple"


@dataclass
class FontInfo:
    """Font information for a text segment."""
    name: str = "Calibri"
    size: float = 11.0  # points
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: Optional[str] = None  # hex color like "#000000"


@dataclass
class ParagraphFormat:
    """Paragraph formatting information."""
    line_spacing_type: LineSpacingType = LineSpacingType.SINGLE
    line_spacing_value: Optional[float] = None  # exact value or multiple
    space_before: float = 0.0  # points
    space_after: float = 0.0  # points
    alignment: Alignment = Alignment.LEFT
    first_line_indent: float = 0.0  # points
    left_indent: float = 0.0  # points
    right_indent: float = 0.0  # points


@dataclass
class PageFormat:
    """Page layout information."""
    top_margin: float = 72.0  # points (1 inch default)
    bottom_margin: float = 72.0
    left_margin: float = 72.0
    right_margin: float = 72.0
    page_width: float = 612.0  # points (Letter size default)
    page_height: float = 792.0


@dataclass
class TextSegment:
    """A text segment within a paragraph with its font info."""
    content: str
    font: FontInfo = field(default_factory=FontInfo)


@dataclass
class Paragraph:
    """A paragraph with its content and formatting."""
    text: str  # combined text content
    segments: list[TextSegment] = field(default_factory=list)
    paragraph_format: ParagraphFormat = field(default_factory=ParagraphFormat)
    style_name: Optional[str] = None  # e.g., "Normal", "Heading 1"


@dataclass
class StructureItem:
    """A structural element like a chapter or section title."""
    title: str
    level: int = 1  # 1 = top-level chapter, 2 = section, etc.
    paragraph_index: int = 0  # index into paragraphs list


@dataclass
class DocumentStructure:
    """Document structure information."""
    title: Optional[str] = None
    authors: list[str] = field(default_factory=list)
    sections: list[StructureItem] = field(default_factory=list)


@dataclass
class TableInfo:
    """Table information extracted from a document."""
    rows: int = 0
    cols: int = 0
    caption: Optional[str] = None
    style: Optional[str] = None  # e.g., "table", "grid"


@dataclass
class FigureInfo:
    """Figure/image information extracted from a document."""
    width: float = 0.0  # pixels
    height: float = 0.0  # pixels
    caption: Optional[str] = None


@dataclass
class FormulaInfo:
    """Formula information extracted from a document."""
    content: str = ""
    numbered: bool = False
    number: Optional[str] = None  # e.g., "(1)", "(2)"


@dataclass
class DocumentModel:
    """
    Unified document model holding parsed document content.
    This is the intermediate representation used by downstream AI processing.
    """
    paragraphs: list[Paragraph] = field(default_factory=list)
    font_info: list[FontInfo] = field(default_factory=list)
    paragraph_format: list[ParagraphFormat] = field(default_factory=list)
    page_format: PageFormat = field(default_factory=PageFormat)
    structure: DocumentStructure = field(default_factory=DocumentStructure)
    tables: list[TableInfo] = field(default_factory=list)
    figures: list[FigureInfo] = field(default_factory=list)
    formulas: list[FormulaInfo] = field(default_factory=list)

    def get_text_content(self) -> str:
        """Extract all text content as a single string."""
        return "\n".join(p.text for p in self.paragraphs)

    def get_paragraph_count(self) -> int:
        return len(self.paragraphs)

    def get_section_titles(self) -> list[str]:
        """Get all section titles in order."""
        return [s.title for s in self.structure.sections]