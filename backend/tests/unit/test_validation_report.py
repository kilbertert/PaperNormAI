"""Unit tests for validation_report entities."""

import pytest
from uuid import uuid4

from app.domain.entities.validation_report import (
    ViolationSeverity,
    ViolationCategory,
    TextLocation,
    ViolationDetail,
    ValidationReport,
)


class TestViolationSeverity:
    """Tests for ViolationSeverity enum."""

    def test_error_value(self):
        assert ViolationSeverity.ERROR == "error"

    def test_warning_value(self):
        assert ViolationSeverity.WARNING == "warning"

    def test_info_value(self):
        assert ViolationSeverity.INFO == "info"


class TestViolationCategory:
    """Tests for ViolationCategory enum."""

    def test_font_value(self):
        assert ViolationCategory.FONT == "font"

    def test_font_size_value(self):
        assert ViolationCategory.FONT_SIZE == "font_size"

    def test_line_spacing_value(self):
        assert ViolationCategory.LINE_SPACING == "line_spacing"

    def test_paragraph_spacing_value(self):
        assert ViolationCategory.PARAGRAPH_SPACING == "paragraph_spacing"

    def test_page_margin_value(self):
        assert ViolationCategory.PAGE_MARGIN == "page_margin"

    def test_heading_value(self):
        assert ViolationCategory.HEADING == "heading"


class TestTextLocation:
    """Tests for TextLocation dataclass."""

    def test_text_location_creation(self):
        location = TextLocation(paragraph_index=5, text="Sample text")
        assert location.paragraph_index == 5
        assert location.text == "Sample text"
        assert location.start_offset is None
        assert location.end_offset is None

    def test_text_location_with_offsets(self):
        location = TextLocation(
            paragraph_index=5,
            text="Sample text",
            start_offset=10,
            end_offset=20,
        )
        assert location.start_offset == 10
        assert location.end_offset == 20


class TestViolationDetail:
    """Tests for ViolationDetail dataclass."""

    def test_violation_detail_creation(self):
        violation = ViolationDetail(
            category=ViolationCategory.FONT,
            severity=ViolationSeverity.ERROR,
            description="Font should be SongTi",
            location=TextLocation(paragraph_index=1, text="Some text"),
            original_content="HeiTi",
            suggested_fix="SongTi",
        )
        assert violation.category == ViolationCategory.FONT
        assert violation.severity == ViolationSeverity.ERROR
        assert violation.user_modified_fix is None

    def test_violation_detail_with_user_fix(self):
        violation = ViolationDetail(
            category=ViolationCategory.FONT_SIZE,
            severity=ViolationSeverity.WARNING,
            description="Font size should be 12pt",
            location=TextLocation(paragraph_index=2, text="Some text"),
            original_content="14pt",
            suggested_fix="12pt",
            user_modified_fix="13pt",
        )
        assert violation.user_modified_fix == "13pt"


class TestValidationReport:
    """Tests for ValidationReport dataclass."""

    def test_validation_report_creation(self):
        report = ValidationReport(document_name="test.docx")
        assert report.document_name == "test.docx"
        assert report.status == "pending"
        assert len(report.violations) == 0

    def test_add_violation(self):
        report = ValidationReport(document_name="test.docx")
        violation = ViolationDetail(
            category=ViolationCategory.FONT,
            severity=ViolationSeverity.ERROR,
            description="Font should be SongTi",
            location=TextLocation(paragraph_index=1, text="Some text"),
            original_content="HeiTi",
            suggested_fix="SongTi",
        )
        report.add_violation(violation)
        assert len(report.violations) == 1

    def test_get_violation_count(self):
        report = ValidationReport(document_name="test.docx")
        assert report.get_violation_count() == 0
        report.add_violation(ViolationDetail(
            category=ViolationCategory.FONT,
            severity=ViolationSeverity.ERROR,
            description="test",
            location=TextLocation(paragraph_index=1, text="text"),
            original_content="",
            suggested_fix="",
        ))
        assert report.get_violation_count() == 1

    def test_get_error_count(self):
        report = ValidationReport(document_name="test.docx")
        report.add_violation(ViolationDetail(
            category=ViolationCategory.FONT,
            severity=ViolationSeverity.ERROR,
            description="test",
            location=TextLocation(paragraph_index=1, text="text"),
            original_content="",
            suggested_fix="",
        ))
        report.add_violation(ViolationDetail(
            category=ViolationCategory.FONT_SIZE,
            severity=ViolationSeverity.WARNING,
            description="test",
            location=TextLocation(paragraph_index=2, text="text"),
            original_content="",
            suggested_fix="",
        ))
        assert report.get_error_count() == 1
        assert report.get_warning_count() == 1

    def test_get_effective_fix(self):
        report = ValidationReport(document_name="test.docx")
        violation = ViolationDetail(
            category=ViolationCategory.FONT,
            severity=ViolationSeverity.ERROR,
            description="Font should be SongTi",
            location=TextLocation(paragraph_index=1, text="Some text"),
            original_content="HeiTi",
            suggested_fix="SongTi",
        )
        report.add_violation(violation)
        violation_id = violation.id

        assert report.get_effective_fix(violation_id) == "SongTi"

    def test_get_effective_fix_user_modified(self):
        report = ValidationReport(document_name="test.docx")
        violation = ViolationDetail(
            category=ViolationCategory.FONT,
            severity=ViolationSeverity.ERROR,
            description="Font should be SongTi",
            location=TextLocation(paragraph_index=1, text="Some text"),
            original_content="HeiTi",
            suggested_fix="SongTi",
            user_modified_fix="SimHei",
        )
        report.add_violation(violation)
        violation_id = violation.id

        assert report.get_effective_fix(violation_id) == "SimHei"

    def test_get_effective_fix_not_found(self):
        report = ValidationReport(document_name="test.docx")
        with pytest.raises(ValueError):
            report.get_effective_fix(uuid4())

    def test_confirm_all(self):
        report = ValidationReport(document_name="test.docx")
        report.confirm_all()
        assert report.status == "confirmed"

    def test_get_editable_violations(self):
        report = ValidationReport(document_name="test.docx")
        report.add_violation(ViolationDetail(
            category=ViolationCategory.FONT,
            severity=ViolationSeverity.ERROR,
            description="test",
            location=TextLocation(paragraph_index=1, text="text"),
            original_content="",
            suggested_fix="",
        ))
        report.add_violation(ViolationDetail(
            category=ViolationCategory.FONT_SIZE,
            severity=ViolationSeverity.WARNING,
            description="test",
            location=TextLocation(paragraph_index=2, text="text"),
            original_content="",
            suggested_fix="",
            user_modified_fix="modified",
        ))
        editable = report.get_editable_violations()
        assert len(editable) == 2
