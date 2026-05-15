"""Document writer for applying corrections to .docx files.

Applies correction plans to parsed documents and generates
corrected .docx files.
"""

from dataclasses import replace
from pathlib import Path
from typing import List, Optional

try:
    import docx
    from docx.document import Document as DocxDocument
    from docx.text.paragraph import Paragraph
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from app.infrastructure.docx.document_parser import ParsedDocument, DocumentElement, ElementProperties
from app.domain.entities.correction_plan import CorrectionPlan, CorrectionStatus, CorrectionActionType


class DocumentWriter:
    """Writes corrections back to .docx files."""

    def __init__(self):
        self._applied_corrections: List[CorrectionPlan] = []

    def apply_corrections(
        self,
        parsed_document: ParsedDocument,
        plans: List[CorrectionPlan],
    ) -> ParsedDocument:
        """Apply correction plans to a parsed document.

        Args:
            parsed_document: The parsed document to modify
            plans: List of correction plans to apply

        Returns:
            Modified ParsedDocument with corrections applied
        """
        self._applied_corrections = []

        approved_plans = [p for p in plans if p.status == CorrectionStatus.APPROVED]

        modified_doc = parsed_document

        for plan in approved_plans:
            modified_doc = self._apply_plan_to_parsed(modified_doc, plan)
            self._applied_corrections.append(plan)

        return modified_doc

    def _apply_plan_to_parsed(
        self,
        parsed_document: ParsedDocument,
        plan: CorrectionPlan,
    ) -> ParsedDocument:
        """Apply a single correction plan to parsed document.

        Returns modified ParsedDocument (immutable operation via replace).
        """
        target_index = self._find_element_index(plan.target_path, parsed_document)

        if target_index is None:
            return parsed_document

        element = parsed_document.elements[target_index]
        modified_element = self._apply_correction_to_element(element, plan)

        new_elements = list(parsed_document.elements)
        new_elements[target_index] = modified_element

        return replace(parsed_document, elements=new_elements)

    def _find_element_index(self, path: str, parsed_document: ParsedDocument) -> Optional[int]:
        """Find element index by path."""
        for i, elem in enumerate(parsed_document.elements):
            if elem.path == path:
                return i
        return None

    def _apply_correction_to_element(
        self,
        element: DocumentElement,
        plan: CorrectionPlan,
    ) -> DocumentElement:
        """Apply correction action to element properties.

        Returns modified DocumentElement (immutable via replace).
        """
        action_type = plan.action_type

        if action_type == CorrectionActionType.FIX_FONT:
            new_properties = replace(
                element.properties,
                font_name=plan.planned_value,
            )
            return replace(element, properties=new_properties)

        elif action_type == CorrectionActionType.FIX_LINE_SPACING:
            # Parse the planned value which could be '23pt (fixed)' or just '23'
            line_spacing_value = self._extract_numeric_value(plan.planned_value) if plan.planned_value else None
            new_properties = replace(
                element.properties,
                line_spacing=line_spacing_value,
                line_spacing_rule='fixed',  # Set to fixed since spec says fixed
            )
            return replace(element, properties=new_properties)

        elif action_type == CorrectionActionType.ADJUST_SPACING:
            new_properties = self._adjust_spacing_properties(
                element.properties,
                plan.original_value,
                plan.planned_value,
            )
            return replace(element, properties=new_properties)

        elif action_type == CorrectionActionType.REPLACE_STYLE:
            return replace(element, style=plan.planned_value)

        return element

    def _adjust_spacing_properties(
        self,
        properties: ElementProperties,
        original: str,
        planned: str,
    ) -> ElementProperties:
        """Adjust spacing properties based on correction."""
        if "before" in original.lower() and "before" in planned.lower():
            value = self._extract_numeric_value(planned)
            if value is not None:
                return replace(properties, paragraph_spacing_before=value)

        if "after" in original.lower() and "after" in planned.lower():
            value = self._extract_numeric_value(planned)
            if value is not None:
                return replace(properties, paragraph_spacing_after=value)

        return properties

    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text like 'before: 0.5'."""
        import re
        match = re.search(r'[\d.]+', text)
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass
        return None

    def write_to_docx(
        self,
        parsed_document: ParsedDocument,
        output_path: Path,
        original_doc_path: Path = None,
    ) -> None:
        """Write parsed document with corrections back to .docx file.

        If original_doc_path is provided, copies it and applies corrections
        in place, preserving all original styles.
        Otherwise creates a new document (styles may be missing).
        """
        if original_doc_path and original_doc_path.exists():
            import shutil
            shutil.copy(original_doc_path, output_path)
            doc = docx.Document(str(output_path))
            self._update_existing_document(doc, parsed_document)
        else:
            doc = docx.Document()
            for element in parsed_document.elements:
                self._write_element(doc, element)
        doc.save(str(output_path))

    def _update_existing_document(
        self,
        doc: docx.Document,
        parsed_document: ParsedDocument,
    ) -> None:
        """Update an existing document in place with corrections."""
        para_index = 0
        element_to_para = {}
        for element in parsed_document.elements:
            if element.element_type in ('paragraph', 'heading'):
                if para_index < len(doc.paragraphs):
                    element_to_para[element.index] = (para_index, doc.paragraphs[para_index])
                para_index += 1

        for element in parsed_document.elements:
            if element.index in element_to_para:
                para_idx, para = element_to_para[element.index]
                if element.style:
                    para.style = element.style
                self._apply_properties_to_paragraph(para, element.properties)

    def _write_element(self, doc: DocxDocument, element: DocumentElement) -> None:
        """Write a single element to the document."""
        if element.element_type == "paragraph":
            para = doc.add_paragraph()
            para.text = element.content

            if element.style:
                para.style = element.style

            self._apply_properties_to_paragraph(para, element.properties)

        elif element.element_type == "heading":
            para = doc.add_heading(element.content, level=self._extract_heading_level(element.style))
            self._apply_properties_to_paragraph(para, element.properties)

        elif element.element_type == "table":
            table = doc.add_table(rows=1, cols=1)
            table.cell(0, 0).text = element.content

    def _apply_properties_to_paragraph(
        self,
        para: Paragraph,
        properties: ElementProperties,
    ) -> None:
        """Apply ElementProperties to a paragraph."""
        if properties.font_name or properties.font_size:
            for run in para.runs:
                if properties.font_name:
                    run.font.name = properties.font_name
                if properties.font_size:
                    run.font.size = docx.shared.Pt(properties.font_size)

        if properties.line_spacing is not None:
            # Skip fixed line spacing for now - requires XML manipulation
            pass

        if properties.paragraph_spacing_before is not None:
            para.paragraph_format.space_before = int(properties.paragraph_spacing_before)

        if properties.paragraph_spacing_after is not None:
            para.paragraph_format.space_after = int(properties.paragraph_spacing_after)

    def _extract_heading_level(self, style: Optional[str]) -> int:
        """Extract heading level from style name."""
        if not style:
            return 1
        import re
        match = re.search(r'\d+', style)
        if match:
            return int(match.group())
        return 1
