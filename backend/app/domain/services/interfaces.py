"""Abstract interfaces (ports) for domain services.

These interfaces define the contract that infrastructure layer must implement.
Domain layer depends on these abstractions, not on concrete infrastructure classes.

This follows the Dependency Inversion Principle:
- Domain defines interfaces (what it needs)
- Infrastructure implements them (how it's done)
- Application layer wires them together (who provides what)
"""

from typing import Protocol, List, Dict, Optional
from uuid import UUID


class IDocumentParser(Protocol):
    """Abstract interface for document parsing.

    Implemented by: DoclingDocumentParser, DocumentParser
    """

    def parse(self, file_path) -> "ParsedDocumentLike":
        """Parse a document file into an intermediate model.

        Returns:
            A document model containing paragraphs, tables, figures, etc.
        """
        ...


class ParsedDocumentLike(Protocol):
    """Protocol for parsed document models returned by IDocumentParser.

    Used to type-hint return values without coupling to concrete classes.
    """
    pass


class IAIProvider(Protocol):
    """Abstract interface for AI providers.

    Implemented by: OpenAIProvider (supports DeepSeek/Ollama/OpenAI)
    """

    def is_configured(self) -> bool:
        """Check if provider is properly configured."""
        ...

    def analyze_citation(self, citation_text: str) -> dict:
        """Analyze citation format compliance."""
        ...

    def analyze_reference(self, reference_text: str) -> dict:
        """Analyze reference format compliance."""
        ...

    def extract_rules(self, content: str) -> List[Dict[str, str]]:
        """Extract rules from spec document content."""
        ...

    def validate_semantics(
        self,
        thesis_content: str,
        rules: List[Dict[str, str]],
        page_format: dict,
    ) -> str:
        """Perform semantic validation and return AI response text."""
        ...


class IDocumentMerger(Protocol):
    """Abstract interface for document merging/correction.

    Implemented by: DocumentMerger (AI-Word-Skill pattern)
    """

    def merge(self, original_doc_path, corrections: List[Dict]) -> "PathLike":
        """Merge corrections into the original document.

        Returns:
            Path to the corrected document.
        """
        ...

    @property
    def using_ai_word_skill(self) -> bool:
        """Returns True if using AI-Word-Skill merge pattern."""
        ...


class IDocumentWriter(Protocol):
    """Abstract interface for document writing.

    Implemented by: DocumentWriter
    """

    def write_to_docx(self, parsed_document, output_path) -> None:
        """Write a parsed document to a .docx file."""
        ...

    def apply_corrections(self, parsed_document, plans) -> "ParsedDocumentLike":
        """Apply correction plans to a parsed document."""
        ...


class PathLike(Protocol):
    """Protocol for path-like objects."""
    pass