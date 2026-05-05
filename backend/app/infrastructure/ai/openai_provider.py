"""AI provider supporting OpenAI and Ollama-compatible APIs."""

from typing import Optional
import json
from app.core.config import settings


try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider:
    """OpenAI API provider for L3 rule AI enhancement.

    Supports both OpenAI and Ollama-compatible endpoints.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None,
                 base_url: Optional[str] = None):
        self._timeout = settings.ai_timeout
        self._base_url = base_url
        self._client = None
        self._provider = settings.ai_provider

        # Get API key, model, base_url based on provider
        if self._provider == "deepseek":
            self._api_key = api_key or settings.deepseek_api_key
            self._model = model or settings.deepseek_model
            self._base_url = base_url or settings.deepseek_base_url
        elif self._provider == "ollama":
            self._api_key = api_key or settings.ollama_api_key
            self._model = model or settings.ollama_model
            self._base_url = base_url or settings.ollama_base_url
        else:  # openai
            self._api_key = api_key or settings.openai_api_key
            self._model = model or settings.openai_model
            self._base_url = base_url

        if OPENAI_AVAILABLE and self._api_key:
            self._init_client()

    def _init_client(self):
        """Initialize the appropriate client based on provider."""
        if self._provider == "ollama":
            self._client = openai.OpenAI(
                api_key=self._api_key or "ollama",
                base_url=self._base_url or settings.ollama_base_url,
            )
        elif self._provider == "deepseek":
            self._client = openai.OpenAI(
                api_key=self._api_key,
                base_url=self._base_url or settings.deepseek_base_url,
            )
        else:
            self._client = openai.OpenAI(api_key=self._api_key)

    def is_configured(self) -> bool:
        """Check if provider is properly configured."""
        return self._client is not None

    def analyze_citation(self, citation_text: str) -> dict:
        """Analyze citation format.

        Args:
            citation_text: The citation text to analyze

        Returns:
            Analysis result dict with is_valid, confidence, suggestions
        """
        if not self.is_configured():
            return {
                "is_valid": False,
                "confidence": 0.0,
                "suggestions": ["OpenAI API not configured"],
            }

        prompt = self._build_citation_prompt(citation_text)
        response = self._call_openai(prompt)

        if not response:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "suggestions": ["Failed to analyze citation"],
            }

        return self._parse_citation_response(response)

    def analyze_reference(self, reference_text: str) -> dict:
        """Analyze reference format.

        Args:
            reference_text: The reference text to analyze

        Returns:
            Analysis result dict with is_valid, confidence, suggestions
        """
        if not self.is_configured():
            return {
                "is_valid": False,
                "confidence": 0.0,
                "suggestions": ["OpenAI API not configured"],
            }

        prompt = self._build_reference_prompt(reference_text)
        response = self._call_openai(prompt)

        if not response:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "suggestions": ["Failed to analyze reference"],
            }

        return self._parse_reference_response(response)

    def _build_citation_prompt(self, citation_text: str) -> str:
        """Build prompt for citation analysis."""
        return f"""Analyze the following academic citation for format compliance.

Citation: {citation_text}

Respond with JSON only:
{{"is_valid": true/false, "confidence": 0.0-1.0, "suggestions": ["suggestion1", "suggestion2"]}}

Rules:
- Valid formats: (Author, Year), (Author, Year, p.X), [1], [1,2,3]
- Invalid: incomplete author names, missing year, malformed brackets"""

    def _build_reference_prompt(self, reference_text: str) -> str:
        """Build prompt for reference analysis."""
        return f"""Analyze the following academic reference entry for format compliance.

Reference: {reference_text}

Respond with JSON only:
{{"is_valid": true/false, "confidence": 0.0-1.0, "suggestions": ["suggestion1", "suggestion2"]}}

Rules for valid academic reference:
- Author(s) in correct order
- Year in correct position
- Title properly formatted
- Journal/Publisher information present
- DOI or URL if applicable"""

    def _call_openai(self, prompt: str) -> Optional[str]:
        """Make a call to OpenAI API.

        Args:
            prompt: The prompt to send

        Returns:
            The response text or None on error
        """
        if not self._client:
            return None

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a citation and reference format expert. Always respond with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=200,
                timeout=self._timeout,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def _parse_citation_response(self, response: str) -> dict:
        """Parse citation analysis response."""
        try:
            data = json.loads(response)
            return {
                "is_valid": data.get("is_valid", False),
                "confidence": data.get("confidence", 0.0),
                "suggestions": data.get("suggestions", []),
            }
        except json.JSONDecodeError:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "suggestions": ["Failed to parse AI response"],
            }

    def _parse_reference_response(self, response: str) -> dict:
        """Parse reference analysis response."""
        return self._parse_citation_response(response)