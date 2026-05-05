"""SQLAlchemy database models for PaperNormAI."""

from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, declarative_base

from app.core.database import Base


class UserModel(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    role = Column(String(50), default="student")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    documents = relationship("DocumentModel", back_populates="user")

    def __repr__(self):
        return f"<UserModel {self.email}>"


class DocumentModel(Base):
    """Document database model."""

    __tablename__ = "documents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    template_id = Column(PGUUID(as_uuid=True), ForeignKey("templates.id"), nullable=True, index=True)
    status = Column(String(50), default="pending")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserModel", back_populates="documents")
    template = relationship("TemplateModel", back_populates="documents")
    validation_jobs = relationship("ValidationJobModel", back_populates="document")

    def __repr__(self):
        return f"<DocumentModel {self.original_filename}>"


class TemplateModel(Base):
    """Template database model."""

    __tablename__ = "templates"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    university = Column(String(200), nullable=False, index=True)
    degree_type = Column(String(50), nullable=False)
    discipline = Column(String(200), nullable=False)
    version = Column(String(20), default="1.0")
    rules_json = Column(Text, nullable=False, default="[]")
    file_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("DocumentModel", back_populates="template")
    validation_jobs = relationship("ValidationJobModel", back_populates="template")

    def __repr__(self):
        return f"<TemplateModel {self.university} {self.degree_type}>"


class ValidationJobModel(Base):
    """Validation job database model."""

    __tablename__ = "validation_jobs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(PGUUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    template_id = Column(PGUUID(as_uuid=True), ForeignKey("templates.id"), nullable=False, index=True)
    status = Column(String(50), default="pending")
    priority = Column(Integer, default=0)
    trigger_type = Column(String(50), default="manual")
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("DocumentModel", back_populates="validation_jobs")
    template = relationship("TemplateModel", back_populates="validation_jobs")
    results = relationship("ValidationResultModel", back_populates="job")

    def __repr__(self):
        return f"<ValidationJobModel {self.id} status={self.status}>"


class ValidationResultModel(Base):
    """Validation result database model."""

    __tablename__ = "validation_results"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(PGUUID(as_uuid=True), ForeignKey("validation_jobs.id"), nullable=False, index=True)
    rule_id = Column(String(100), nullable=False)
    rule_name = Column(String(200), nullable=False)
    element_path = Column(String(200), nullable=False)
    severity = Column(String(20), nullable=False)
    expected_value = Column(Text, nullable=True)
    actual_value = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    auto_fixable = Column(Boolean, default=False)
    ai_enhanced = Column(Boolean, default=False)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("ValidationJobModel", back_populates="results")

    def __repr__(self):
        return f"<ValidationResultModel {self.rule_id} {self.severity}>"


class CorrectionPlanModel(Base):
    """Correction plan database model."""

    __tablename__ = "correction_plans"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = Column(PGUUID(as_uuid=True), ForeignKey("validation_results.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    target_path = Column(String(200), nullable=False)
    original_value = Column(Text, nullable=True)
    planned_value = Column(Text, nullable=True)
    status = Column(String(50), default="planned")
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CorrectionPlanModel {self.action_type} status={self.status}>"


class CorrectionJobModel(Base):
    """Correction job database model."""

    __tablename__ = "correction_jobs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(PGUUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    plan_ids_json = Column(Text, nullable=False, default="[]")
    status = Column(String(50), default="pending")
    output_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CorrectionJobModel {self.id} status={self.status}>"


class SpecSessionModel(Base):
    """Spec session database model — persists AI-extracted rules."""

    __tablename__ = "spec_sessions"

    session_id = Column(String(32), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)  # UUID as string for SQLite compat
    rules_json = Column(Text, nullable=False, default="[]")
    summary_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SpecSessionModel {self.session_id}>"


class AuditLogModel(Base):
    """Audit log database model."""

    __tablename__ = "audit_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(PGUUID(as_uuid=True), nullable=True)
    detail_json = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLogModel {self.action} {self.entity_type}>"