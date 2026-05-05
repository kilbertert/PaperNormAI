"""Document merger for applying corrections to .docx files.

Uses AI-Word-Skill pattern: copy original file → edit run.text → save.
This preserves all original formatting.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional
import shutil
import difflib
import tempfile
import uuid

try:
    from docx import Document
    from docx.text.paragraph import Paragraph
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


@dataclass
class MergeResult:
    """Result of a merge operation."""
    success: bool
    output_path: Optional[Path]
    applied_corrections: int = 0
    failed_corrections: List[Dict] = field(default_factory=list)


class DocumentMerger:
    """Merges corrections back into original .docx files.

    Preserves all original formatting - only text content is modified.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize DocumentMerger.

        Args:
            output_dir: Directory to save corrected documents.
                       Defaults to system temp directory.
        """
        self._output_dir = output_dir

    def merge(
        self,
        original_path: Path,
        corrections: List[Dict],
    ) -> MergeResult:
        """Merge corrections into original document.

        Args:
            original_path: Path to original .docx file
            corrections: List of correction dicts with keys:
                - original: original text to find
                - fixed: corrected text to replace with
                - paragraph_index: 1-based paragraph index hint
                - context_before: text before (for disambiguation)
                - context_after: text after (for disambiguation)

        Returns:
            MergeResult with success status, output path, and failure details

        Raises:
            FileNotFoundError: If original_path does not exist
            RuntimeError: If python-docx is not available
        """
        if not DOCX_AVAILABLE:
            return MergeResult(
                success=False,
                output_path=None,
                failed_corrections=[{"original": "N/A", "error": "python-docx not installed"}]
            )

        if not original_path.exists():
            return MergeResult(
                success=False,
                output_path=None,
                failed_corrections=[{"original": "N/A", "error": f"File not found: {original_path}"}]
            )

        # Use temp file for atomic operation (Fix 3)
        temp_path = Path(tempfile.gettempdir()) / f"{original_path.stem}_temp_{uuid.uuid4().hex[:8]}.docx"

        try:
            shutil.copy2(original_path, temp_path)

            result = self._apply_corrections(temp_path, corrections)

            # Check if any corrections were applied
            applied = getattr(result, 'applied_corrections', 0)
            if applied > 0:
                # Some corrections were applied - save the document even if some failed
                output_path = self._get_output_path(original_path)
                shutil.move(str(temp_path), str(output_path))
                result.output_path = output_path
                return result
            else:
                # No corrections applied - delete temp file
                return result

        except Exception as e:
            return MergeResult(
                success=False,
                output_path=None,
                failed_corrections=[{"original": "N/A", "error": str(e)}]
            )
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _get_output_path(self, original_path: Path) -> Path:
        """Determine output path for corrected document."""
        output_dir = self._output_dir or Path(original_path).parent

        original_stem = original_path.stem
        output_path = output_dir / f"{original_stem}_corrected.docx"

        # If file exists, add counter
        counter = 1
        while output_path.exists():
            output_path = output_dir / f"{original_stem}_corrected_{counter}.docx"
            counter += 1

        return output_path

    def _apply_corrections(
        self,
        docx_path: Path,
        corrections: List[Dict],
    ) -> MergeResult:
        """Apply corrections using AI-Word-Skill pattern.

        Copy original file → edit run.text → save.
        This preserves all original formatting.
        """
        doc = Document(str(docx_path))
        applied = 0
        failed = []

        for correction in corrections:
            original_text = correction["original"]
            fixed_text = correction["fixed"]
            context_before = correction.get("context_before")
            context_after = correction.get("context_after")
            paragraph_index = correction.get("paragraph_index")

            # Try paragraph_index hint first
            if paragraph_index:
                target_idx = paragraph_index - 1  # Convert to 0-based
                if 0 <= target_idx < len(doc.paragraphs):
                    para = doc.paragraphs[target_idx]
                    if self._paragraph_matches_context(para, original_text, context_before, context_after):
                        if self._replace_paragraph_text(para, original_text, fixed_text):
                            applied += 1
                            continue

            # Fall back to full iteration
            if self._replace_in_paragraphs(
                doc,
                original_text,
                fixed_text,
                context_before,
                context_after,
            ):
                applied += 1
            else:
                failed.append({
                    "original": original_text,
                    "paragraph_index": paragraph_index,
                    "error": "No matching paragraph found"
                })

        doc.save(str(docx_path))

        return MergeResult(
            success=len(failed) == 0,
            output_path=docx_path,
            applied_corrections=applied,
            failed_corrections=failed
        )

    def _replace_in_paragraphs(
        self,
        doc: Document,
        original: str,
        fixed: str,
        context_before: Optional[str],
        context_after: Optional[str],
    ) -> bool:
        """Replace text in paragraphs, using context for disambiguation.

        Returns True if replacement was made, False otherwise.
        """
        for para in doc.paragraphs:
            if self._paragraph_matches_context(para, original, context_before, context_after):
                if self._replace_paragraph_text(para, original, fixed):
                    return True
        return False

    def _paragraph_matches_context(
        self,
        para: Paragraph,
        target_text: str,
        context_before: Optional[str],
        context_after: Optional[str],
    ) -> bool:
        """Check if paragraph matches the given context."""
        para_text = para.text

        # Check if target text is in paragraph
        if target_text not in para_text:
            return False

        # If context provided, verify it matches
        if context_before:
            idx = para_text.find(target_text)
            text_before = para_text[:idx]
            # Check if context_before appears near the target
            if context_before not in text_before and not self._fuzzy_match(context_before, text_before[-50:] if len(text_before) >= 50 else text_before):
                return False

        if context_after:
            idx = para_text.find(target_text)
            text_after = para_text[idx + len(target_text):]
            if context_after not in text_after and not self._fuzzy_match(context_after, text_after[:50] if len(text_after) >= 50 else text_after):
                return False

        return True

    def _replace_paragraph_text(
        self,
        para: Paragraph,
        original: str,
        fixed: str,
    ) -> bool:
        """Replace text in a paragraph while preserving first-run formatting."""
        if original not in para.text:
            return False

        # Get the first run's formatting to preserve
        first_run_formatting = None
        if para.runs:
            first_run = para.runs[0]
            first_run_formatting = {
                "font_name": first_run.font.name,
                "font_size": first_run.font.size,
                "font_bold": first_run.font.bold,
                "font_italic": first_run.font.italic,
            }

        # For simple case: single run, just replace
        if len(para.runs) == 1:
            para.runs[0].text = para.runs[0].text.replace(original, fixed, 1)
            return True

        # For multiple runs, we need to handle carefully
        # Find the run containing the original text
        for run in para.runs:
            if original in run.text:
                run.text = run.text.replace(original, fixed, 1)
                return True

        return False

    def _fuzzy_match(self, pattern: str, text: str, threshold: float = 0.8) -> bool:
        """Check if pattern fuzzy-matches in text."""
        if not pattern or not text:
            return False

        # Simple ratio match
        ratio = difflib.SequenceMatcher(None, pattern, text[-len(pattern):] if len(text) > len(pattern) else text).ratio()
        return ratio >= threshold