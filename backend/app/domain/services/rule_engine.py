"""RuleEngine domain service.

The core domain service that orchestrates validation using L1/L2/L3 rules.
L1 rules are deterministic (font, size, spacing).
L2 rules are pattern-based (heading levels, citation patterns).
L3 rules require AI enhancement (complex citation/reference validation).
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from app.domain.entities.document import Document
from app.domain.entities.template import Template
from app.domain.entities.validation_result import ValidationReport, ValidationResult, Severity
from app.domain.entities.validation_rule import RuleLevel, ValidationRule
from app.infrastructure.docx.document_parser import ParsedDocument, DocumentElement
from app.domain.services.template_service import TemplateService
from app.domain.services.ai_enhancement_service import AIEnhancementService


class RuleEngine:
    """Core domain service for document validation."""

    L1_RULE_HANDLERS = {
        "font_name_body": "_check_font_name_body",
        "font_name_heading": "_check_font_name_heading",
        "font_size_body": "_check_font_size_body",
        "line_spacing": "_check_line_spacing",
        "paragraph_spacing": "_check_paragraph_spacing",
        "page_margin": "_check_page_margin",
    }

    L2_RULE_HANDLERS = {
        "heading_level": "_check_heading_level",
        "citation_format": "_check_citation_format_pattern",
    }

    def __init__(
        self,
        template_service: TemplateService,
        ai_enhancement: AIEnhancementService,
    ):
        self.template_service = template_service
        self.ai_enhancement = ai_enhancement

    def validate(
        self,
        document: Document,
        parsed_document: ParsedDocument,
        template: Template,
    ) -> ValidationReport:
        """Validate a parsed document against a template.

        Args:
            document: The domain document entity
            parsed_document: The intermediate parsed document model
            template: The template with validation rules

        Returns:
            ValidationReport with all results
        """
        results: List[ValidationResult] = []
        rules = template.get_active_rules()

        for rule in rules:
            if rule.level == RuleLevel.L3:
                rule_results = self._validate_with_ai(parsed_document, rule)
                results.extend(rule_results)
            elif rule.level in (RuleLevel.L1, RuleLevel.L2):
                rule_results = self._validate_rule(parsed_document, rule)
                results.extend(rule_results)

        return ValidationReport(
            document_id=document.id,
            template_id=template.id,
            job_id=getattr(document, "current_job_id", document.id),
            results=results,
        )

    def _validate_rule(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> List[ValidationResult]:
        """Execute a deterministic (L1/L2) rule."""
        results = []

        handler_name = self.L1_RULE_HANDLERS.get(rule.id)
        if handler_name and hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            result = handler(parsed_document, rule)
            if result:
                results.append(result)
        elif rule.id in self.L2_RULE_HANDLERS:
            handler_name = self.L2_RULE_HANDLERS[rule.id]
            if hasattr(self, handler_name):
                handler = getattr(self, handler_name)
                rule_results = handler(parsed_document, rule)
                if rule_results:
                    results.extend(rule_results)
        else:
            results.extend(self._check_generic_rule(parsed_document, rule))

        return results

    def _check_font_name_body(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> Optional[ValidationResult]:
        """Check body font name matches expected value."""
        expected_fonts = rule.params.get("allowed_fonts", [rule.params.get("expected_value")])
        expected_fonts_lower = [f.lower() for f in expected_fonts if f]

        for element in parsed_document.elements:
            if element.element_type != "paragraph":
                continue
            if element.properties.font_name:
                font_lower = element.properties.font_name.lower()
                if font_lower not in expected_fonts_lower:
                    return ValidationResult(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        element_path=element.path,
                        expected_value=str(expected_fonts),
                        actual_value=element.properties.font_name,
                        message=f"Expected font '{expected_fonts[0]}' but found '{element.properties.font_name}'",
                        severity=Severity(rule.severity.value),
                        auto_fixable=rule.auto_fixable,
                        ai_enhanced=False,
                    )
        return None

    def _check_font_name_heading(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> Optional[ValidationResult]:
        """Check heading font name matches expected value."""
        expected_fonts = rule.params.get("allowed_fonts", [rule.params.get("expected_value")])
        expected_fonts_lower = [f.lower() for f in expected_fonts if f]

        for element in parsed_document.elements:
            if element.element_type != "heading":
                continue
            if element.properties.font_name:
                font_lower = element.properties.font_name.lower()
                if font_lower not in expected_fonts_lower:
                    return ValidationResult(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        element_path=element.path,
                        expected_value=str(expected_fonts),
                        actual_value=element.properties.font_name,
                        message=f"Heading font should be '{expected_fonts[0]}' but found '{element.properties.font_name}'",
                        severity=Severity(rule.severity.value),
                        auto_fixable=rule.auto_fixable,
                        ai_enhanced=False,
                    )
        return None

    def _check_font_size_body(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> Optional[ValidationResult]:
        """Check body font size matches expected value."""
        expected_size = rule.params.get("expected_value")
        tolerance = rule.params.get("tolerance", 0)

        if expected_size is None:
            return None

        for element in parsed_document.elements:
            if element.element_type != "paragraph":
                continue
            if element.properties.font_size is not None:
                actual_size = element.properties.font_size
                if abs(actual_size - expected_size) > tolerance:
                    return ValidationResult(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        element_path=element.path,
                        expected_value=f"{expected_size}pt",
                        actual_value=f"{actual_size}pt",
                        message=f"Expected font size {expected_size}pt but found {actual_size}pt",
                        severity=Severity(rule.severity.value),
                        auto_fixable=rule.auto_fixable,
                        ai_enhanced=False,
                    )
        return None

    def _check_line_spacing(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> Optional[ValidationResult]:
        """Check line spacing matches expected value.

        Handles both:
        - 'fixed' mode: exact pt value (e.g., 23pt)
        - 'multiple' mode: multiplier (e.g., 1.5x)
        """
        expected_spacing = rule.params.get("expected_value")
        expected_rule = rule.params.get("line_spacing_type")  # 'fixed' or 'multiple'
        tolerance = rule.params.get("tolerance", 0.1)

        if expected_spacing is None:
            return None

        for element in parsed_document.elements:
            if element.element_type != "paragraph":
                continue
            if element.properties.line_spacing is not None:
                actual_spacing = element.properties.line_spacing
                actual_rule = element.properties.line_spacing_rule

                # First check if the rule type matches
                if expected_rule and actual_rule:
                    if expected_rule != actual_rule:
                        return ValidationResult(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            element_path=element.path,
                            expected_value=f"{expected_spacing}pt ({expected_rule})",
                            actual_value=f"{actual_spacing}pt ({actual_rule})",
                            message=f"Line spacing type mismatch: expected {expected_rule} but found {actual_rule}",
                            severity=Severity(rule.severity.value),
                            auto_fixable=rule.auto_fixable,
                            ai_enhanced=False,
                        )

                # Then check the value (with tolerance for pt values)
                if abs(actual_spacing - expected_spacing) > tolerance:
                    return ValidationResult(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        element_path=element.path,
                        expected_value=f"{expected_spacing}pt",
                        actual_value=f"{actual_spacing}pt",
                        message=f"Expected line spacing {expected_spacing}pt but found {actual_spacing}pt",
                        severity=Severity(rule.severity.value),
                        auto_fixable=rule.auto_fixable,
                        ai_enhanced=False,
                    )
        return None

    def _check_paragraph_spacing(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> Optional[ValidationResult]:
        """Check paragraph spacing matches expected values."""
        expected_before = rule.params.get("space_before")
        expected_after = rule.params.get("space_after")
        tolerance = 0.1

        if expected_before is None and expected_after is None:
            return None

        for element in parsed_document.elements:
            if element.element_type != "paragraph":
                continue

            if expected_before is not None and element.properties.paragraph_spacing_before is not None:
                if abs(element.properties.paragraph_spacing_before - expected_before) > tolerance:
                    return ValidationResult(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        element_path=element.path,
                        expected_value=f"before: {expected_before}",
                        actual_value=f"before: {element.properties.paragraph_spacing_before}",
                        message=f"Expected paragraph spacing before {expected_before} but found {element.properties.paragraph_spacing_before}",
                        severity=Severity(rule.severity.value),
                        auto_fixable=rule.auto_fixable,
                        ai_enhanced=False,
                    )

            if expected_after is not None and element.properties.paragraph_spacing_after is not None:
                if abs(element.properties.paragraph_spacing_after - expected_after) > tolerance:
                    return ValidationResult(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        element_path=element.path,
                        expected_value=f"after: {expected_after}",
                        actual_value=f"after: {element.properties.paragraph_spacing_after}",
                        message=f"Expected paragraph spacing after {expected_after} but found {element.properties.paragraph_spacing_after}",
                        severity=Severity(rule.severity.value),
                        auto_fixable=rule.auto_fixable,
                        ai_enhanced=False,
                    )
        return None

    def _check_page_margin(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> Optional[ValidationResult]:
        """Check page margins against expected values.

        Reads margins from parsed_document.metadata.section which is
        populated by DocumentParser from python-docx section properties.
        """
        section = parsed_document.metadata.section

        if section is None:
            return ValidationResult(
                rule_id=rule.id,
                rule_name=rule.name,
                element_path="document/section",
                expected_value=self._format_margin_params(rule.params),
                actual_value="section properties not available",
                message="Unable to extract page section properties from document",
                severity=Severity(rule.severity.value),
                auto_fixable=False,
                ai_enhanced=False,
            )

        params = rule.params
        tolerance = params.get("tolerance", 0.1)
        unit = params.get("unit", "cm")

        if unit == "cm":
            margin_getter = {
                "top": section.margin_top,
                "bottom": section.margin_bottom,
                "left": section.margin_left,
                "right": section.margin_right,
            }
        else:
            margin_getter = {
                "top": section.margin_top,
                "bottom": section.margin_bottom,
                "left": section.margin_left,
                "right": section.margin_right,
            }

        violations = []

        if "top" in params:
            expected = params["top"]
            actual = margin_getter.get("top")
            if actual is not None and abs(actual - expected) > tolerance:
                violations.append(f"top margin: expected {expected}cm, got {actual:.2f}cm")

        if "bottom" in params:
            expected = params["bottom"]
            actual = margin_getter.get("bottom")
            if actual is not None and abs(actual - expected) > tolerance:
                violations.append(f"bottom margin: expected {expected}cm, got {actual:.2f}cm")

        if "left" in params:
            expected = params["left"]
            actual = margin_getter.get("left")
            if actual is not None and abs(actual - expected) > tolerance:
                violations.append(f"left margin: expected {expected}cm, got {actual:.2f}cm")

        if "right" in params:
            expected = params["right"]
            actual = margin_getter.get("right")
            if actual is not None and abs(actual - expected) > tolerance:
                violations.append(f"right margin: expected {expected}cm, got {actual:.2f}cm")

        if violations:
            return ValidationResult(
                rule_id=rule.id,
                rule_name=rule.name,
                element_path="document/section",
                expected_value=self._format_margin_params(params),
                actual_value="; ".join(violations),
                message=f"Page margin mismatch: {violations[0]}",
                severity=Severity(rule.severity.value),
                auto_fixable=False,
                ai_enhanced=False,
            )

        return None

    def _format_margin_params(self, params: dict) -> str:
        """Format margin parameters for display."""
        parts = []
        for key in ["top", "bottom", "left", "right"]:
            if key in params:
                parts.append(f"{key}={params[key]}cm")
        return ", ".join(parts) if parts else "unknown"

    def _check_heading_level(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> List[ValidationResult]:
        """Check heading levels are sequential (no level jumping).

        e.g., 1 -> 2 -> 3 is valid, but 1 -> 3 is invalid (skipping level 2).
        """
        results = []
        max_level = rule.params.get("max_level", 6)

        heading_elements = [
            (i, elem) for i, elem in enumerate(parsed_document.elements)
            if elem.element_type == "heading"
        ]

        if not heading_elements:
            return results

        previous_level = 0
        for index, element in heading_elements:
            current_level = self._extract_heading_level(element.style or "", element.content)

            if current_level == 0:
                continue

            if previous_level > 0 and current_level > previous_level + 1:
                results.append(ValidationResult(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    element_path=element.path,
                    expected_value=f"level {previous_level + 1} after level {previous_level}",
                    actual_value=f"level {current_level}",
                    message=f"Heading level jumped from {previous_level} to {current_level}. "
                            f"Should not skip levels (found '{element.content[:30]}...')",
                    severity=Severity(rule.severity.value),
                    auto_fixable=False,
                    ai_enhanced=False,
                ))

            if current_level > max_level:
                results.append(ValidationResult(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    element_path=element.path,
                    expected_value=f"level <= {max_level}",
                    actual_value=f"level {current_level}",
                    message=f"Heading level {current_level} exceeds maximum level {max_level} "
                            f"(found '{element.content[:30]}...')",
                    severity=Severity(rule.severity.value),
                    auto_fixable=False,
                    ai_enhanced=False,
                ))

            previous_level = current_level

        return results

    def _extract_heading_level(self, style: str, content: str) -> int:
        """Extract heading level from style name or content.

        Examples:
            'Heading 1' -> 1
            'Title' -> 0 (not a numbered heading)
            '2. Section' -> 2 (content pattern)
        """
        style_lower = style.lower()

        if "heading" in style_lower:
            import re
            match = re.search(r'\d+', style_lower)
            if match:
                return int(match.group())

        if content:
            import re
            match = re.match(r'^(\d+)\.', content.strip())
            if match:
                return int(match.group(1))

        return 0

    def _check_citation_format_pattern(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> List[ValidationResult]:
        """Check citation format matches expected pattern (L2 rule).

        This is a pattern-based check, not AI-enhanced.
        L3 would use AI for more complex citation validation.
        """
        results = []
        expected_style = rule.params.get("style", "academic")

        if expected_style == "academic":
            results.extend(self._check_academic_citation_pattern(parsed_document, rule))
        elif expected_style == "numeric":
            results.extend(self._check_numeric_citation_pattern(parsed_document, rule))

        return results

    def _check_academic_citation_pattern(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> List[ValidationResult]:
        """Check academic citation patterns: (Author, Year) or [Author, Year]."""
        import re
        results = []

        citation_pattern = re.compile(r'[\(\[][^(]\w+[,.]?\s*\d{4}[\)\]]')

        for element in parsed_document.elements:
            if element.element_type == "paragraph":
                matches = citation_pattern.findall(element.content)
                for match in matches:
                    if not self._is_valid_academic_citation(match):
                        results.append(ValidationResult(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            element_path=element.path,
                            expected_value="(Author, Year) format",
                            actual_value=match,
                            message=f"Suspicious citation format: '{match}'. Expected format: (Author, Year) or [Author, Year]",
                            severity=Severity(rule.severity.value),
                            auto_fixable=False,
                            ai_enhanced=False,
                        ))
                        break

        return results

    def _check_numeric_citation_pattern(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> List[ValidationResult]:
        """Check numeric citation patterns: [1] or [1, 2] or [1-3]."""
        import re
        results = []

        numeric_pattern = re.compile(r'\[\d+(?:[\s,;\-]+\d+)*\]')

        for element in parsed_document.elements:
            if element.element_type == "paragraph":
                matches = numeric_pattern.findall(element.content)
                for match in matches:
                    if not self._is_valid_numeric_citation(match):
                        results.append(ValidationResult(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            element_path=element.path,
                            expected_value="[1] or [1, 2] or [1-3] format",
                            actual_value=match,
                            message=f"Invalid numeric citation format: '{match}'",
                            severity=Severity(rule.severity.value),
                            auto_fixable=False,
                            ai_enhanced=False,
                        ))
                        break

        return results

    def _is_valid_academic_citation(self, citation: str) -> bool:
        """Validate academic citation format."""
        import re
        patterns = [
            r'\([A-Z][a-z]+,?\s*\d{4}[,.]?\s*[a-z]?\)',
            r'\[[A-Z][a-z]+,?\s*\d{4}[,.]?\s*[a-z]?\]',
        ]
        return any(re.match(p, citation) for p in patterns)

    def _is_valid_numeric_citation(self, citation: str) -> bool:
        """Validate numeric citation format."""
        import re
        pattern = r'^\[\d+(?:[\s,;\-]+\d+)*\]$'
        return bool(re.match(pattern, citation))

    def _check_generic_rule(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> List[ValidationResult]:
        """Generic rule checker for unknown rule IDs."""
        results = []
        expected_value = rule.params.get("expected_value")

        if not expected_value:
            return results

        for element in parsed_document.elements:
            actual_value = self._get_element_property(element, rule.id)
            if actual_value and actual_value != expected_value:
                results.append(ValidationResult(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    element_path=element.path,
                    expected_value=str(expected_value),
                    actual_value=str(actual_value),
                    message=f"Expected {rule.name} to be '{expected_value}' but found '{actual_value}'",
                    severity=Severity(rule.severity.value),
                    auto_fixable=rule.auto_fixable,
                    ai_enhanced=False,
                ))
                break

        return results

    def _get_element_property(
        self,
        element: DocumentElement,
        rule_id: str,
    ) -> Any:
        """Get element property based on rule ID."""
        if "font" in rule_id.lower() and "name" in rule_id.lower():
            return element.properties.font_name
        if "size" in rule_id.lower():
            return element.properties.font_size
        if "spacing" in rule_id.lower() or "line" in rule_id.lower():
            return element.properties.line_spacing
        return None

    def _validate_with_ai(
        self,
        parsed_document: ParsedDocument,
        rule: ValidationRule,
    ) -> List[ValidationResult]:
        """Execute an AI-enhanced (L3) rule."""
        results = []

        if not self.ai_enhancement.is_enabled():
            return results

        if rule.id == "citation_format":
            for element in parsed_document.elements:
                if self._looks_like_citation(element.content):
                    analysis = self.ai_enhancement.analyze_citation_format(element.content)
                    result = self.ai_enhancement.create_ai_result(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        element_path=element.path,
                        analysis_result=analysis,
                    )
                    results.append(result)

        elif rule.id == "reference_format":
            for element in parsed_document.elements:
                if self._looks_like_reference(element.content):
                    analysis = self.ai_enhancement.analyze_reference_format(element.content)
                    result = self.ai_enhancement.create_ai_result(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        element_path=element.path,
                        analysis_result=analysis,
                    )
                    results.append(result)

        return results

    def _looks_like_citation(self, content: str) -> bool:
        """Check if content looks like a citation."""
        citation_markers = ["(", ")", "[", "]"]
        return any(marker in content for marker in citation_markers) and len(content) < 200

    def _looks_like_reference(self, content: str) -> bool:
        """Check if content looks like a reference entry."""
        reference_indicators = [".", "doi:", "http", "://"]
        return any(indicator in content.lower() for indicator in reference_indicators)