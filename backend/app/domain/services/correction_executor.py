"""CorrectionExecutor domain service.

Applies correction plans to parsed documents and generates
corrected .docx files.
"""

from dataclasses import replace
from pathlib import Path
from typing import List, Optional

from app.domain.entities.document import Document
from app.domain.entities.correction_plan import CorrectionPlan, CorrectionStatus, CorrectionActionType
from app.domain.entities.validation_result import ValidationResult
from app.infrastructure.docx.document_parser import ParsedDocument, DocumentElement
from app.infrastructure.docx.document_writer import DocumentWriter


class CorrectionExecutor:
    """Domain service for executing correction plans."""

    def __init__(self, document_writer: Optional[DocumentWriter] = None):
        self._writer = document_writer or DocumentWriter()

    def execute(
        self,
        document: Document,
        parsed_document: ParsedDocument,
        plans: List[CorrectionPlan],
    ) -> ParsedDocument:
        """Execute correction plans on a parsed document.

        Args:
            document: The domain document entity (for reference)
            parsed_document: The intermediate parsed document model
            plans: List of correction plans to apply

        Returns:
            Modified ParsedDocument with corrections applied
        """
        approved_plans = [p for p in plans if p.status == CorrectionStatus.APPROVED]

        if not approved_plans:
            return parsed_document

        modified_doc = self._writer.apply_corrections(parsed_document, plans)

        return modified_doc

    def execute_and_save(
        self,
        document: Document,
        parsed_document: ParsedDocument,
        plans: List[CorrectionPlan],
        output_path: Path,
    ) -> Path:
        """Execute corrections and save to a new .docx file.

        Args:
            document: The domain document entity
            parsed_document: The intermediate parsed document model
            plans: List of correction plans to apply
            output_path: Path to save the corrected document

        Returns:
            Path to the saved corrected document
        """
        modified_doc = self.execute(document, parsed_document, plans)
        self._writer.write_to_docx(modified_doc, output_path)
        return output_path

    def generate_correction_plans(
        self, results: List[ValidationResult]
    ) -> List[CorrectionPlan]:
        """Generate correction plans from validation results.

        Only auto_fixable results generate plans.
        """
        plans = []
        for result in results:
            if result.auto_fixable:
                plan = CorrectionPlan(
                    result_id=result.id,
                    action_type=self._determine_action_type(result),
                    target_path=result.element_path,
                    original_value=result.actual_value,
                    planned_value=result.expected_value,
                )
                plans.append(plan)
        return plans

    def _determine_action_type(self, result: ValidationResult) -> CorrectionActionType:
        """Determine the correction action type based on result."""
        rule_id = result.rule_id.lower()

        if "font" in rule_id and "name" in rule_id:
            return CorrectionActionType.FIX_FONT
        elif "font" in rule_id and "size" in rule_id:
            return CorrectionActionType.FIX_FONT
        elif "spacing" in rule_id or "line_spacing" in rule_id:
            return CorrectionActionType.FIX_LINE_SPACING
        elif "paragraph_spacing" in rule_id:
            return CorrectionActionType.ADJUST_SPACING
        elif "style" in rule_id:
            return CorrectionActionType.REPLACE_STYLE
        elif "citation" in rule_id:
            return CorrectionActionType.NORMALIZE_CITATION

        return CorrectionActionType.REPLACE_STYLE

    def approve_plan(self, plan: CorrectionPlan) -> CorrectionPlan:
        """Approve a correction plan for execution."""
        return replace(plan, status=CorrectionStatus.APPROVED)

    def skip_plan(self, plan: CorrectionPlan) -> CorrectionPlan:
        """Skip a correction plan."""
        return replace(plan, status=CorrectionStatus.SKIPPED)

    def get_applied_corrections(self) -> List[CorrectionPlan]:
        """Get list of corrections that were applied by last execute()."""
        return self._writer._applied_corrections