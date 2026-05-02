"""TemplateService domain service."""

from typing import List, Optional
from uuid import UUID
from app.domain.entities.template import Template
from app.domain.repositories import ITemplateRepository


class TemplateService:
    """Domain service for managing templates."""

    def __init__(self, repository: ITemplateRepository):
        self._repository = repository

    def get_template(self, template_id: UUID) -> Optional[Template]:
        """Get a template by ID with caching."""
        return self._repository.find_by_id(template_id)

    def list_templates(
        self,
        university: Optional[str] = None,
        degree_type: Optional[str] = None,
    ) -> List[Template]:
        """List templates with optional filters."""
        if university:
            return self._repository.find_by_university(university, degree_type)
        return self._repository.find_active()

    def validate_template(self, template: Template) -> bool:
        """Validate that a template has all required rules."""
        if not template.rules:
            return False
        required_rule_names = {"font_name", "font_size", "line_spacing"}
        actual_rule_names = {r.name for r in template.rules}
        return required_rule_names.issubset(actual_rule_names)