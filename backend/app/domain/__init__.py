"""Domain module.

Contains domain entities, value objects, domain services, and repository interfaces.
This is the heart of the application's business logic.

Domain layer rules:
- No infrastructure dependencies (no database, no external APIs)
- Pure business logic
- Defines interfaces (protocols) that infrastructure must implement
"""

from app.domain.entities import Document, Template, ValidationRule, ValidationResult

__all__ = [
    "Document",
    "Template",
    "ValidationRule",
    "ValidationResult",
]