"""Template repository implementation using SQLAlchemy."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.domain.entities.template import Template, DegreeType
from app.domain.repositories import ITemplateRepository
from app.infrastructure.persistence.models import TemplateModel
from app.infrastructure.persistence.mappers import TemplateMapper


class TemplateRepository(ITemplateRepository):
    """SQLAlchemy implementation of TemplateRepository."""

    def __init__(self, db: Session):
        self._db = db

    def save(self, template: Template) -> None:
        """Save a template to database."""
        model = TemplateMapper.to_model(template)
        self._db.add(model)
        self._db.commit()

    def find_by_id(self, template_id: UUID) -> Optional[Template]:
        """Find a template by ID."""
        model = self._db.query(TemplateModel).filter(
            TemplateModel.id == template_id
        ).first()

        if model is None:
            return None

        return TemplateMapper.to_domain(model)

    def find_by_university(
        self,
        university: str,
        degree_type: Optional[str] = None,
    ) -> List[Template]:
        """Find templates by university."""
        query = self._db.query(TemplateModel).filter(
            TemplateModel.university == university,
            TemplateModel.is_active == True,
        )

        if degree_type:
            query = query.filter(TemplateModel.degree_type == degree_type)

        models = query.order_by(TemplateModel.discipline).all()
        return [TemplateMapper.to_domain(m) for m in models]

    def find_active(self) -> List[Template]:
        """Find all active templates."""
        models = self._db.query(TemplateModel).filter(
            TemplateModel.is_active == True
        ).order_by(
            TemplateModel.university,
            TemplateModel.degree_type,
            TemplateModel.discipline,
        ).all()

        return [TemplateMapper.to_domain(m) for m in models]

    def update(self, template: Template) -> None:
        """Update a template."""
        model = self._db.query(TemplateModel).filter(
            TemplateModel.id == template.id
        ).first()

        if model is None:
            raise ValueError(f"Template not found: {template.id}")

        model.university = template.university
        model.degree_type = template.degree_type.value
        model.discipline = template.discipline
        model.version = template.version
        model.rules_json = TemplateMapper.to_model(template).rules_json
        model.file_path = template.file_path
        model.is_active = template.is_active
        model.updated_at = datetime.utcnow()

        self._db.commit()

    def deactivate(self, template_id: UUID) -> None:
        """Deactivate a template."""
        model = self._db.query(TemplateModel).filter(
            TemplateModel.id == template_id
        ).first()

        if model:
            model.is_active = False
            model.updated_at = datetime.utcnow()
            self._db.commit()

    def find_by_discipline(self, discipline: str) -> List[Template]:
        """Find templates by discipline."""
        models = self._db.query(TemplateModel).filter(
            TemplateModel.discipline == discipline,
            TemplateModel.is_active == True,
        ).all()

        return [TemplateMapper.to_domain(m) for m in models]

    def count_active(self) -> int:
        """Count active templates."""
        return self._db.query(TemplateModel).filter(
            TemplateModel.is_active == True
        ).count()