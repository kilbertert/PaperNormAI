"""Template management endpoints."""

from typing import Optional
from uuid import UUID
import json

from fastapi import APIRouter, HTTPException, Query, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user, CurrentUser
from app.infrastructure.persistence.template_repository import TemplateRepository
from app.infrastructure.persistence.models import TemplateModel

router = APIRouter()


class TemplateRule(BaseModel):
    id: str
    name: str
    level: str
    description: str
    auto_fixable: bool


class TemplateResponse(BaseModel):
    id: str
    university: str
    degree_type: str
    discipline: str
    version: str
    is_active: bool
    rules: list[TemplateRule] = []
    file_path: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TemplateListResponse(BaseModel):
    items: list[TemplateResponse]
    total: int


class TemplateCreateRequest(BaseModel):
    university: str
    degree_type: str
    discipline: str
    version: str = "1.0"
    rules: list[dict] = []
    file_path: Optional[str] = None


class TemplateUpdateRequest(BaseModel):
    university: Optional[str] = None
    degree_type: Optional[str] = None
    discipline: Optional[str] = None
    version: Optional[str] = None
    rules: Optional[list[dict]] = None
    file_path: Optional[str] = None
    is_active: Optional[bool] = None


def _parse_rules_from_json(rules_json: str) -> list[TemplateRule]:
    """Parse rules from JSON string."""
    rules = []
    try:
        rules_data = json.loads(rules_json) if rules_json else []
        for r in rules_data:
            rules.append(TemplateRule(
                id=r.get('id', ''),
                name=r.get('name', ''),
                level=r.get('level', 'L1'),
                description=r.get('description', ''),
                auto_fixable=r.get('auto_fixable', False),
            ))
    except (json.JSONDecodeError, KeyError):
        pass
    return rules


@router.get("/", response_model=TemplateListResponse)
async def list_templates(
    university: Optional[str] = Query(None),
    degree_type: Optional[str] = Query(None),
    discipline: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List available templates with optional filters."""
    repo = TemplateRepository(db)

    if university:
        templates = repo.find_by_university(university, degree_type)
        total = len(templates)
    elif discipline:
        templates = repo.find_by_discipline(discipline)
        total = len(templates)
    else:
        templates = repo.find_active()
        total = repo.count_active()

    offset = (page - 1) * page_size
    templates = templates[offset:offset + page_size]

    items = []
    for t in templates:
        template_model = db.query(TemplateModel).filter(
            TemplateModel.id == t.id
        ).first()

        rules = _parse_rules_from_json(template_model.rules_json) if template_model else []

        items.append(TemplateResponse(
            id=str(t.id),
            university=t.university,
            degree_type=t.degree_type,
            discipline=t.discipline,
            version=t.version,
            is_active=t.is_active,
            rules=rules,
            file_path=t.file_path,
            created_at=t.created_at.isoformat() if t.created_at else None,
            updated_at=t.updated_at.isoformat() if t.updated_at else None,
        ))

    return TemplateListResponse(items=items, total=total)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
):
    """Get template details including rules."""
    try:
        uid = UUID(template_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid template ID format")

    repo = TemplateRepository(db)
    template = repo.find_by_id(uid)

    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    template_model = db.query(TemplateModel).filter(
        TemplateModel.id == uid
    ).first()

    rules = _parse_rules_from_json(template_model.rules_json) if template_model else []

    return TemplateResponse(
        id=str(template.id),
        university=template.university,
        degree_type=template.degree_type,
        discipline=template.discipline,
        version=template.version,
        is_active=template.is_active,
        rules=rules,
        file_path=template.file_path,
        created_at=template.created_at.isoformat() if template.created_at else None,
        updated_at=template.updated_at.isoformat() if template.updated_at else None,
    )


@router.post("/", response_model=TemplateResponse, status_code=201)
async def create_template(
    request: TemplateCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new template."""
    template_model = TemplateModel(
        university=request.university,
        degree_type=request.degree_type.lower(),
        discipline=request.discipline,
        version=request.version,
        rules_json=json.dumps(request.rules),
        file_path=request.file_path,
        is_active=True,
    )

    db.add(template_model)
    db.commit()
    db.refresh(template_model)

    return TemplateResponse(
        id=str(template_model.id),
        university=template_model.university,
        degree_type=template_model.degree_type,
        discipline=template_model.discipline,
        version=template_model.version,
        is_active=template_model.is_active,
        rules=[],
        file_path=template_model.file_path,
        created_at=template_model.created_at.isoformat() if template_model.created_at else None,
        updated_at=template_model.updated_at.isoformat() if template_model.updated_at else None,
    )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    request: TemplateUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing template."""
    try:
        uid = UUID(template_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid template ID format")

    template_model = db.query(TemplateModel).filter(
        TemplateModel.id == uid
    ).first()

    if template_model is None:
        raise HTTPException(status_code=404, detail="Template not found")

    if request.university is not None:
        template_model.university = request.university
    if request.degree_type is not None:
        template_model.degree_type = request.degree_type.lower()
    if request.discipline is not None:
        template_model.discipline = request.discipline
    if request.version is not None:
        template_model.version = request.version
    if request.rules is not None:
        template_model.rules_json = json.dumps(request.rules)
    if request.file_path is not None:
        template_model.file_path = request.file_path
    if request.is_active is not None:
        template_model.is_active = request.is_active

    db.commit()
    db.refresh(template_model)

    rules = _parse_rules_from_json(template_model.rules_json)

    return TemplateResponse(
        id=str(template_model.id),
        university=template_model.university,
        degree_type=template_model.degree_type,
        discipline=template_model.discipline,
        version=template_model.version,
        is_active=template_model.is_active,
        rules=rules,
        file_path=template_model.file_path,
        created_at=template_model.created_at.isoformat() if template_model.created_at else None,
        updated_at=template_model.updated_at.isoformat() if template_model.updated_at else None,
    )


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deactivate a template (soft delete)."""
    try:
        uid = UUID(template_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid template ID format")

    template_model = db.query(TemplateModel).filter(
        TemplateModel.id == uid
    ).first()

    if template_model is None:
        raise HTTPException(status_code=404, detail="Template not found")

    template_model.is_active = False
    db.commit()