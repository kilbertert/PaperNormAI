"""Docling-based document parser for PaperNormAI."""
from pathlib import Path
from typing import Optional

from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import Document, JsonAnnotation
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from .document_model import (
    Alignment,
    DocumentModel,
    DocumentStructure,
    FontInfo,
    LineSpacingType,
    PageFormat,
    Paragraph,
    ParagraphFormat,
    StructureItem,
    TextSegment,
)


class DoclingDocumentParser:
    """
    Parser that uses docling to extract content from .docx files.

    Args:
        validate: Whether to validate the output structure
    """

    def __init__(self, validate: bool = True):
        self.validate = validate
        self._converter: Optional[DocumentConverter] = None

    def _get_converter(self) -> DocumentConverter:
        """Lazy initialization of the docling converter."""
        if self._converter is None:
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = False
            pipeline_options.do_table_structure = False

            format_options = {
                InputFormat.DOCX: PdfFormatOption(
                    pipeline_options=pipeline_options,
                    validate_document=self.validate,
                )
            }
            self._converter = DocumentConverter(format_options=format_options)
        return self._converter

    def parse(self, file_path: Path) -> DocumentModel:
        """
        Parse a .docx file and return a DocumentModel.

        Args:
            file_path: Path to the .docx file

        Returns:
            DocumentModel containing parsed document content

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if file_path.suffix.lower() != ".docx":
            raise ValueError(f"Expected .docx file, got: {file_path.suffix}")

        try:
            converter = self._get_converter()
            result = converter.convert(str(file_path))
            return self._convert_to_document_model(result.document)
        except Exception as e:
            raise ValueError(f"Failed to parse document: {e}") from e

    def _convert_to_document_model(self, docling_doc: Document) -> DocumentModel:
        """Convert docling Document to our DocumentModel."""
        model = DocumentModel()

        # Extract page format from document metadata
        if docling_doc.metadata:
            page_format = self._extract_page_format(docling_doc.metadata)
            model.page_format = page_format

        # Process elements to extract paragraphs and structure
        paragraphs: list[Paragraph] = []
        sections: list[StructureItem] = []
        paragraph_index = 0

        if hasattr(docling_doc, "elements") and docling_doc.elements:
            for element in docling_doc.elements:
                element_type = type(element).__name__

                # Handle text elements
                if hasattr(element, "text") and element.text:
                    text = element.text.strip()
                    if not text:
                        continue

                    # Determine if this is a heading based on style or content patterns
                    is_heading = self._is_heading_element(element)

                    if is_heading:
                        level = self._extract_heading_level(element)
                        sections.append(
                            StructureItem(
                                title=text,
                                level=level,
                                paragraph_index=paragraph_index,
                            )
                        )
                    else:
                        # Extract font info from element
                        font_info = self._extract_font_info(element)

                        # Create paragraph
                        para_format = self._extract_paragraph_format(element)
                        segments = [TextSegment(content=text, font=font_info)]
                        paragraph = Paragraph(
                            text=text,
                            segments=segments,
                            paragraph_format=para_format,
                            style_name=self._extract_style_name(element),
                        )
                        paragraphs.append(paragraph)
                        paragraph_index += 1

        model.paragraphs = paragraphs
        model.structure = DocumentStructure(sections=sections)

        # Extract document title if available
        if docling_doc.metadata and hasattr(docling_doc.metadata, "title"):
            model.structure.title = docling_doc.metadata.title

        return model

    def _extract_page_format(self, metadata) -> PageFormat:
        """Extract page format from docling metadata."""
        page_format = PageFormat()

        if hasattr(metadata, "page_width") and metadata.page_width:
            page_format.page_width = float(metadata.page_width)
        if hasattr(metadata, "page_height") and metadata.page_height:
            page_format.page_height = float(metadata.page_height)
        if hasattr(metadata, "margin_top") and metadata.margin_top:
            page_format.top_margin = float(metadata.margin_top)
        if hasattr(metadata, "margin_bottom") and metadata.margin_bottom:
            page_format.bottom_margin = float(metadata.margin_bottom)
        if hasattr(metadata, "margin_left") and metadata.margin_left:
            page_format.left_margin = float(metadata.margin_left)
        if hasattr(metadata, "margin_right") and metadata.margin_right:
            page_format.right_margin = float(metadata.margin_right)

        return page_format

    def _is_heading_element(self, element) -> bool:
        """Check if an element is a heading based on its properties."""
        # Check for explicit heading properties
        if hasattr(element, "type"):
            element_str = str(element.type).lower()
            if "heading" in element_str or "title" in element_str:
                return True

        # Check style name
        if hasattr(element, "properties"):
            props = element.properties
            if isinstance(props, dict):
                if props.get("style") and "heading" in str(props.get("style")).lower():
                    return True

        return False

    def _extract_heading_level(self, element) -> int:
        """Extract heading level from element."""
        if hasattr(element, "level"):
            return int(element.level)

        if hasattr(element, "properties"):
            props = element.properties
            if isinstance(props, dict):
                level = props.get("level")
                if level:
                    return int(level)

        # Try to infer from style name
        style_name = self._extract_style_name(element)
        if style_name:
            style_lower = style_name.lower()
            if "heading 1" in style_lower or "title" in style_lower:
                return 1
            elif "heading 2" in style_lower:
                return 2
            elif "heading 3" in style_lower:
                return 3

        return 1

    def _extract_style_name(self, element) -> Optional[str]:
        """Extract style name from element."""
        if hasattr(element, "style"):
            return str(element.style) if element.style else None

        if hasattr(element, "properties"):
            props = element.properties
            if isinstance(props, dict):
                return props.get("style")

        return None

    def _extract_font_info(self, element) -> FontInfo:
        """Extract font information from element."""
        font = FontInfo()

        if hasattr(element, "font"):
            font_info = element.font
            if hasattr(font_info, "name"):
                font.name = str(font_info.name) if font_info.name else "Calibri"
            if hasattr(font_info, "size"):
                font.size = float(font_info.size) if font_info.size else 11.0
            if hasattr(font_info, "bold"):
                font.bold = bool(font_info.bold)
            if hasattr(font_info, "italic"):
                font.italic = bool(font_info.italic)

        return font

    def _extract_paragraph_format(self, element) -> ParagraphFormat:
        """Extract paragraph formatting from element."""
        para_format = ParagraphFormat()

        if hasattr(element, "line_spacing"):
            ls = element.line_spacing
            if ls:
                para_format.line_spacing_type = self._map_line_spacing_type(ls)
                # Preserve the raw numeric value
                if hasattr(ls, "value"):
                    para_format.line_spacing_value = float(ls.value)
                elif isinstance(ls, (int, float)):
                    para_format.line_spacing_value = float(ls)

        if hasattr(element, "space_before"):
            para_format.space_before = float(element.space_before) if element.space_before else 0.0

        if hasattr(element, "space_after"):
            para_format.space_after = float(element.space_after) if element.space_after else 0.0

        if hasattr(element, "alignment"):
            para_format.alignment = self._map_alignment(element.alignment)

        return para_format

    def _map_line_spacing_type(self, spacing) -> LineSpacingType:
        """Map docling line spacing to our LineSpacingType."""
        spacing_str = str(spacing).lower() if spacing else ""

        if "1.5" in spacing_str or "one_point_five" in spacing_str:
            return LineSpacingType.ONE_POINT_FIVE
        elif "double" in spacing_str:
            return LineSpacingType.DOUBLE
        elif "exact" in spacing_str:
            return LineSpacingType.EXACT
        elif "multiple" in spacing_str:
            return LineSpacingType.MULTIPLE
        else:
            return LineSpacingType.SINGLE

    def _map_alignment(self, alignment) -> Alignment:
        """Map docling alignment to our Alignment enum."""
        alignment_str = str(alignment).lower() if alignment else ""

        if "center" in alignment_str:
            return Alignment.CENTER
        elif "right" in alignment_str:
            return Alignment.RIGHT
        elif "justify" in alignment_str:
            return Alignment.JUSTIFY
        else:
            return Alignment.LEFT