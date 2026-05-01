"""Unit tests for database repositories."""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import MagicMock, patch
from pathlib import Path

from app.infrastructure.persistence.document_repository import DocumentRepository
from app.infrastructure.persistence.template_repository import TemplateRepository
from app.infrastructure.persistence.mappers import DocumentMapper, TemplateMapper
from app.domain.entities.document import Document, DocumentStatus
from app.domain.entities.template import Template, DegreeType
from app.infrastructure.persistence.models import DocumentModel, TemplateModel


class TestDocumentRepository:
    """Tests for DocumentRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = MagicMock()
        db.query.return_value = db
        db.filter.return_value = db
        db.order_by.return_value = db
        db.limit.return_value = db
        db.offset.return_value = db
        db.first.return_value = None
        db.all.return_value = []
        db.add = MagicMock()
        db.commit = MagicMock()
        db.delete = MagicMock()
        db.count.return_value = 0
        return db

    @pytest.fixture
    def repository(self, mock_db):
        """Create DocumentRepository with mock db."""
        return DocumentRepository(mock_db)

    @pytest.fixture
    def sample_document(self):
        """Create a sample Document entity."""
        return Document(
            user_id=uuid4(),
            original_filename="论文.docx",
            file_path=Path("/uploads/test.docx"),
            file_hash="abc123def456",
        )

    def test_save_document(self, repository, mock_db, sample_document):
        """Test saving a document."""
        repository.save(sample_document)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_find_by_id_returns_none_when_not_found(self, repository, mock_db):
        """Test find_by_id returns None when document doesn't exist."""
        mock_db.first.return_value = None
        result = repository.find_by_id(uuid4())
        assert result is None

    def test_find_by_id_returns_document(self, repository, mock_db):
        """Test find_by_id returns document when found."""
        model = MagicMock(spec=DocumentModel)
        model.id = uuid4()
        model.user_id = uuid4()
        model.original_filename = "test.docx"
        model.file_path = "/uploads/test.docx"
        model.file_hash = "hash123"
        model.template_id = None
        model.status = "pending"
        model.uploaded_at = datetime.utcnow()
        model.updated_at = datetime.utcnow()

        mock_db.first.return_value = model

        result = repository.find_by_id(model.id)
        assert result is not None
        assert result.original_filename == "test.docx"

    def test_find_by_user_id(self, repository, mock_db):
        """Test finding documents by user ID."""
        mock_db.all.return_value = []
        result = repository.find_by_user_id(uuid4())
        assert isinstance(result, list)

    def test_find_by_hash(self, repository, mock_db):
        """Test finding document by hash."""
        mock_db.first.return_value = None
        result = repository.find_by_hash("nonexistent_hash")
        assert result is None

    def test_delete_document(self, repository, mock_db):
        """Test deleting a document."""
        mock_model = MagicMock()
        mock_db.first.return_value = mock_model
        repository.delete(uuid4())
        mock_db.delete.assert_called_once_with(mock_model)
        mock_db.commit.assert_called()

    def test_count_by_user(self, repository, mock_db):
        """Test counting documents by user."""
        mock_db.count.return_value = 5
        count = repository.count_by_user(uuid4())
        assert count == 5


class TestTemplateRepository:
    """Tests for TemplateRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = MagicMock()
        db.query.return_value = db
        db.filter.return_value = db
        db.order_by.return_value = db
        db.all.return_value = []
        db.first.return_value = None
        db.add = MagicMock()
        db.commit = MagicMock()
        db.count.return_value = 0
        return db

    @pytest.fixture
    def repository(self, mock_db):
        """Create TemplateRepository with mock db."""
        return TemplateRepository(mock_db)

    @pytest.fixture
    def sample_template(self):
        """Create a sample Template entity."""
        return Template(
            university="清华大学",
            degree_type=DegreeType.MASTER,
            discipline="计算机科学",
            version="1.0",
            rules=[],
        )

    def test_save_template(self, repository, mock_db, sample_template):
        """Test saving a template."""
        repository.save(sample_template)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_find_by_id_returns_none(self, repository, mock_db):
        """Test find_by_id returns None when not found."""
        mock_db.first.return_value = None
        result = repository.find_by_id(uuid4())
        assert result is None

    def test_find_active_templates(self, repository, mock_db):
        """Test finding active templates."""
        mock_db.all.return_value = []
        result = repository.find_active()
        assert isinstance(result, list)

    def test_count_active(self, repository, mock_db):
        """Test counting active templates."""
        mock_db.count.return_value = 10
        count = repository.count_active()
        assert count == 10


class TestDocumentMapper:
    """Tests for DocumentMapper."""

    def test_to_domain_creates_entity(self):
        """Test mapper creates domain entity from model."""
        model = MagicMock(spec=DocumentModel)
        model.id = uuid4()
        model.user_id = uuid4()
        model.original_filename = "test.docx"
        model.file_path = "/uploads/test.docx"
        model.file_hash = "hash123"
        model.template_id = None
        model.status = "pending"
        model.uploaded_at = datetime.utcnow()
        model.updated_at = datetime.utcnow()

        result = DocumentMapper.to_domain(model)

        assert result.original_filename == "test.docx"
        assert result.status == DocumentStatus.PENDING

    def test_to_model_creates_database_model(self):
        """Test mapper creates database model from entity."""
        entity = Document(
            user_id=uuid4(),
            original_filename="论文.docx",
            file_path=Path("/uploads/test.docx"),
            file_hash="hash123",
        )

        result = DocumentMapper.to_model(entity)

        assert result.original_filename == "论文.docx"
        assert result.file_hash == "hash123"


class TestTemplateMapper:
    """Tests for TemplateMapper."""

    def test_to_domain_creates_entity(self):
        """Test mapper creates domain entity from model."""
        model = MagicMock(spec=TemplateModel)
        model.id = uuid4()
        model.university = "清华大学"
        model.degree_type = "master"
        model.discipline = "计算机科学"
        model.version = "1.0"
        model.rules_json = "[]"
        model.file_path = None
        model.is_active = True
        model.created_at = datetime.utcnow()
        model.updated_at = datetime.utcnow()

        result = TemplateMapper.to_domain(model)

        assert result.university == "清华大学"
        assert result.degree_type == DegreeType.MASTER

    def test_to_model_creates_database_model(self):
        """Test mapper creates database model from entity."""
        entity = Template(
            university="北京大学",
            degree_type=DegreeType.BACHELOR,
            discipline="数学",
            version="1.0",
            rules=[],
        )

        result = TemplateMapper.to_model(entity)

        assert result.university == "北京大学"
        assert result.degree_type == "bachelor"