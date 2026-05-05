"""Docling-based document parser for PaperNormAI."""

from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter, WordFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from .document_model import (
    Alignment,
    DocumentModel,
    DocumentStructure,
    FigureInfo,
    FontInfo,
    FormulaInfo,
    LineSpacingType,
    PageFormat,
    Paragraph,
    ParagraphFormat,
    StructureItem,
    TableInfo,
    TextSegment,
)


class DoclingDocumentParser:
    """Parser that uses docling to extract content from .docx files.

    Args:
        validate: Whether to validate the output structure
    """

    def __init__(self, validate: bool = True):
        self.validate = validate
        self._converter: Optional[DocumentConverter] = None

    def _get_converter(self) -> DocumentConverter:
        """Lazy initialization of the docling converter."""
        if self._converter is None:
            # For DOCX, use WordFormatOption which uses the simple pipeline
            format_options = {
                InputFormat.DOCX: WordFormatOption(
                    validate_document=self.validate,
                )
            }
            self._converter = DocumentConverter(format_options=format_options)
        return self._converter

    def parse(self, file_path: Path) -> DocumentModel:
        """Parse a .docx file and return a DocumentModel.

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

    def _convert_to_document_model(self, docling_doc) -> DocumentModel:
        """Convert docling DoclingDocument to our DocumentModel.

        Args:
            docling_doc: A DoclingDocument from docling_core.types.doc.document

        Returns:
            DocumentModel containing parsed document content
        """
        model = DocumentModel()

        # Build sections and paragraphs from texts
        sections = []
        paragraphs = []
        for idx, item in enumerate(docling_doc.texts):
            if item.label.value == 'section_header':
                # Section headers go to structure, not paragraphs
                if hasattr(item, 'level') and item.level:
                    sections.append(StructureItem(
                        title=item.text,
                        level=item.level,
                        paragraph_index=len(paragraphs),  # track position among paragraphs
                    ))
                continue

            # Extract font info from formatting
            font_info = FontInfo()
            if item.formatting:
                font_info.bold = item.formatting.bold or False
                font_info.italic = item.formatting.italic or False

            # Build text segment
            segment = TextSegment(content=item.text, font=font_info)

            # Build paragraph with default formatting
            para_format = ParagraphFormat()

            paragraph = Paragraph(
                text=item.text,
                segments=[segment],
                paragraph_format=para_format,
                style_name=None,
            )
            paragraphs.append(paragraph)

        model.paragraphs = paragraphs
        model.structure = DocumentStructure(sections=sections)

        # Extract tables
        for table_item in docling_doc.tables:
            caption = table_item.caption_text(docling_doc) if hasattr(table_item, 'caption_text') else None
            style = None
            if hasattr(table_item, 'table') and hasattr(table_item.table, 'style'):
                style = table_item.table.style
            model.tables.append(TableInfo(
                rows=table_item.data.num_rows if hasattr(table_item, 'data') else 0,
                cols=table_item.data.num_cols if hasattr(table_item, 'data') else 0,
                caption=caption,
                style=style,
            ))

        # Extract figures/pictures
        for picture_item in docling_doc.pictures:
            caption = picture_item.caption_text(docling_doc) if hasattr(picture_item, 'caption_text') else None
            # Dimensions are in image.size
            width = 0.0
            height = 0.0
            if hasattr(picture_item, 'image') and hasattr(picture_item.image, 'size'):
                width = picture_item.image.size.width
                height = picture_item.image.size.height
            model.figures.append(FigureInfo(
                width=width,
                height=height,
                caption=caption,
            ))

        # Extract formulas by filtering iterate_items for formula items
        for item_tuple in docling_doc.iterate_items():
            for sub_item in item_tuple:
                if type(sub_item).__name__ == 'FormulaItem':
                    content = sub_item.text if hasattr(sub_item, 'text') else ""
                    number = sub_item.number if hasattr(sub_item, 'number') else None
                    numbered = number is not None
                    model.formulas.append(FormulaInfo(
                        content=content,
                        numbered=numbered,
                        number=str(number) if number is not None else None,
                    ))

        return model