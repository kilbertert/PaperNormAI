"""CorrectionService domain service.

Applies user-confirmed corrections from ValidationReport to documents.
"""

from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

from app.domain.entities.validation_report import ValidationReport, ViolationDetail
from app.infrastructure.docx.document_merger import DocumentMerger


class CorrectionService:
    """Service for applying corrections to documents based on ValidationReport.

    Takes a ValidationReport with user-confirmed violations and applies
    the corrections to the original document.
    """

    def __init__(self, merger: Optional[DocumentMerger] = None, output_dir: Optional[Path] = None):
        """Initialize CorrectionService.

        Args:
            merger: DocumentMerger instance. Creates default if not provided.
            output_dir: Directory for corrected documents. Uses original dir if not provided.
        """
        self._merger = merger or DocumentMerger(output_dir=output_dir)
        self._output_dir = output_dir

    def apply_corrections(
        self,
        validation_report: ValidationReport,
        user_modifications: Dict[UUID, str],
        original_doc_path: Path,
    ) -> Path:
        """Apply corrections from ValidationReport to the original document.

        Args:
            validation_report: The validation report with violations to apply
            user_modifications: Dict mapping violation_id to user-modified fix.
                               If a violation_id is not in this dict, the
                               suggested_fix from the report is used.
            original_doc_path: Path to the original .docx file

        Returns:
            Path to the corrected .docx file

        Raises:
            FileNotFoundError: If original_doc_path does not exist
            ValueError: If validation_report has no violations
        """
        if not original_doc_path.exists():
            raise FileNotFoundError(f"Original document not found: {original_doc_path}")

        if not validation_report.violations:
            raise ValueError("ValidationReport has no violations to apply")

        # Build corrections list from validation report and user modifications
        corrections = self._build_corrections(validation_report, user_modifications)

        # Merge corrections into original document
        corrected_path = self._merger.merge(original_doc_path, corrections)

        return corrected_path

    def _build_corrections(
        self,
        validation_report: ValidationReport,
        user_modifications: Dict[UUID, str],
    ) -> List[Dict]:
        """Build corrections list from validation report.

        Args:
            validation_report: The validation report
            user_modifications: User modifications dict

        Returns:
            List of correction dicts for DocumentMerger
        """
        corrections = []

        for violation in validation_report.violations:
            # Skip if original_content or suggested_fix are empty
            if not violation.original_content or not violation.suggested_fix:
                continue

            # Get effective fix (user modification takes priority)
            effective_fix = user_modifications.get(
                violation.id,
                violation.user_modified_fix or violation.suggested_fix
            )

            correction = {
                "original": violation.original_content,
                "fixed": effective_fix,
                "paragraph_index": violation.location.paragraph_index,
                "context_before": violation.context_before,
                "context_after": violation.context_after,
            }

            corrections.append(correction)

        return corrections

    def apply_corrections_batch(
        self,
        validation_reports: List[ValidationReport],
        user_modifications_list: List[Dict[UUID, str]],
        original_doc_paths: List[Path],
    ) -> List[Path]:
        """Apply corrections to multiple documents.

        Args:
            validation_reports: List of validation reports
            user_modifications_list: List of user modification dicts
            original_doc_paths: List of original document paths

        Returns:
            List of paths to corrected documents

        Raises:
            ValueError: If lists have different lengths
        """
        if len(validation_reports) != len(user_modifications_list) != len(original_doc_paths):
            raise ValueError(
                "All input lists must have the same length. "
                f"Got {len(validation_reports)}, {len(user_modifications_list)}, "
                f"and {len(original_doc_paths)}"
            )

        corrected_paths = []
        for report, modifications, doc_path in zip(
            validation_reports, user_modifications_list, original_doc_paths
        ):
            corrected_path = self.apply_corrections(report, modifications, doc_path)
            corrected_paths.append(corrected_path)

        return corrected_paths

    @property
    def using_ai_word_skill(self) -> bool:
        """Returns True if the underlying merger uses AI-Word-Skill."""
        return self._merger.using_ai_word_skill