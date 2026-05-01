"""Unit tests for CorrectionExecutor."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from dataclasses import replace
from uuid import uuid4

from app.domain.services.correction_executor import CorrectionExecutor
from app.domain.entities.correction_plan import (
    CorrectionPlan,
    CorrectionStatus,
    CorrectionActionType,
)
from app.domain.entities.validation_result import ValidationResult, Severity
from app.infrastructure.docx.document_parser import (
    ParsedDocument,
    DocumentElement,
    ElementProperties,
    DocumentMetadata,
)


class TestCorrectionExecutor:
    """Tests for CorrectionExecutor."""

    @pytest.fixture
    def mock_writer(self):
        """Create a mock DocumentWriter."""
        return MagicMock()

    @pytest.fixture
    def executor(self, mock_writer):
        """Create CorrectionExecutor with mock writer."""
        return CorrectionExecutor(document_writer=mock_writer)

    @pytest.fixture
    def sample_parsed_document(self):
        """Create a sample ParsedDocument for testing."""
        elements = [
            DocumentElement(
                path="paragraph[1]",
                element_type="paragraph",
                content="正文内容",
                style="Normal",
                properties=ElementProperties(
                    font_name="Times New Roman",
                    font_size=12,
                    line_spacing=1.5,
                ),
                index=1,
            ),
            DocumentElement(
                path="paragraph[2]",
                element_type="paragraph",
                content="更多内容",
                style="Normal",
                properties=ElementProperties(
                    font_name="宋体",
                    font_size=12,
                    line_spacing=2.0,
                ),
                index=2,
            ),
        ]
        return ParsedDocument(
            metadata=DocumentMetadata(title="测试文档"),
            elements=elements,
            styles={},
        )

    def test_execute_with_no_approved_plans(self, executor, sample_parsed_document):
        """Test execute returns original doc when no approved plans."""
        plans = [
            CorrectionPlan(
                result_id=uuid4(),
                action_type=CorrectionActionType.FIX_FONT,
                target_path="paragraph[1]",
                original_value="Times New Roman",
                planned_value="宋体",
                status=CorrectionStatus.PLANNED,
            )
        ]

        result = executor.execute(MagicMock(), sample_parsed_document, plans)
        assert result == sample_parsed_document

    def test_execute_with_approved_plans(self, executor, mock_writer, sample_parsed_document):
        """Test execute applies corrections when plans are approved."""
        plans = [
            CorrectionPlan(
                result_id=uuid4(),
                action_type=CorrectionActionType.FIX_FONT,
                target_path="paragraph[1]",
                original_value="Times New Roman",
                planned_value="宋体",
                status=CorrectionStatus.APPROVED,
            )
        ]

        modified_doc = replace(sample_parsed_document, elements=[])
        mock_writer.apply_corrections.return_value = modified_doc

        result = executor.execute(MagicMock(), sample_parsed_document, plans)

        mock_writer.apply_corrections.assert_called_once_with(sample_parsed_document, plans)
        assert result == modified_doc

    def test_generate_correction_plans_from_results(self, executor):
        """Test correction plans are generated from validation results."""
        results = [
            ValidationResult(
                rule_id="font_name_body",
                rule_name="正文字体",
                element_path="paragraph[1]",
                expected_value="宋体",
                actual_value="Times New Roman",
                message="Font mismatch",
                severity=Severity.ERROR,
                auto_fixable=True,
            ),
            ValidationResult(
                rule_id="line_spacing",
                rule_name="行距",
                element_path="paragraph[2]",
                expected_value="1.5",
                actual_value="2.0",
                message="Line spacing mismatch",
                severity=Severity.WARNING,
                auto_fixable=True,
            ),
            ValidationResult(
                rule_id="citation_format",
                rule_name="引用格式",
                element_path="paragraph[3]",
                expected_value="(Author, Year)",
                actual_value="invalid",
                message="Citation error",
                severity=Severity.ERROR,
                auto_fixable=False,
            ),
        ]

        plans = executor.generate_correction_plans(results)

        assert len(plans) == 2
        assert plans[0].action_type == CorrectionActionType.FIX_FONT
        assert plans[1].action_type == CorrectionActionType.FIX_LINE_SPACING
        assert all(p.status == CorrectionStatus.PLANNED for p in plans)

    def test_determine_action_type_font(self, executor):
        """Test action type determination for font rules."""
        result = MagicMock()
        result.rule_id = "font_name_body"

        action_type = executor._determine_action_type(result)
        assert action_type == CorrectionActionType.FIX_FONT

    def test_determine_action_type_line_spacing(self, executor):
        """Test action type determination for spacing rules."""
        result = MagicMock()
        result.rule_id = "line_spacing"

        action_type = executor._determine_action_type(result)
        assert action_type == CorrectionActionType.FIX_LINE_SPACING

    def test_determine_action_type_paragraph_spacing(self, executor):
        """Test action type determination for paragraph spacing."""
        result = MagicMock()
        result.rule_id = "paragraph_spacing"

        action_type = executor._determine_action_type(result)
        assert action_type == CorrectionActionType.ADJUST_SPACING

    def test_determine_action_type_style(self, executor):
        """Test action type determination for style rules."""
        result = MagicMock()
        result.rule_id = "style_rule"

        action_type = executor._determine_action_type(result)
        assert action_type == CorrectionActionType.REPLACE_STYLE

    def test_determine_action_type_citation(self, executor):
        """Test action type determination for citation rules."""
        result = MagicMock()
        result.rule_id = "citation_format"

        action_type = executor._determine_action_type(result)
        assert action_type == CorrectionActionType.NORMALIZE_CITATION

    def test_approve_plan(self, executor):
        """Test plan approval returns new plan with APPROVED status."""
        plan = CorrectionPlan(
            result_id=uuid4(),
            action_type=CorrectionActionType.FIX_FONT,
            target_path="paragraph[1]",
            original_value="Arial",
            planned_value="宋体",
            status=CorrectionStatus.PLANNED,
        )

        approved = executor.approve_plan(plan)

        assert approved.status == CorrectionStatus.APPROVED
        assert approved != plan

    def test_skip_plan(self, executor):
        """Test plan skip returns new plan with SKIPPED status."""
        plan = CorrectionPlan(
            result_id=uuid4(),
            action_type=CorrectionActionType.FIX_FONT,
            target_path="paragraph[1]",
            original_value="Arial",
            planned_value="宋体",
            status=CorrectionStatus.PLANNED,
        )

        skipped = executor.skip_plan(plan)

        assert skipped.status == CorrectionStatus.SKIPPED
        assert skipped != plan

    def test_execute_and_save(self, executor, mock_writer, sample_parsed_document, tmp_path):
        """Test execute_and_save writes corrected document to file."""
        plans = [
            CorrectionPlan(
                result_id=uuid4(),
                action_type=CorrectionActionType.FIX_FONT,
                target_path="paragraph[1]",
                original_value="Times New Roman",
                planned_value="宋体",
                status=CorrectionStatus.APPROVED,
            )
        ]

        modified_doc = replace(sample_parsed_document, elements=[])
        mock_writer.apply_corrections.return_value = modified_doc

        output_path = tmp_path / "corrected.docx"
        result = executor.execute_and_save(
            MagicMock(),
            sample_parsed_document,
            plans,
            output_path,
        )

        mock_writer.write_to_docx.assert_called_once_with(modified_doc, output_path)
        assert result == output_path


class TestDocumentWriter:
    """Tests for DocumentWriter."""

    def test_find_element_index(self):
        """Test finding element index by path."""
        from app.infrastructure.docx.document_writer import DocumentWriter

        writer = DocumentWriter()
        elements = [
            DocumentElement(path="paragraph[1]", element_type="paragraph", content="1", index=1),
            DocumentElement(path="paragraph[2]", element_type="paragraph", content="2", index=2),
        ]
        doc = ParsedDocument(elements=elements, metadata=DocumentMetadata())

        assert writer._find_element_index("paragraph[1]", doc) == 0
        assert writer._find_element_index("paragraph[2]", doc) == 1
        assert writer._find_element_index("paragraph[99]", doc) is None

    def test_extract_numeric_value(self):
        """Test extracting numeric value from text."""
        from app.infrastructure.docx.document_writer import DocumentWriter

        writer = DocumentWriter()

        assert writer._extract_numeric_value("before: 0.5") == 0.5
        assert writer._extract_numeric_value("after: 1.0") == 1.0
        assert writer._extract_numeric_value("value is 2.5") == 2.5
        assert writer._extract_numeric_value("no number here") is None