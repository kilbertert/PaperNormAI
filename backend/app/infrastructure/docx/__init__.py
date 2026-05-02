"""Infrastructure DOCX parsing module."""

from app.infrastructure.docx.document_parser import DocumentParser, ParsedDocument, DocumentElement
from app.infrastructure.docx.document_writer import DocumentWriter
from app.infrastructure.docx.rule_pattern_extractor import RulePatternExtractor, ExtractedRule
from app.infrastructure.docx.specification_to_rules import SpecificationToRulesPipeline, ExtractionResult

__all__ = [
    "DocumentParser",
    "ParsedDocument",
    "DocumentElement",
    "DocumentWriter",
    "RulePatternExtractor",
    "ExtractedRule",
    "SpecificationToRulesPipeline",
    "ExtractionResult",
]
