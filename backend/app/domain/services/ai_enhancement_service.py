"""AI Enhancement domain service."""

from typing import Optional
from app.infrastructure.ai.openai_provider import OpenAIProvider
from app.domain.entities.validation_result import ValidationResult, Severity


class AIEnhancementService:
    """Domain service for AI-enhanced validations (L3 rules)."""

    def __init__(self, openai_provider: Optional[OpenAIProvider] = None):
        self._enabled = False
        self._provider = openai_provider or OpenAIProvider()

    def enable(self) -> None:
        """Enable AI enhancement."""
        self._enabled = True

    def disable(self) -> None:
        """Disable AI enhancement."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if AI enhancement is enabled."""
        return self._enabled

    def is_available(self) -> bool:
        """Check if AI provider is configured and available."""
        return self._provider.is_configured()

    def analyze_citation_format(self, citation_text: str) -> dict:
        """Analyze citation format for compliance.

        Returns dict with:
            - is_valid: bool
            - confidence: float
            - suggestions: list[str]
        """
        if not self._provider.is_configured():
            return {
                "is_valid": False,
                "confidence": 0.0,
                "suggestions": ["AI provider not configured"],
            }

        return self._provider.analyze_citation(citation_text)

    def analyze_reference_format(self, reference_text: str) -> dict:
        """Analyze reference format for compliance.

        Returns dict with:
            - is_valid: bool
            - confidence: float
            - suggestions: list[str]
        """
        if not self._provider.is_configured():
            return {
                "is_valid": False,
                "confidence": 0.0,
                "suggestions": ["AI provider not configured"],
            }

        return self._provider.analyze_reference(reference_text)

    def create_ai_result(
        self,
        rule_id: str,
        rule_name: str,
        element_path: str,
        analysis_result: dict,
    ) -> ValidationResult:
        """Create a ValidationResult from AI analysis."""
        suggestions = analysis_result.get("suggestions", [])
        actual_value = suggestions[0] if suggestions else "unknown"

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            element_path=element_path,
            expected_value="compliant format",
            actual_value=actual_value,
            message="; ".join(suggestions) if suggestions else "AI analysis complete",
            severity=Severity.WARNING,
            auto_fixable=False,
            ai_enhanced=True,
            confidence=analysis_result.get("confidence", 0.0),
        )