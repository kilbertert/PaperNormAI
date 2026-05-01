"""Core infrastructure module.

Provides configuration, database, dependency injection, authentication,
exception handling, and logging infrastructure.

Does NOT contain document parsing, rule judgment, or template matching logic.
"""

from app.core.config import settings

__all__ = ["settings"]