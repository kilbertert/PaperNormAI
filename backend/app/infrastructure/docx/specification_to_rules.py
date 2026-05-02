"""Specification document to rules pipeline.

Orchestrates the extraction of rules from a specification document
using pattern-based extraction (L1/L2) and AI enhancement (L3).
"""

from typing import List, Optional, Dict
from pathlib import Path
from dataclasses import dataclass

from app.infrastructure.docx.document_parser import DocumentParser, ParsedDocument
from app.infrastructure.docx.rule_pattern_extractor import RulePatternExtractor, ExtractedRule
from app.domain.entities.validation_rule import ValidationRule, RuleLevel, Severity


@dataclass
class ExtractionResult:
    """Result of rule extraction from specification."""
    rules: List[ValidationRule]
    unparsed_sections: List[str]
    extraction_summary: Dict


class SpecificationToRulesPipeline:
    """Converts a specification document into ValidationRule objects.

    Flow:
    1. Parse specification .docx with DocumentParser
    2. Split into logical sections (摘要, 目录, 正文, etc.)
    3. Run RulePatternExtractor on each section
    4. For complex rules, use AI enhancement (L3)
    5. Return standardized ValidationRule list
    """

    def __init__(self, ai_enhancement=None):
        """Initialize pipeline.

        Args:
            ai_enhancement: Optional AIEnhancementService for L3 rules
        """
        self.document_parser = DocumentParser()
        self.pattern_extractor = RulePatternExtractor()
        self.ai_enhancement = ai_enhancement

    def process(self, spec_file_path: Path) -> ExtractionResult:
        """Process a specification document and extract rules.

        Args:
            spec_file_path: Path to the specification .docx file

        Returns:
            ExtractionResult with rules and metadata
        """
        parsed_doc = self.document_parser.parse(spec_file_path)

        sections = self._split_into_sections(parsed_doc)

        all_extracted_rules = []
        unparsed_sections = []

        for section_name, section_content in sections.items():
            extracted = self.pattern_extractor.extract_rules_from_text(section_content)
            if extracted:
                all_extracted_rules.extend(extracted)
            else:
                if len(section_content) > 50:
                    unparsed_sections.append(section_content[:200])

        normalized_rules = self._normalize_rules(all_extracted_rules)

        summary = {
            "total_rules": len(normalized_rules),
            "l1_rules": sum(1 for r in normalized_rules if r.level == RuleLevel.L1),
            "l2_rules": sum(1 for r in normalized_rules if r.level == RuleLevel.L2),
            "l3_rules": sum(1 for r in normalized_rules if r.level == RuleLevel.L3),
            "sections_processed": len(sections),
            "unparsed_sections_count": len(unparsed_sections),
        }

        return ExtractionResult(
            rules=normalized_rules,
            unparsed_sections=unparsed_sections,
            extraction_summary=summary,
        )

    def _split_into_sections(self, parsed_doc: ParsedDocument) -> Dict[str, str]:
        """Split document into logical sections based on heading structure.

        Returns:
            Dict of section_name -> section_text
        """
        sections = {}
        current_section = "general"
        current_content = []

        section_markers = [
            "毕业论文（设计）排版规范",
            "中文摘要和关键词",
            "英文摘要和关键词",
            "目录",
            "前言",
            "正文",
            "图",
            "表格",
            "公式",
            "参考文献",
            "附录",
            "致谢",
        ]

        for element in parsed_doc.elements:
            if element.element_type == "heading":
                text = element.content

                matched_section = None
                for marker in section_markers:
                    if marker in text:
                        matched_section = marker
                        break

                if matched_section:
                    if current_content:
                        sections[current_section] = "\n".join(current_content)
                    current_section = matched_section
                    current_content = []
                else:
                    current_content.append(text)
            else:
                current_content.append(element.content)

        if current_content:
            sections[current_section] = "\n".join(current_content)

        return sections

    def _normalize_rules(self, extracted_rules: List[ExtractedRule]) -> List[ValidationRule]:
        """Convert ExtractedRule objects to ValidationRule domain entities.

        Merges rules with the same handler ID by combining their params.
        This ensures each RuleEngine handler gets one rule with all relevant params.

        Args:
            extracted_rules: List of pattern-extracted rules

        Returns:
            List of ValidationRule domain entities (one per unique handler ID)
        """
        # Group rules by handler ID
        rules_by_handler: Dict[str, List[ExtractedRule]] = {}
        for extracted in extracted_rules:
            handler_id = extracted.rule_id
            if handler_id not in rules_by_handler:
                rules_by_handler[handler_id] = []
            rules_by_handler[handler_id].append(extracted)

        # Merge params for each handler ID
        merged_rules = []
        for handler_id, rules_list in rules_by_handler.items():
            merged_params = self._merge_rule_params(rules_list)

            # Use the most severe severity among merged rules
            severities = [r.severity for r in rules_list]
            if 'error' in severities:
                merged_severity = Severity.ERROR
            elif 'warning' in severities:
                merged_severity = Severity.WARNING
            else:
                merged_severity = Severity.INFO

            # Use description from first rule
            merged_description = rules_list[0].description

            # Check if any rule is auto-fixable
            merged_auto_fixable = any(r.auto_fixable for r in rules_list)

            # Use highest level among merged rules
            levels = [self._map_level(r.level) for r in rules_list]
            merged_level = max(levels, key=lambda l: l.value if hasattr(l, 'value') else l)

            rule = ValidationRule(
                id=handler_id,
                name=rules_list[0].name,
                level=merged_level,
                description=merged_description,
                severity=merged_severity,
                auto_fixable=merged_auto_fixable,
                params=merged_params,
            )
            merged_rules.append(rule)

        return merged_rules

    def _merge_rule_params(self, rules_list: List[ExtractedRule]) -> Dict:
        """Merge params from multiple rules into a single params dict.

        Merging strategy:
        - For numeric values (margins, sizes): take the first non-None value
        - For list values (allowed_fonts): merge and dedupe
        - For string values: take first non-None value
        - For nested dicts: recursively merge
        - Special handling: expected_font -> add to allowed_fonts

        Args:
            rules_list: List of rules with same handler ID

        Returns:
            Merged params dict
        """
        merged = {}

        for rule in rules_list:
            params = rule.params
            for key, value in params.items():
                if value is None:
                    continue

                if key == 'expected_font':
                    # expected_font should populate allowed_fonts
                    if 'allowed_fonts' not in merged:
                        merged['allowed_fonts'] = []
                    if value not in merged['allowed_fonts']:
                        merged['allowed_fonts'].append(value)
                    if 'expected_value' not in merged:
                        merged['expected_value'] = value
                elif key not in merged:
                    merged[key] = value
                else:
                    existing = merged[key]
                    # Merge based on value type
                    if isinstance(value, list) and isinstance(existing, list):
                        # Merge lists and remove duplicates while preserving order
                        combined = existing + value
                        if key == 'allowed_fonts':
                            # Dedupe for font-related lists
                            merged[key] = list(dict.fromkeys(combined))
                        else:
                            merged[key] = combined
                    elif isinstance(value, (int, float)) and isinstance(existing, (int, float)):
                        # For margins, take first value (they should be consistent)
                        pass  # Keep existing
                    elif isinstance(value, dict) and isinstance(existing, dict):
                        # Recursively merge nested dicts
                        merged[key] = self._merge_nested_params(existing, value)
                    # For strings, keep existing (first value wins)

        return merged

    def _merge_nested_params(self, existing: Dict, new: Dict) -> Dict:
        """Recursively merge nested params dicts."""
        result = existing.copy()
        for key, value in new.items():
            if key not in result:
                result[key] = value
            elif isinstance(value, dict) and isinstance(result[key], dict):
                result[key] = self._merge_nested_params(result[key], value)
            # Keep existing for non-dict values
        return result

    def _map_level(self, level_str: str) -> RuleLevel:
        """Map level string to RuleLevel enum."""
        level_map = {
            "L1": RuleLevel.L1,
            "L2": RuleLevel.L2,
            "L3": RuleLevel.L3,
        }
        return level_map.get(level_str, RuleLevel.L1)
