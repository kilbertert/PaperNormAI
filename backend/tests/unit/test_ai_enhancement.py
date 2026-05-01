"""Unit tests for AI Enhancement Service and OpenAI Provider."""

import pytest
from unittest.mock import MagicMock, patch

from app.domain.services.ai_enhancement_service import AIEnhancementService
from app.infrastructure.ai.openai_provider import OpenAIProvider
from app.domain.entities.validation_result import Severity


class TestAIEnhancementService:
    """Tests for AIEnhancementService."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock OpenAI provider."""
        provider = MagicMock(spec=OpenAIProvider)
        provider.is_configured.return_value = True
        provider.analyze_citation.return_value = {
            "is_valid": True,
            "confidence": 0.9,
            "suggestions": ["格式正确"],
        }
        provider.analyze_reference.return_value = {
            "is_valid": True,
            "confidence": 0.85,
            "suggestions": ["参考文献格式规范"],
        }
        return provider

    @pytest.fixture
    def ai_service(self, mock_provider):
        """Create AIEnhancementService with mock provider."""
        return AIEnhancementService(openai_provider=mock_provider)

    def test_enable_disable(self, ai_service):
        """Test AI enhancement can be enabled and disabled."""
        assert not ai_service.is_enabled()
        ai_service.enable()
        assert ai_service.is_enabled()
        ai_service.disable()
        assert not ai_service.is_enabled()

    def test_is_available_when_provider_configured(self, ai_service):
        """Test is_available returns True when provider is configured."""
        assert ai_service.is_available()

    def test_is_available_when_provider_not_configured(self):
        """Test is_available returns False when provider is not configured."""
        provider = MagicMock(spec=OpenAIProvider)
        provider.is_configured.return_value = False
        service = AIEnhancementService(openai_provider=provider)
        assert not service.is_available()

    def test_analyze_citation_calls_provider(self, ai_service, mock_provider):
        """Test analyze_citation_format delegates to provider."""
        result = ai_service.analyze_citation_format("(Author, 2024)")
        assert result["is_valid"] is True
        mock_provider.analyze_citation.assert_called_once_with("(Author, 2024)")

    def test_analyze_reference_calls_provider(self, ai_service, mock_provider):
        """Test analyze_reference_format delegates to provider."""
        result = ai_service.analyze_reference_format("Author, A. (2024). Title.")
        assert result["is_valid"] is True
        mock_provider.analyze_reference.assert_called_once_with("Author, A. (2024). Title.")

    def test_create_ai_result_creates_valid_result(self, ai_service):
        """Test create_ai_result creates ValidationResult."""
        analysis = {
            "is_valid": False,
            "confidence": 0.75,
            "suggestions": ["建议1", "建议2"],
        }
        result = ai_service.create_ai_result(
            rule_id="citation_format",
            rule_name="引用格式",
            element_path="paragraph[1]",
            analysis_result=analysis,
        )
        assert result.rule_id == "citation_format"
        assert result.ai_enhanced is True
        assert result.confidence == 0.75
        assert "建议1" in result.message
        assert result.severity == Severity.WARNING

    def test_analyze_when_provider_not_configured(self):
        """Test analysis returns error when provider not configured."""
        provider = MagicMock(spec=OpenAIProvider)
        provider.is_configured.return_value = False
        service = AIEnhancementService(openai_provider=provider)

        result = service.analyze_citation_format("test")
        assert result["is_valid"] is False
        assert "not configured" in result["suggestions"][0]


class TestOpenAIProvider:
    """Tests for OpenAIProvider."""

    def test_is_configured_returns_true_when_api_key_set(self):
        """Test is_configured returns True when API key is provided."""
        with patch.object(OpenAIProvider, '__init__', lambda self, api_key=None: None):
            provider = OpenAIProvider()
            provider._api_key = "test-key"
            provider._client = MagicMock()
            assert provider.is_configured()

    def test_is_configured_returns_false_when_no_api_key(self):
        """Test is_configured returns False when no API key."""
        with patch.object(OpenAIProvider, '__init__', lambda self, api_key=None: None):
            provider = OpenAIProvider()
            provider._api_key = ""
            provider._client = None
            assert not provider.is_configured()

    def test_analyze_citation_returns_error_when_not_configured(self):
        """Test analyze_citation returns error when not configured."""
        with patch.object(OpenAIProvider, '__init__', lambda self, api_key=None: None):
            provider = OpenAIProvider()
            provider._client = None

            result = provider.analyze_citation("(Author, 2024)")
            assert result["is_valid"] is False
            assert "not configured" in result["suggestions"][0]

    def test_analyze_reference_returns_error_when_not_configured(self):
        """Test analyze_reference returns error when not configured."""
        with patch.object(OpenAIProvider, '__init__', lambda self, api_key=None: None):
            provider = OpenAIProvider()
            provider._client = None

            result = provider.analyze_reference("Author, A. (2024). Title.")
            assert result["is_valid"] is False
            assert "not configured" in result["suggestions"][0]

    def test_parse_citation_response_valid_json(self):
        """Test _parse_citation_response handles valid JSON."""
        with patch.object(OpenAIProvider, '__init__', lambda self, api_key=None: None):
            provider = OpenAIProvider()
            response = '{"is_valid": true, "confidence": 0.9, "suggestions": ["ok"]}'
            result = provider._parse_citation_response(response)
            assert result["is_valid"] is True
            assert result["confidence"] == 0.9

    def test_parse_citation_response_invalid_json(self):
        """Test _parse_citation_response handles invalid JSON."""
        with patch.object(OpenAIProvider, '__init__', lambda self, api_key=None: None):
            provider = OpenAIProvider()
            response = "not valid json"
            result = provider._parse_citation_response(response)
            assert result["is_valid"] is False
            assert "Failed to parse" in result["suggestions"][0]

    def test_build_citation_prompt(self):
        """Test _build_citation_prompt returns non-empty string."""
        with patch.object(OpenAIProvider, '__init__', lambda self, api_key=None: None):
            provider = OpenAIProvider()
            prompt = provider._build_citation_prompt("(Author, 2024)")
            assert len(prompt) > 0
            assert "Citation" in prompt

    def test_build_reference_prompt(self):
        """Test _build_reference_prompt returns non-empty string."""
        with patch.object(OpenAIProvider, '__init__', lambda self, api_key=None: None):
            provider = OpenAIProvider()
            prompt = provider._build_reference_prompt("Author, A. (2024). Title.")
            assert len(prompt) > 0
            assert "Reference" in prompt