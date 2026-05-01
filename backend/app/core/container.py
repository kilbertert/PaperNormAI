"""Dependency injection container."""

from typing import Callable
from app.core.database import SessionLocal
from app.infrastructure.persistence.document_repository import DocumentRepository
from app.infrastructure.persistence.template_repository import TemplateRepository
from app.infrastructure.persistence.user_repository import UserRepository
from app.domain.services.rule_engine import RuleEngine
from app.domain.services.template_service import TemplateService
from app.domain.services.ai_enhancement_service import AIEnhancementService
from app.infrastructure.docx.document_parser import DocumentParser
from app.infrastructure.storage.file_storage import FileStorage


class Container:
    """Simple dependency injection container."""

    _instance = None

    def __init__(self):
        self._services = {}

    @classmethod
    def get_instance(cls) -> "Container":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, key: str, factory: Callable):
        self._services[key] = factory

    def resolve(self, key: str):
        return self._services[key]()

    def reset(self):
        self._services.clear()
        self._instance = None


container = Container.get_instance()


def init_container():
    """Initialize the dependency injection container."""
    container.register("db", lambda: SessionLocal())

    container.register(
        "document_repository",
        lambda: DocumentRepository(SessionLocal()),
    )
    container.register(
        "template_repository",
        lambda: TemplateRepository(SessionLocal()),
    )
    container.register(
        "user_repository",
        lambda: UserRepository(SessionLocal()),
    )

    container.register(
        "file_storage",
        lambda: FileStorage(),
    )

    container.register(
        "document_parser",
        lambda: DocumentParser(),
    )

    container.register(
        "ai_enhancement_service",
        lambda: AIEnhancementService(),
    )

    container.register(
        "template_service",
        lambda: TemplateService(container.resolve("template_repository")),
    )

    container.register(
        "rule_engine",
        lambda: RuleEngine(
            template_service=container.resolve("template_service"),
            ai_enhancement=container.resolve("ai_enhancement_service"),
        ),
    )