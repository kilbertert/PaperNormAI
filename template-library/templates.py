"""
Template management utilities.

Provides functions for loading, validating, and managing
university paper format templates.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.domain.entities.template import Template, DegreeType
from app.domain.entities.validation_rule import ValidationRule, RuleLevel, Severity


def load_template_from_file(file_path: Path) -> Template:
    """Load a template from a JSON file.

    Args:
        file_path: Path to the template JSON file

    Returns:
        Template domain entity
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rules = []
    for rule_data in data.get('rules', []):
        rule = ValidationRule(
            id=rule_data['id'],
            name=rule_data['name'],
            level=RuleLevel(rule_data['level']),
            description=rule_data['description'],
            severity=Severity(rule_data.get('severity', 'error')),
            auto_fixable=rule_data.get('auto_fixable', False),
            params=rule_data.get('params', {}),
        )
        rules.append(rule)

    return Template(
        university=data['university'],
        degree_type=DegreeType(data['degree_type']),
        discipline=data['discipline'],
        version=data.get('version', '1.0'),
        rules=rules,
        is_active=data.get('is_active', True),
        file_path=data.get('file_path'),
    )


def load_templates_from_directory(directory: Path) -> List[Template]:
    """Load all templates from a directory.

    Args:
        directory: Directory containing template JSON files

    Returns:
        List of Template entities
    """
    templates = []
    for file_path in directory.glob("*.json"):
        try:
            template = load_template_from_file(file_path)
            templates.append(template)
        except Exception as e:
            print(f"Failed to load template from {file_path}: {e}")
    return templates


def validate_template_data(data: Dict[str, Any]) -> List[str]:
    """Validate template data against schema.

    Args:
        data: Template data dictionary

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    required_fields = ['university', 'degree_type', 'discipline', 'rules']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if 'degree_type' in data and data['degree_type'] not in ['bachelor', 'master', 'doctor']:
        errors.append(f"Invalid degree_type: {data['degree_type']}")

    if 'rules' in data:
        if not isinstance(data['rules'], list):
            errors.append("'rules' must be an array")
        elif len(data['rules']) == 0:
            errors.append("'rules' cannot be empty")

    return errors