"""Template application use cases."""

from typing import List, Optional
from uuid import UUID

from app.domain.entities.template import Template, DegreeType
from app.domain.repositories import ITemplateRepository


class TemplateUseCases:
    """Application use cases for template operations."""

    def __init__(self, template_repository: ITemplateRepository):
        self._repo = template_repository

    def create_template(
        self,
        university: str,
        degree_type: DegreeType,
        discipline: str,
        version: str = "1.0",
    ) -> Template:
        """Create a new template.

        Args:
            university: University name
            degree_type: Degree type (bachelor/master/doctor)
            discipline: Academic discipline
            version: Template version

        Returns:
            The created Template
        """
        template = Template(
            university=university,
            degree_type=degree_type,
            discipline=discipline,
            version=version,
        )
        self._repo.save(template)
        return template

    def get_template(self, template_id: UUID) -> Optional[Template]:
        """Get a template by ID."""
        return self._repo.find_by_id(template_id)

    def list_templates(
        self,
        university: Optional[str] = None,
        degree_type: Optional[DegreeType] = None,
    ) -> List[Template]:
        """List templates with optional filters."""
        if university:
            return self._repo.find_by_university(
                university,
                degree_type.value if degree_type else None,
            )
        return self._repo.find_active()

    def update_template(self, template: Template) -> None:
        """Update a template."""
        self._repo.update(template)

    def deactivate_template(self, template_id: UUID) -> None:
        """Deactivate a template."""
        template = self._repo.find_by_id(template_id)
        if template:
            template.is_active = False
            self._repo.update(template)