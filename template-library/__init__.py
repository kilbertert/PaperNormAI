"""
Template library package.

Contains university paper format templates as JSON/YAML files.
Templates define validation rules for different universities and degree types.
"""

from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent
UNIVERSITIES_DIR = TEMPLATE_DIR / "universities"

__all__ = ["TEMPLATE_DIR", "UNIVERSITIES_DIR"]